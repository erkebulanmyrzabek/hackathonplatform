from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('webinar/<int:webinar_id>/', views.webinar_detail_view, name='webinar_detail'),
    path('webinar/<int:webinar_id>/register/', views.webinar_register_view, name='webinar_register'),
    path('casecup/<int:casecup_id>/', views.casecup_detail_view, name='casecup_detail'),
    path('casecup/<int:casecup_id>/register/', views.casecup_register_view, name='casecup_register'),
]
