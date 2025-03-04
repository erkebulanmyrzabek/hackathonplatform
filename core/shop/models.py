from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from user.models import User
import os
from django.utils import timezone

product_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'product_img'),  
    base_url='/static/img/product_img'
)

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    crystal_price = models.PositiveIntegerField(default=0, verbose_name="Цена в кристаллах")
    image = models.ImageField(upload_to='product_images/', storage=product_img_url, verbose_name="Изображение")
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="Категория")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    discount_percent = models.PositiveIntegerField(default=0, verbose_name="Процент скидки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name
    
    @property
    def discounted_price(self):
        if self.discount_percent > 0:
            return self.price - (self.price * (self.discount_percent / 100))
        return self.price
    
    @property
    def discounted_crystal_price(self):
        if self.discount_percent > 0:
            return self.crystal_price - (self.crystal_price * (self.discount_percent / 100))
        return self.crystal_price
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

class ProductVariant(models.Model):
    VARIANT_TYPE_CHOICES = [
        ('size', 'Размер'),
        ('color', 'Цвет'),
        ('material', 'Материал'),
        ('other', 'Другое'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="Товар")
    variant_type = models.CharField(max_length=20, choices=VARIANT_TYPE_CHOICES, default='size', verbose_name="Тип варианта")
    name = models.CharField(max_length=100, verbose_name="Название варианта")
    value = models.CharField(max_length=100, verbose_name="Значение")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Количество в наличии")
    
    def __str__(self):
        return f"{self.product.name} - {self.variant_type}: {self.value}"
    
    class Meta:
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товаров"
        unique_together = ['product', 'variant_type', 'value']

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    
    def __str__(self):
        return f"Корзина пользователя {self.user.username} ({self.id})"
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_crystal_price(self):
        return sum(item.total_crystal_price for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Вариант")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    
    def __str__(self):
        variant_info = f" ({self.variant.value})" if self.variant else ""
        return f"{self.product.name}{variant_info} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.product.discounted_price * self.quantity
    
    @property
    def total_crystal_price(self):
        return self.product.discounted_crystal_price * self.quantity
    
    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"
        unique_together = ['cart', 'product', 'variant']

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'Обрабатывается'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Банковская карта'),
        ('crystals', 'Кристаллы'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
    full_name = models.CharField(max_length=100, verbose_name="ФИО")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Адрес доставки")
    city = models.CharField(max_length=100, verbose_name="Город")
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    country = models.CharField(max_length=100, default="Казахстан", verbose_name="Страна")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='cash', verbose_name="Способ оплаты")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость")
    total_crystal_price = models.PositiveIntegerField(default=0, verbose_name="Стоимость в кристаллах")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Стоимость доставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Номер отслеживания")
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания")
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.user.username}"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    product_name = models.CharField(max_length=100, verbose_name="Название товара")
    product_variant = models.CharField(max_length=100, blank=True, null=True, verbose_name="Вариант товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    crystal_price = models.PositiveIntegerField(default=0, verbose_name="Цена в кристаллах")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    
    def __str__(self):
        variant_info = f" ({self.product_variant})" if self.product_variant else ""
        return f"{self.product_name}{variant_info} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.price * self.quantity
    
    @property
    def total_crystal_price(self):
        return self.crystal_price * self.quantity
    
    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"
    
    