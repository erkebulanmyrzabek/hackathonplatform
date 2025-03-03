from django.urls import path
from .views import *

urlpatterns = [
    path("<int:pk>/", detailed_hackathon_view, name="hackathon"),
    path("view", hackathons_view, name="hackathons"),
]