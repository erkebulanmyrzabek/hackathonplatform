from django.urls import path
from . import views

app_name = 'hackathon'

urlpatterns = [
    # Главная страница хакатонов (список всех хакатонов)
    path('', views.hackathon_list, name='index'),
    
    # Детальная страница хакатона
    path('<int:pk>/', views.hackathon_detail, name='detail'),
    
    # Список хакатонов (альтернативный URL)
    path('list/', views.hackathon_list, name='list'),
]