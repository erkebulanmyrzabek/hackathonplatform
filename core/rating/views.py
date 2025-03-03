from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from user.models import User
from .models import Rating

def rating_view(request):
    # Получаем хэш из параметров запроса
    hash_code = request.GET.get("hash")
    
    # Если хэш передан, получаем пользователя, иначе используем None
    user = get_object_or_404(User, hash_code=hash_code) if hash_code else None

    # Получаем параметры фильтрации
    search_query = request.GET.get('search', '')
    period = request.GET.get('period', 'all')
    activity = request.GET.get('activity', 'all')

    # Базовый QuerySet
    ratings = Rating.objects.all()

    # Применяем поиск по имени пользователя
    if search_query:
        ratings = ratings.filter(
            Q(user__username__icontains=search_query)
        )

    # Фильтрация по периоду
    now = timezone.now()
    if period == 'month':
        month_ago = now - timedelta(days=30)
        ratings = ratings.filter(last_updated__gte=month_ago)
    elif period == 'year':
        year_ago = now - timedelta(days=365)
        ratings = ratings.filter(last_updated__gte=year_ago)

    # Фильтрация по типу активности
    if activity == 'hackathons':
        ratings = ratings.filter(hackathons_count__gt=0)
    elif activity == 'casecups':
        ratings = ratings.filter(casecups_count__gt=0)
    elif activity == 'webinars':
        ratings = ratings.filter(webinars_count__gt=0)

    # Сортировка по очкам
    ratings = ratings.order_by('-points')

    # Обновляем ранги для отфильтрованных результатов
    for i, rating in enumerate(ratings, 1):
        rating.rank = i

    # Пагинация
    paginator = Paginator(ratings, 20)  # 20 пользователей на страницу
    page = request.GET.get('page', 1)
    ratings = paginator.get_page(page)

    context = {
        'user': user,
        'ratings': ratings,
        'current_search': search_query,
        'current_period': period,
        'current_activity': activity,
    }

    return render(request, 'rating/rating_list.html', context)
