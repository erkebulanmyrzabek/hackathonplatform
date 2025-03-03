from django.db import models
from django.core.files.storage import FileSystemStorage
from community.models import Team
from django.conf import settings
import os

post_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'post_img'),  
    base_url='/static/img/post_img'
)

webinar_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'webinar_img'),  
    base_url='/static/img/webinar_img'
)

casecup_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'casecup_img'),  
    base_url='/static/img/casecup_img'
)

class Post(models.Model):
    header = models.CharField(max_length=100)
    body = models.TextField()
    image = models.ImageField(storage=post_img_url, upload_to='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cat = models.ForeignKey('feed.Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.header
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Webinar(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='webinar_images/')
    cat = models.ForeignKey('feed.Category', on_delete=models.CASCADE)

class Casecup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='casecup_images/')
    cat = models.ForeignKey('feed.Category', on_delete=models.CASCADE)

class Event(models.Model):
    EVENT_TYPES = [
        ('hackathon', 'Хакатон'),
        ('casecamp', 'Кейс-чемпионат'),
        ('webinar', 'Вебинар'),
    ]

    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateTimeField()
    participants_count = models.IntegerField(default=0)
    format = models.CharField(max_length=100)  # онлайн/офлайн
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.title
