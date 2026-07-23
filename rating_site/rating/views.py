from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction

import uuid
import requests
from pathlib import Path

from rating_site.rating.decorators import admin_required
from rating_site.rating.mysql_models import (
    Achievements,
    CategoryData,
)
from rating_site.backend.maps import CATEGORY_MAP

import json
import math

def home(request):
    return render(request, 'home.html')

@login_required
def my_achievements(request):
    return render(request, 'my_achievements.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def add_achievement(request):
    if request.method == 'POST':
        description = request.POST.get('description', '')
        categories = request.POST.getlist('categories')
        user_tg_id = request.POST.get('user_tg_id')

        file = request.FILES.get('file')

        upload_dir = Path(__file__).parent.parent.parent / 'data'
        upload_dir.mkdir(parents=True, exist_ok=True)

        try:
            ext = Path(file.name).suffix.lower()
            if not ext:
                ext = '.bin'

            filename = f'{uuid.uuid4()}{ext}'
            relative_path = f'data/{filename}'
            full_path = Path(__file__).parent.parent.parent / relative_path

            with open(full_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            print(f"Файл сохранен: {file.name}")

        except Exception as e:
            full_path.unlink(missing_ok=True)

            print(f"Ошибка при сохранении файла {file.name}: {e}")
            return redirect('add_achievement')

        payload = {
            'login': request.user.login,
            'user_tg_id': int(user_tg_id),
            'categories': categories,
            'description': description,
            'file_info': {
                'file_path': relative_path,
                'file_type': ext.replace('.', '')
            },
        }

        try:
            response = requests.post(
                f'{settings.INTERNAL_API_BASE_URL}/post_api_add_web_achievement',
                json=payload,
                timeout=10
            )
            print("PAYLOAD:", payload)
            print("STATUS:", response.status_code)
            print("FASTAPI ANSWER:", response.text)

            response.raise_for_status()

        except requests.RequestException as e:
            messages.error(request, f'{e}')
            return redirect('add_achievement')
        
        result = response.json()

        messages.success(request, f'Ваше достижение добавлено!')
        
        return redirect('my_achievements')

    return render(request, 'add_achievement.html')

@login_required
@admin_required
def admin_interface(request):
    pending_achievements_count = Achievements.objects.using('mysql_db').filter(status='viewing').count()

    category_rows = CategoryData.objects.using('mysql_db').filter(title__in = CATEGORY_MAP.values())

    weights_by_name = {
        category.title: category.weight
        for category in category_rows
    }

    weights = {
        "academic": weights_by_name.get(
            CATEGORY_MAP["academic"],
            1,
        ),
        "science": weights_by_name.get(
            CATEGORY_MAP["science"],
            1,
        ),
        "social": weights_by_name.get(
            CATEGORY_MAP["social"],
            1,
        ),
        "cultural": weights_by_name.get(
            CATEGORY_MAP["cultural"],
            1,
        ),
    }

    context = {
        'title': 'Панель администратора',
        'current_user': request.user,
        'pending_achievements_count': pending_achievements_count,
        'weights': weights,
    }

    return render(request, 'admin_interface.html', context)

@require_POST
@login_required
@admin_required
def save_category_weights(request):
    try:
        payload = json.loads(request.body)

        weights = {
            key: float(payload[key])
            for key in CATEGORY_MAP
        }
    except json.JSONDecodeError:
        return JsonResponse(
        {
                'success': False,
                'message': 'Получен некорректный JSON'
             },
            status=400
        )
    except (KeyError, TypeError, ValueError):
        return JsonResponse(
            {
                'success': False,
                'message': 'Все веса должны быть числами'
            },
            status=400
        )

    invalid_weight = any(
        not math.isfinite(weight) or weight < 0
        for weight in weights.values()
    )

    if invalid_weight:
        return JsonResponse(
            {
                'success': False,
                'message': 'Вес должен быть числом не меньше нуля'
            },
            status=400
        )

    try:
        with transaction.atomic(using='mysql_db'):
            for alias, title in CATEGORY_MAP.items():
                updated_rows = (
                    CategoryData.objects
                    .using('mysql_db')
                    .filter(title=title)
                    .update(weight=weights[alias])
                )

                if updated_rows == 0:
                    raise ValueError(
                        f'Категория {title} не найдена'
                    )

    except ValueError as error:
        return JsonResponse(
            {
                "success": False,
                "message": str(error),
            },
            status=404,
        )

    except Exception:
        return JsonResponse(
            {
                "success": False,
                "message": "Ошибка при сохранении весов",
            },
            status=500,
        )

    return JsonResponse(
        {
            "success": True,
            "message": "Веса категорий сохранены",
            "weights": weights,
        }
    )

