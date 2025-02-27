from django.db import models
from django.core.files.storage import FileSystemStorage
from community.models import Team
from django.conf import settings
import os

image_storage = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img'),  
    base_url='/static/img/'
)

# Create your models here.
class Post(models.Model):
    header = models.CharField(max_length=100)
    body = models.TextField()
    image = models.ImageField(storage=image_storage, upload_to='', blank=True, null=True)
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
