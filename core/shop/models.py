from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

product_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'product_img'),  
    base_url='/static/img/product_img'
)
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', storage=product_img_url)

    def __str__(self):
        return self.name
    
    