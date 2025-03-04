from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'hackathon'

router = DefaultRouter()
router.register(r'hackathons', views.HackathonViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'prize-places', views.PrizePlacesViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Web pages
    path('', views.hackathon_list, name='index'),
    path('<int:pk>/', views.hackathon_detail, name='detail'),
    path('list/', views.hackathon_list, name='list'),
]