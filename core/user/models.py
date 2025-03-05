from django.db import models
import uuid
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

user_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'user_img'),  
    base_url='/static/img/user_img'
)

class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50, choices=[
        ('programming', 'Языки программирования'),
        ('database', 'Базы данных'),
        ('framework', 'Фреймворки'),
        ('tool', 'Инструменты'),
        ('other', 'Другое')
    ])
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['category', 'name']

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/', null=True, blank=True)
    xp_reward = models.PositiveIntegerField(default=0)
    crystal_reward = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name

class Certificate(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='certificates')
    hackathon = models.ForeignKey('hackathon.Hackathon', on_delete=models.CASCADE, null=True, blank=True)
    webinar = models.ForeignKey('feed.Webinar', on_delete=models.CASCADE, null=True, blank=True)
    casecup = models.ForeignKey('feed.Casecup', on_delete=models.CASCADE, null=True, blank=True)
    issue_date = models.DateField(auto_now_add=True)
    certificate_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    
    def __str__(self):
        event_name = self.hackathon.name if self.hackathon else (
            self.webinar.name if self.webinar else (
                self.casecup.name if self.casecup else "Неизвестное событие"
            )
        )
        return f"Сертификат {self.user.name} - {event_name}"

class User(models.Model):
    THEME_CHOICES = [
        ('light', 'Светлая'),
        ('dark', 'Темная')
    ]
    
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('en', 'Английский')
    ]
    
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)  
    name = models.CharField(max_length=100)
    coin = models.IntegerField(default=0)
    hash_code = models.CharField(max_length=16, unique=True, default="temp_value", null=True, editable=False)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name='users', blank=True)
    achievements = models.ManyToManyField(Achievement, related_name='users', blank=True)
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)
    is_premium = models.BooleanField(default=False)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='ru')
    bio = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.hash_code:
            self.hash_code = uuid.uuid4().hex[:16]
            
        # Расчет уровня на основе XP
        self.level = 1 + (self.xp // 100)  # Каждые 100 XP = 1 уровень
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    
    def add_xp(self, amount):
        """Добавляет опыт пользователю и обновляет уровень"""
        self.xp += amount
        self.save()
        
    def add_achievement(self, achievement):
        """Добавляет достижение пользователю и начисляет награды"""
        if achievement not in self.achievements.all():
            self.achievements.add(achievement)
            self.xp += achievement.xp_reward
            self.coin += achievement.crystal_reward
            self.save()
    
    def xp_to_next_level(self):
        """Возвращает количество XP, необходимое для достижения следующего уровня"""
        return (self.level + 1) * 100 - self.xp
    
    def participation_count(self):
        """Возвращает количество хакатонов, в которых участвовал пользователь"""
        return self.hackathons.count()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class UserNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('hackathon', 'Хакатон'),
        ('friend', 'Друзья'),
        ('achievement', 'Достижение'),
        ('system', 'Системное')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.name}"
    
    class Meta:
        ordering = ['-created_at']

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
