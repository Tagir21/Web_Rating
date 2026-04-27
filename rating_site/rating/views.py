from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
import os

import uuid

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
        # Получаем данные из формы
        description = request.POST.get('description', '')
        categories = request.POST.getlist('categories')
        
        # Получаем файлы
        files = request.FILES.getlist('files')


        
        saved_files = []
        for file in files:
            try:
                ext = file.name.split('.')[-1] if '.' in file.name else 'bin'
                filename = f'{uuid.uuid4()}.{ext}'
                file_path = os.path.join('../data', filename)

                # Сохраняем файл
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                saved_files.append(file.name)
                print(f"Файл сохранен: {file.name}")
                
            except Exception as e:
                print(f"Ошибка при сохранении файла {file.name}: {e}")
        
        # Выводим информацию для отладки
        print(f"Описание: {description}")
        print(f"Категории: {categories}")
        print(f"Сохраненные файлы: {saved_files}")
        
        # Добавляем сообщение об успехе (опционально)
        from django.contrib import messages
        if saved_files:
            messages.success(request, f'Достижение добавлено! Сохранено файлов: {len(saved_files)}')
        else:
            messages.warning(request, 'Достижение добавлено, но файлы не были сохранены')
        
        return redirect('my_achievements')

    return render(request, 'add_achievement.html')