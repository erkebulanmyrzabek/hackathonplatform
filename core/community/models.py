from django.db import models
from user.models import User
from django.utils import timezone



# Create your models here.
class Team(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открытая'),
        ('closed', 'Закрытая')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_community_teams', null=True)
    members = models.ManyToManyField(User, related_name='community_teams')
    max_members = models.PositiveIntegerField(default=4)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    @property
    def members_count(self):
        return self.members.count()
    
    @property
    def is_full(self):
        return self.members.count() >= self.max_members
    
    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

class Friendship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено')
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.sender.name} -> {self.receiver.name} ({self.status})"
    
    class Meta:
        unique_together = ['sender', 'receiver']
        verbose_name = 'Дружба'
        verbose_name_plural = 'Дружба'

class Leaderboard(models.Model):
    PERIOD_CHOICES = [
        ('week', 'Неделя'),
        ('month', 'Месяц'),
        ('year', 'Год'),
        ('all_time', 'За все время')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    score = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField()
    hackathons_won = models.PositiveIntegerField(default=0)
    hackathons_participated = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.period} - Ранг {self.rank}"
    
    class Meta:
        unique_together = ['user', 'period']
        ordering = ['rank']
        verbose_name = 'Лидерборд'
        verbose_name_plural = 'Лидерборды'

class CommunityEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('meetup', 'Митап'),
        ('workshop', 'Воркшоп'),
        ('conference', 'Конференция'),
        ('other', 'Другое')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, null=True, blank=True)
    is_online = models.BooleanField(default=False)
    online_url = models.URLField(null=True, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_community_events')
    participants = models.ManyToManyField(User, related_name='community_events', blank=True)
    max_participants = models.PositiveIntegerField(default=0)  # 0 = без ограничений
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_past(self):
        return timezone.now() > self.end_date
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    @property
    def participants_count(self):
        return self.participants.count()
    
    @property
    def is_full(self):
        return self.max_participants > 0 and self.participants.count() >= self.max_participants
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Событие сообщества'
        verbose_name_plural = 'События сообщества'

class UserSearch(models.Model):
    """Модель для хранения истории поиска пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    query = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.query}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Поиск пользователя'
        verbose_name_plural = 'Поиски пользователей'
    