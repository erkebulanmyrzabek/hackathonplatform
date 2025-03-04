from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Sum, F, Q
from .models import (
    Product, ProductCategory, ProductVariant,
    Cart, CartItem, Order, OrderItem
)
from user.models import User

def shop_view(request):
    """Основная страница магазина со списком товаров"""
    
    # Получаем хэш из параметров запроса
    hash_code = request.GET.get('hash', '')
    
    # Если хэш передан, пытаемся получить пользователя
    if hash_code:
        try:
            user = User.objects.get(hash_code=hash_code)
            # Получаем корзину пользователя или создаем новую
            cart, created = Cart.objects.get_or_create(user=user, is_active=True)
        except User.DoesNotExist:
            user = None
            cart = None
    else:
        user = None
        cart = None
    
    # Получаем все категории
    categories = ProductCategory.objects.all()
    
    # Получаем все товары или фильтруем по категории
    category_id = request.GET.get('category')
    
    if category_id:
        products = Product.objects.filter(category_id=category_id, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)
    
    context = {
        'user': user,
        'products': products,
        'categories': categories,
        'cart': cart,
        'current_category': category_id
    }
    
    return render(request, 'shop/shop.html', context)

def product_detail(request):
    """API для получения деталей товара"""
    
    product_id = request.GET.get('product_id')
    hash_code = request.GET.get('hash', '')
    
    if not product_id:
        return JsonResponse({'error': 'ID товара не указан'}, status=400)
    
    # Получаем товар с вариантами
    try:
        product = Product.objects.get(id=product_id, is_available=True)
        variants = product.variants.all().order_by('variant_type', 'value')
        
        # Группируем варианты по типу
        variant_types = {}
        for variant in variants:
            if variant.variant_type not in variant_types:
                variant_types[variant.variant_type] = []
            
            variant_types[variant.variant_type].append({
                'id': variant.id,
                'name': variant.name,
                'value': variant.value,
                'in_stock': variant.in_stock
            })
        
        # Формируем данные о товаре
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'crystal_price': product.crystal_price,
            'discount_percent': product.discount_percent,
            'discounted_price': float(product.discounted_price),
            'discounted_crystal_price': product.discounted_crystal_price,
            'image_url': product.image.url,
            'category': product.category.name if product.category else None,
            'variants': variant_types
        }
        
        return JsonResponse({'product': product_data})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Товар не найден'}, status=404)

@require_POST
def add_to_cart(request):
    """Добавить товар в корзину"""
    
    hash_code = request.POST.get('hash', '')
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    
    if not product_id:
        return JsonResponse({'error': 'ID товара не указан'}, status=400)
    
    # Получаем пользователя по хэш-коду
    try:
        user = User.objects.get(hash_code=hash_code)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    
    # Получаем товар
    try:
        product = Product.objects.get(id=product_id, is_available=True)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Товар не найден'}, status=404)
    
    # Получаем вариант товара, если указан
    variant = None
    if variant_id:
        try:
            variant = ProductVariant.objects.get(id=variant_id, product=product)
            if not variant.in_stock or variant.stock_quantity < quantity:
                return JsonResponse({'error': 'Товара нет в наличии'}, status=400)
        except ProductVariant.DoesNotExist:
            return JsonResponse({'error': 'Вариант товара не найден'}, status=404)
    
    # Получаем корзину пользователя или создаем новую
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)
    
    # Проверяем, есть ли уже такой товар в корзине
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product, variant=variant)
        cart_item.quantity += quantity
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            variant=variant,
            quantity=quantity
        )
    
    # Возвращаем обновленную информацию о корзине
    return JsonResponse({
        'success': True,
        'cart_total': cart.total_items,
        'cart_price': float(cart.total_price),
        'cart_crystal_price': cart.total_crystal_price
    })

@require_POST
def update_cart_item(request):
    """Обновить количество товара в корзине"""
    
    hash_code = request.POST.get('hash', '')
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    if not item_id:
        return JsonResponse({'error': 'ID товара в корзине не указан'}, status=400)
    
    # Получаем пользователя по хэш-коду
    try:
        user = User.objects.get(hash_code=hash_code)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    
    # Получаем товар в корзине
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=user, cart__is_active=True)
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Товар в корзине не найден'}, status=404)
    
    # Обновляем количество или удаляем товар
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    # Получаем обновленную корзину
    cart = cart_item.cart
    
    # Возвращаем обновленную информацию о корзине
    return JsonResponse({
        'success': True,
        'cart_total': cart.total_items,
        'cart_price': float(cart.total_price),
        'cart_crystal_price': cart.total_crystal_price
    })

@require_POST
def remove_from_cart(request):
    """Удалить товар из корзины"""
    
    hash_code = request.POST.get('hash', '')
    item_id = request.POST.get('item_id')
    
    if not item_id:
        return JsonResponse({'error': 'ID товара в корзине не указан'}, status=400)
    
    # Получаем пользователя по хэш-коду
    try:
        user = User.objects.get(hash_code=hash_code)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    
    # Получаем товар в корзине
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=user, cart__is_active=True)
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Товар в корзине не найден'}, status=404)
    
    # Получаем корзину перед удалением товара
    cart = cart_item.cart
    
    # Удаляем товар
    cart_item.delete()
    
    # Возвращаем обновленную информацию о корзине
    return JsonResponse({
        'success': True,
        'cart_total': cart.total_items,
        'cart_price': float(cart.total_price),
        'cart_crystal_price': cart.total_crystal_price
    })

def cart_view(request):
    """Страница корзины"""
    
    hash_code = request.GET.get('hash', '')
    
    # Если хэш передан, пытаемся получить пользователя
    if hash_code:
        try:
            user = User.objects.get(hash_code=hash_code)
            # Получаем корзину пользователя
            try:
                cart = Cart.objects.get(user=user, is_active=True)
                cart_items = cart.items.all().select_related('product', 'variant')
            except Cart.DoesNotExist:
                cart = None
                cart_items = []
        except User.DoesNotExist:
            return redirect('shop:shop')
    else:
        # Если пользователь не аутентифицирован, перенаправляем на страницу магазина
        return redirect('shop:shop')
    
    context = {
        'user': user,
        'cart': cart,
        'cart_items': cart_items
    }
    
    return render(request, 'shop/cart.html', context)

def checkout_view(request):
    """Страница оформления заказа"""
    
    hash_code = request.GET.get('hash', '')
    
    # Если хэш передан, пытаемся получить пользователя
    if hash_code:
        try:
            user = User.objects.get(hash_code=hash_code)
            # Получаем корзину пользователя
            try:
                cart = Cart.objects.get(user=user, is_active=True)
                cart_items = cart.items.all().select_related('product', 'variant')
                
                if not cart_items:
                    messages.error(request, 'Ваша корзина пуста')
                    return redirect(f'/shop/cart/?hash={hash_code}')
            
            except Cart.DoesNotExist:
                messages.error(request, 'Ваша корзина пуста')
                return redirect(f'/shop/?hash={hash_code}')
        except User.DoesNotExist:
            return redirect('shop:shop')
    else:
        # Если пользователь не аутентифицирован, перенаправляем на страницу магазина
        return redirect('shop:shop')
    
    context = {
        'user': user,
        'cart': cart,
        'cart_items': cart_items
    }
    
    return render(request, 'shop/checkout.html', context)

@require_POST
def place_order(request):
    """Оформление заказа"""
    
    hash_code = request.POST.get('hash', '')
    payment_type = request.POST.get('payment_type', 'cash')
    
    # Получаем пользователя по хэш-коду
    try:
        user = User.objects.get(hash_code=hash_code)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    
    # Получаем корзину пользователя
    try:
        cart = Cart.objects.get(user=user, is_active=True)
        cart_items = cart.items.all().select_related('product', 'variant')
        
        if not cart_items:
            return JsonResponse({'error': 'Ваша корзина пуста'}, status=400)
    
    except Cart.DoesNotExist:
        return JsonResponse({'error': 'Ваша корзина пуста'}, status=400)
    
    # Создаем заказ
    order = Order.objects.create(
        user=user,
        full_name=request.POST.get('full_name'),
        phone_number=request.POST.get('phone_number'),
        email=request.POST.get('email'),
        address=request.POST.get('address'),
        city=request.POST.get('city'),
        postal_code=request.POST.get('postal_code'),
        country=request.POST.get('country', 'Казахстан'),
        payment_type=payment_type,
        total_price=cart.total_price,
        total_crystal_price=cart.total_crystal_price,
        shipping_cost=0,  # Можно добавить логику расчета стоимости доставки
        notes=request.POST.get('notes', '')
    )
    
    # Добавляем товары из корзины в заказ
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_variant=item.variant.value if item.variant else None,
            price=item.product.discounted_price,
            crystal_price=item.product.discounted_crystal_price,
            quantity=item.quantity
        )
    
    # Если оплата кристаллами, списываем кристаллы с пользователя
    if payment_type == 'crystals':
        if user.crystals >= cart.total_crystal_price:
            user.crystals -= cart.total_crystal_price
            user.save()
        else:
            order.delete()
            return JsonResponse({'error': 'Недостаточно кристаллов'}, status=400)
    
    # Закрываем корзину
    cart.is_active = False
    cart.save()
    
    return JsonResponse({
        'success': True,
        'order_id': order.id,
        'message': 'Заказ успешно оформлен'
    })

def order_success(request):
    """Страница успешного оформления заказа"""
    
    hash_code = request.GET.get('hash', '')
    order_id = request.GET.get('order_id')
    
    # Получаем пользователя по хэш-коду
    try:
        user = User.objects.get(hash_code=hash_code)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    
    # Получаем заказ
    try:
        order = Order.objects.get(id=order_id, user=user)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Заказ не найден'}, status=404)
    
    context = {
        'user': user,
        'order': order
    }
    
    return render(request, 'shop/order_success.html', context)

def user_orders(request):
    """Список заказов пользователя"""
    
    hash_code = request.GET.get('hash', '')
    
    # Получаем пользователя по хэш-коду
    try:
        user = User.objects.get(hash_code=hash_code)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    
    # Получаем заказы пользователя
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'orders': orders
    }
    
    return render(request, 'shop/user_orders.html', context)

def order_detail(request, order_id):
    """Детали заказа"""
    
    hash_code = request.GET.get('hash', '')
    
    # Получаем пользователя по хэш-коду
    try:
        user = User.objects.get(hash_code=hash_code)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    
    # Получаем заказ
    try:
        order = Order.objects.get(id=order_id, user=user)
        order_items = order.items.all()
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Заказ не найден'}, status=404)
    
    context = {
        'user': user,
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'shop/order_detail.html', context)