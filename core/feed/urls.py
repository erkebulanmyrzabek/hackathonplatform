from django.urls import path

from feed.views import *

urlpatterns = [
    path("", feed_view, name="feed"),
]
