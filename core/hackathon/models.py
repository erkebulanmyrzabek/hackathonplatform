from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

image_storage = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img'),  
    base_url='/static/img/'
)

# Create your models here.
class Hackathon(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(storage=image_storage, upload_to='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name