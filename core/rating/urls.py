from django.urls import path
from .views import rating_view

urlpatterns = [
    path('', rating_view, name='rating'),
] 