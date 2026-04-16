from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os

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
def add_ach(request):
    if request.method == 'POST':
        # Получаем данные из формы
        description = request.POST.get('description', '')
        categories = request.POST.getlist('categories')
        
        # Получаем файлы
        files = request.FILES.getlist('files')

        upload_dir = os.path.join(settings.BASE_DIR, 'static', 'download')
        
        # Создаем папку если её нет
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            print(f"Создана папка: {upload_dir}")
        
        print(f"Путь для сохранения: {upload_dir}")
        print(f"Количество файлов: {len(files)}")
        
        saved_files = []
        for file in files:
            try:
                # Сохраняем каждый файл
                file_path = os.path.join(upload_dir, file.name)
                
                # Если файл с таким именем уже есть, добавляем номер
                counter = 1
                original_name = file.name
                while os.path.exists(file_path):
                    name, ext = os.path.splitext(original_name)
                    file.name = f"{name}_{counter}{ext}"
                    file_path = os.path.join(upload_dir, file.name)
                    counter += 1
                
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
    
    # players = Player.objects.all().order_by('-rating')
    return render(request, 'add_achievement.html')