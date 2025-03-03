from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Hackathon
from user.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# Create your views here.
def hackathon_list(request):
    # Получаем хэш из параметров запроса
    hash_code = request.GET.get("hash")
    user = get_object_or_404(User, hash_code=hash_code) if hash_code else None

    # Получаем все хакатоны
    hackathons = Hackathon.objects.all().order_by('-start_hackathon')

    # Фильтрация по статусу
    status = request.GET.get('status', 'all')
    now = timezone.now()

    if status == 'registration':
        hackathons = hackathons.filter(
            start_registration__lte=now,
            end_registration__gte=now
        )
    elif status == 'active':
        hackathons = hackathons.filter(
            start_hackathon__lte=now,
            end_hackathon__gte=now
        )
    elif status == 'finished':
        hackathons = hackathons.filter(
            end_hackathon__lt=now
        )
    elif status == 'upcoming':
        hackathons = hackathons.filter(
            start_hackathon__gt=now
        )

    # Поиск по названию или описанию
    search_query = request.GET.get('search', '')
    if search_query:
        hackathons = hackathons.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Пагинация
    paginator = Paginator(hackathons, 12)  # 12 хакатонов на страницу
    page = request.GET.get('page', 1)
    hackathons = paginator.get_page(page)

    context = {
        'user': user,
        'hackathons': hackathons,
        'current_status': status,
        'current_search': search_query,
    }

    return render(request, 'hackathon/hackathon_list.html', context)

def hackathon_detail(request, pk):
    user = None
    if 'hash' in request.GET:
        user = get_object_or_404(User, hash_code=request.GET.get('hash'))
    
    hackathon = get_object_or_404(Hackathon, pk=pk)
    
    context = {
        'hackathon': hackathon,
        'user': user,
    }
    
    return render(request, 'hackathon/hackathon_detail.html', context)