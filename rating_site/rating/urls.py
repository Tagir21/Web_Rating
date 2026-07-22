from django.urls import path
from rating_site.rating import views

urlpatterns = [
    path('', views.home, name='home'),
    path('my_achievements/', views.my_achievements, name='my_achievements'),  # Исправлено: achievements
    path('profile/', views.profile, name='profile'),
    path('add_achievement/', views.add_achievement, name='add_achievement'),
    path('admin_interface/', views.admin_interface, name='admin_interface'),
    path('admin_interface/save_category_weights', views.save_category_weights, name='save_category_weights'),
]