from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rating/', views.rating_table, name='rating'),
    path('my_achievements/', views.my_achievements, name='my_achievements'),  # Исправлено: achievements
    path('profile/', views.profile, name='profile'),
    path('add_achievement/', views.add_ach, name='add_achievement'),
]