from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import os

import uuid
import requests
from pathlib import Path

from .decorators import admin_required

def home(request):
    return render(request, 'home.html')

@login_required
def rating_table(request):
    return render(request, 'rating_table.html')

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

        upload_dir = Path(settings.MEDIA_ROOT) / 'achievements'
        upload_dir.mkdir(parents=True, exist_ok=True)

        try:
            ext = Path(file.name).suffix.lower()
            if not ext:
                ext = '.bin'

            filename = f'{uuid.uuid4()}{ext}'
            relative_path = f'achievements/{filename}'
            full_path = Path(settings.MEDIA_ROOT) / relative_path

            with open(full_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            print(f"Файл сохранен: {file.name}")

        except Exception as e:
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
                'http://127.0.0.1:8000/post_api_add_web_achievement',
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
    context = {
        'title': 'Панель администратора',
        'current_user': request.user
    }
    return render(request, 'admin_interface.html', context)