from django.db import models
import uuid
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

user_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'user_img'),  
    base_url='/static/img/user_img'
)

class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)  
    name = models.CharField(max_length=100)
    coin = models.IntegerField(default=0)
    hash_code = models.CharField(max_length=16, unique=True, default="temp_value", null=True, editable=False)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        
        if not self.hash_code:
            self.hash_code = uuid.uuid4().hex[:16]  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
