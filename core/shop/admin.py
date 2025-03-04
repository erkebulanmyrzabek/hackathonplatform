from django.contrib import admin
from .models import (
    Product, ProductCategory, ProductVariant,
    Cart, CartItem, Order, OrderItem
)

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'crystal_price', 'category', 'is_available', 'discount_percent', 'created_at')
    list_filter = ('is_available', 'category', 'discount_percent')
    search_fields = ('name', 'description')
    inlines = [ProductVariantInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price', 'crystal_price', 'image', 'category')
        }),
        ('Настройки', {
            'fields': ('is_available', 'discount_percent')
        }),
    )

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'product_variant', 'price', 'crystal_price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'status', 'payment_type', 'total_price', 'created_at')
    list_filter = ('status', 'payment_type', 'created_at')
    search_fields = ('full_name', 'phone_number', 'email', 'address')
    readonly_fields = ('total_price', 'total_crystal_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user', 'status', 'payment_type', 'total_price', 'total_crystal_price', 'shipping_cost')
        }),
        ('Информация о получателе', {
            'fields': ('full_name', 'phone_number', 'email')
        }),
        ('Адрес доставки', {
            'fields': ('country', 'city', 'address', 'postal_code')
        }),
        ('Дополнительно', {
            'fields': ('tracking_number', 'notes', 'created_at', 'updated_at')
        }),
    )

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    inlines = [CartItemInline]
