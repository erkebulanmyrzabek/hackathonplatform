from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from user.models import User

product_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'product_img'),  
    base_url='/static/img/product_img'
)

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('physical', 'Физический товар'),
        ('digital', 'Цифровой товар'),
        ('premium', 'Премиум-статус')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField(help_text="Цена в кристаллах")
    image = models.ImageField(upload_to='product_images/', storage=product_img_url)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='physical')
    stock = models.PositiveIntegerField(default=0, help_text="0 означает неограниченное количество")
    is_available = models.BooleanField(default=True)
    premium_duration_days = models.PositiveIntegerField(default=30, help_text="Длительность премиум-статуса в днях (только для премиум-товаров)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def is_in_stock(self):
        return self.stock > 0 or self.stock == 0 and self.product_type != 'physical'
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
        ('refunded', 'Возвращена')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.TextField(null=True, blank=True, help_text="Только для физических товаров")
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Расчет общей стоимости при создании
        if not self.pk:
            self.total_price = self.product.price * self.quantity
        
        # Обработка покупки премиум-статуса
        if self.status == 'completed' and self.product.product_type == 'premium':
            self.user.is_premium = True
            self.user.save()
            
        # Обновление склада
        if self.status == 'completed' and self.product.stock > 0:
            self.product.stock -= self.quantity
            self.product.save()
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.name} - {self.product.name} ({self.status})"
    
    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-created_at']

class DigitalAsset(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='digital_assets/', null=True, blank=True)
    price = models.PositiveIntegerField(help_text="Цена в кристаллах")
    asset_type = models.CharField(max_length=50, help_text="Тип цифрового актива (аватар, фон, значок и т.д.)")
    users = models.ManyToManyField(User, related_name='digital_assets', blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Цифровой актив'
        verbose_name_plural = 'Цифровые активы'
    
    