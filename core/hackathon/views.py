from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Hackathon, Tag, PrizePlaces
from user.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import HackathonSerializer, TagSerializer, PrizePlacesSerializer

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
            Q(name__icontains=search_query) |
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

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PrizePlacesViewSet(viewsets.ModelViewSet):
    queryset = PrizePlaces.objects.all()
    serializer_class = PrizePlacesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class HackathonViewSet(viewsets.ModelViewSet):
    queryset = Hackathon.objects.all()
    serializer_class = HackathonSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        hackathon = self.get_object()
        if not hackathon.is_registration_open:
            return Response(
                {"error": "Registration is closed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hackathon.participants.add(request.user)
        hackathon.update_participants_count()
        return Response({"status": "joined"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        hackathon = self.get_object()
        if request.user in hackathon.participants.all():
            hackathon.participants.remove(request.user)
            hackathon.update_participants_count()
            return Response({"status": "left"}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Not a participant"},
            status=status.HTTP_400_BAD_REQUEST
        )