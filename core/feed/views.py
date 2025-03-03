from django.shortcuts import render, get_object_or_404, redirect
from user.models import User
from feed.models import Post, Webinar, Casecup
from hackathon.models import Hackathon, Tag
from .models import Event
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone


def feed_view(request):
    hash_code = request.GET.get("hash")
    user = get_object_or_404(User, hash_code=hash_code)

    # Получаем параметры фильтрации
    search_query = request.GET.get('search', '')
    tag_filter = request.GET.get('tag', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-start_hackathon')  # По умолчанию сортировка по дате начала (сначала новые)

    # Базовый QuerySet для хакатонов
    hackathons = Hackathon.objects.all()

    # Применяем поиск по названию и описанию
    if search_query:
        hackathons = hackathons.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # Фильтрация по тегам
    if tag_filter:
        hackathons = hackathons.filter(tags__name=tag_filter).distinct()

    # Фильтрация по статусу
    now = timezone.now()
    if status_filter == 'registration':
        hackathons = hackathons.filter(
            start_registation__lte=now,
            end_registration__gte=now
        )
    elif status_filter == 'active':
        hackathons = hackathons.filter(
            start_hackathon__lte=now,
            end_hackathon__gte=now
        )
    elif status_filter == 'finished':
        hackathons = hackathons.filter(end_hackathon__lt=now)
    elif status_filter == 'upcoming':
        hackathons = hackathons.filter(start_hackathon__gt=now)

    # Сортировка
    if sort_by == 'name':
        hackathons = hackathons.order_by('name')
    elif sort_by == '-name':
        hackathons = hackathons.order_by('-name')
    elif sort_by == 'start_hackathon':
        hackathons = hackathons.order_by('start_hackathon')
    elif sort_by == '-start_hackathon':
        hackathons = hackathons.order_by('-start_hackathon')
    elif sort_by == 'participants':
        hackathons = hackathons.order_by('-participants_count')

    # Получаем все уникальные теги для фильтра
    all_tags = Tag.objects.filter(hackathons__isnull=False).distinct()

    # Получаем остальные данные
    posts = Post.objects.all().order_by('-created_at')
    webinars = Webinar.objects.all()
    casecups = Casecup.objects.all()
    events = Event.objects.all()

    context = {
        'user': user,
        'posts': posts,
        'hackathons': hackathons,
        'webinars': webinars,
        'casecups': casecups,
        'events': events,
        'all_tags': all_tags,
        'current_search': search_query,
        'current_tag': tag_filter,
        'current_status': status_filter,
        'current_sort': sort_by,
        'statuses': [
            {'value': 'registration', 'label': 'Открыта регистрация'},
            {'value': 'active', 'label': 'Проходят сейчас'},
            {'value': 'finished', 'label': 'Завершенные'},
            {'value': 'upcoming', 'label': 'Предстоящие'}
        ],
        'sort_options': [
            {'value': '-start_hackathon', 'label': 'Сначала новые'},
            {'value': 'start_hackathon', 'label': 'Сначала старые'},
            {'value': 'name', 'label': 'По названию (А-Я)'},
            {'value': '-name', 'label': 'По названию (Я-А)'},
            {'value': 'participants', 'label': 'По количеству участников'}
        ]
    }
    return render(request, 'feed.html', context)


def webinar_detail_view(request, webinar_id):
    hash_code = request.GET.get("hash")
    user = get_object_or_404(User, hash_code=hash_code)
    webinar = get_object_or_404(Webinar, id=webinar_id)
    
    context = {
        'user': user,
        'webinar': webinar,
    }
    return render(request, 'webinar_detail.html', context)


def casecup_detail_view(request, casecup_id):
    hash_code = request.GET.get("hash")
    user = get_object_or_404(User, hash_code=hash_code)
    casecup = get_object_or_404(Casecup, id=casecup_id)
    
    context = {
        'user': user,
        'casecup': casecup,
    }
    return render(request, 'casecup_detail.html', context)


def webinar_register_view(request, webinar_id):
    hash_code = request.GET.get("hash")
    user = get_object_or_404(User, hash_code=hash_code)
    webinar = get_object_or_404(Webinar, id=webinar_id)
    
    if webinar.is_registration_open:
        if user not in webinar.participants.all():
            webinar.participants.add(user)
            messages.success(request, 'Вы успешно зарегистрированы на вебинар!')
        else:
            messages.info(request, 'Вы уже зарегистрированы на этот вебинар')
    else:
        messages.error(request, 'Регистрация на вебинар закрыта')
    
    return redirect(f'/feed/webinar/{webinar_id}/?hash={hash_code}')


def casecup_register_view(request, casecup_id):
    hash_code = request.GET.get("hash")
    user = get_object_or_404(User, hash_code=hash_code)
    casecup = get_object_or_404(Casecup, id=casecup_id)
    
    if casecup.is_registration_open:
        if user not in casecup.participants.all():
            casecup.participants.add(user)
            messages.success(request, 'Вы успешно зарегистрированы на кейс-чемпионат!')
        else:
            messages.info(request, 'Вы уже зарегистрированы на этот кейс-чемпионат')
    else:
        messages.error(request, 'Регистрация на кейс-чемпионат закрыта')
    
    return redirect(f'/feed/casecup/{casecup_id}/?hash={hash_code}')

