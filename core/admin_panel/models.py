from django.db import models
from user.models import User
from hackathon.models import Hackathon
from django.utils import timezone

class AdminRole(models.Model):
    """Модель для хранения ролей администраторов"""
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('content_manager', 'Контент-менеджер'),
        ('organizer', 'Организатор'),
        ('analyst', 'Аналитик')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.get_role_display()}"
    
    class Meta:
        unique_together = ['user', 'role']
        verbose_name = 'Роль администратора'
        verbose_name_plural = 'Роли администраторов'

class HackathonRequest(models.Model):
    """Модель для хранения запросов на проведение хакатонов"""
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hackathon_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    expected_start_date = models.DateField()
    expected_end_date = models.DateField()
    expected_participants = models.PositiveIntegerField()
    prize_pool = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def approve(self, reviewer):
        """Одобряет запрос и создает хакатон"""
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
        
        # Создаем хакатон
        hackathon = Hackathon.objects.create(
            name=self.title,
            description=self.description,
            start_hackathon=self.expected_start_date,
            end_hackathon=self.expected_end_date,
            prize_pool=self.prize_pool,
            organizer=self.user,
            status='anonce'
        )
        
        # Назначаем пользователя организатором
        AdminRole.objects.get_or_create(
            user=self.user,
            role='organizer',
            assigned_by=reviewer
        )
        
        return hackathon
    
    def reject(self, reviewer, comment=None):
        """Отклоняет запрос"""
        self.status = 'rejected'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        if comment:
            self.comment = comment
        self.save()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запрос на хакатон'
        verbose_name_plural = 'Запросы на хакатоны'

class AdminLog(models.Model):
    """Модель для хранения логов действий администраторов"""
    ACTION_CHOICES = [
        ('create', 'Создание'),
        ('update', 'Обновление'),
        ('delete', 'Удаление'),
        ('approve', 'Одобрение'),
        ('reject', 'Отклонение'),
        ('block', 'Блокировка'),
        ('unblock', 'Разблокировка'),
        ('other', 'Другое')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50, help_text="Тип сущности (пользователь, хакатон и т.д.)")
    entity_id = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.get_action_display()} - {self.entity_type} #{self.entity_id}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Лог администратора'
        verbose_name_plural = 'Логи администраторов'

class UserBlock(models.Model):
    """Модель для хранения информации о блокировке пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocks')
    blocked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    reason = models.TextField()
    blocked_until = models.DateTimeField(null=True, blank=True, help_text="Если пусто, то блокировка постоянная")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.name} - заблокирован до {self.blocked_until or 'бессрочно'}"
    
    @property
    def is_active(self):
        if not self.blocked_until:
            return True
        return timezone.now() < self.blocked_until
    
    class Meta:
        verbose_name = 'Блокировка пользователя'
        verbose_name_plural = 'Блокировки пользователей'

class Analytics(models.Model):
    """Модель для хранения аналитических данных"""
    date = models.DateField(unique=True)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    hackathons_created = models.PositiveIntegerField(default=0)
    hackathons_completed = models.PositiveIntegerField(default=0)
    solutions_submitted = models.PositiveIntegerField(default=0)
    transactions_completed = models.PositiveIntegerField(default=0)
    total_crystals_spent = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Аналитика за {self.date}"
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Аналитика'
        verbose_name_plural = 'Аналитика'

class OrganizerDashboard(models.Model):
    """Модель для хранения данных дашборда организатора"""
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizer_dashboards')
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='dashboards')
    participants_count = models.PositiveIntegerField(default=0)
    teams_count = models.PositiveIntegerField(default=0)
    solutions_count = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Дашборд {self.organizer.name} - {self.hackathon.name}"
    
    def update_stats(self):
        """Обновляет статистику дашборда"""
        from hackathon.models import Solution, SolutionReview
        
        self.participants_count = self.hackathon.participants.count()
        self.teams_count = self.hackathon.teams.count()
        self.solutions_count = Solution.objects.filter(hackathon=self.hackathon).count()
        
        # Расчет среднего балла
        reviews = SolutionReview.objects.filter(solution__hackathon=self.hackathon)
        if reviews.exists():
            self.average_score = reviews.aggregate(models.Avg('score'))['score__avg']
        
        self.save()
    
    class Meta:
        unique_together = ['organizer', 'hackathon']
        verbose_name = 'Дашборд организатора'
        verbose_name_plural = 'Дашборды организаторов'
