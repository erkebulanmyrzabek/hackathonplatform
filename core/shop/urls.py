from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Основные страницы
    path('', views.shop_view, name='shop'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('orders/', views.user_orders, name='orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # API для работы с корзиной и товарами
    path('api/product-detail/', views.product_detail, name='product_detail'),
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('api/update-cart-item/', views.update_cart_item, name='update_cart_item'),
    path('api/remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('api/place-order/', views.place_order, name='place_order'),
] 