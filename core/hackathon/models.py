from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.validators import MinValueValidator
import os
import uuid

from user.models import User

def hackathon_image_path(instance, filename):
    ext = filename.split('.')[-1]
    if instance.pk:
        return f'hackathon_{instance.pk}.{ext}'
    return filename

hackathon_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'hackathon_img'),  
    base_url='/static/img/hackathon_img'
)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class PrizePlaces(models.Model):
    hackathon = models.ForeignKey('Hackathon', on_delete=models.CASCADE, related_name='prize_places')
    place = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    prize_amount = models.IntegerField()
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    winner_team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['place']
        unique_together = ['hackathon', 'place']

    def __str__(self):
        return f"{self.hackathon.name} - {self.place} место"

class Track(models.Model):
    hackathon = models.ForeignKey('Hackathon', on_delete=models.CASCADE, related_name='tracks')
    name = models.CharField(max_length=100)
    description = models.TextField()
    task_description = models.TextField()
    max_participants = models.PositiveIntegerField(default=0)  # 0 = без ограничений
    
    def __str__(self):
        return f"{self.name} - {self.hackathon.name}"
    
    @property
    def participants_count(self):
        return self.teams.count() + self.solo_participants.count()

class Team(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открытая'),
        ('closed', 'Закрытая')
    ]
    
    name = models.CharField(max_length=100)
    hackathon = models.ForeignKey('Hackathon', on_delete=models.CASCADE, related_name='teams')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='teams', null=True, blank=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    members = models.ManyToManyField(User, related_name='teams')
    max_members = models.PositiveIntegerField(default=4)
    join_code = models.CharField(max_length=8, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = uuid.uuid4().hex[:8]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.hackathon.name}"
    
    @property
    def members_count(self):
        return self.members.count()
    
    @property
    def is_full(self):
        return self.members.count() >= self.max_members

class Solution(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('submitted', 'Отправлено'),
        ('reviewed', 'Проверено')
    ]
    
    hackathon = models.ForeignKey('Hackathon', on_delete=models.CASCADE, related_name='solutions')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='solutions', null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='solutions', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solo_solutions', null=True, blank=True)
    repository_url = models.URLField()
    presentation_url = models.URLField(null=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='liked_solutions', blank=True)
    
    def __str__(self):
        if self.team:
            return f"Решение команды {self.team.name} - {self.hackathon.name}"
        return f"Решение {self.user.name} - {self.hackathon.name}"
    
    @property
    def likes_count(self):
        return self.likes.count()

class SolutionReview(models.Model):
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    score = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Оценка {self.score} для {self.solution}"
    
    class Meta:
        unique_together = ['solution', 'reviewer']

class Hackathon(models.Model):
    STATUS_CHOICES = [
        ('anonce', 'Анонс'),
        ('start_registration', 'Регистрации'),
        ('end_registration', 'Регистрация завершена'),
        ('started', 'Проводится'),
        ('determining_stage', 'Определение победителей'),
        ('finished', 'Завершенный'),
    ]
    
    PARTICIPATION_TYPE_CHOICES = [
        ('solo', 'Индивидуальное'),
        ('team', 'Командное'),
        ('both', 'Оба варианта')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=100, choices=[('online', 'Онлайн'), ('offline', 'Офлайн'), ('hybrid', 'Гибридный')], default='online')
    participation_type = models.CharField(max_length=10, choices=PARTICIPATION_TYPE_CHOICES, default='both')
    
    start_registation = models.DateField(null=True, blank=True)
    end_registration = models.DateField(null=True, blank=True)
    anonce_start = models.DateField(null=True, blank=True)
    start_hackathon = models.DateField(null=True, blank=True)
    end_hackathon = models.DateField(null=True, blank=True)
    submission_deadline = models.DateTimeField(null=True, blank=True)
    
    image = models.ImageField(storage=hackathon_img_url, upload_to=hackathon_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='anonce')
    participants = models.ManyToManyField(User, related_name='hackathons')
    solo_participants = models.ManyToManyField(User, related_name='solo_hackathons', blank=True)
    tags = models.ManyToManyField(Tag, related_name='hackathons', blank=True)
    prize_pool = models.IntegerField(default=0)
    number_of_winners = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1)])
    participants_count = models.PositiveIntegerField(default=0)
    max_team_size = models.PositiveIntegerField(default=4)
    
    # Организаторы
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='organized_hackathons')
    
    # Дополнительная информация
    location = models.CharField(max_length=200, null=True, blank=True)
    rules = models.TextField(null=True, blank=True)
    program = models.TextField(null=True, blank=True)
    judges = models.TextField(null=True, blank=True)
    
    # Настройки
    enable_public_voting = models.BooleanField(default=False)
    show_solutions_after_deadline = models.BooleanField(default=True)
    xp_reward_participation = models.PositiveIntegerField(default=50)
    xp_reward_winner = models.PositiveIntegerField(default=200)
    crystal_reward_winner = models.PositiveIntegerField(default=100)

    def update_participants_count(self):
        team_participants = sum(team.members.count() for team in self.teams.all())
        solo_count = self.solo_participants.count()
        self.participants_count = team_participants + solo_count
        self.save()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Если это новый объект (без ID) или изображение изменилось
        if self.pk:
            try:
                old_instance = Hackathon.objects.get(pk=self.pk)
                if old_instance.image and self.image != old_instance.image:
                    old_instance.image.delete(save=False)
            except Hackathon.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    @property
    def is_registration_open(self):
        from django.utils import timezone
        now = timezone.now().date()
        return (self.start_registation and self.end_registration and 
                self.start_registation <= now <= self.end_registration)
    
    @property
    def is_submission_open(self):
        from django.utils import timezone
        now = timezone.now()
        return (self.start_hackathon and self.submission_deadline and 
                self.start_hackathon <= now.date() <= self.submission_deadline)
    
    @property
    def can_view_solutions(self):
        from django.utils import timezone
        now = timezone.now()
        return self.show_solutions_after_deadline and self.submission_deadline and now > self.submission_deadline
    
    def award_winners(self):
        """Награждает победителей хакатона"""
        for prize_place in self.prize_places.all():
            if prize_place.winner:
                prize_place.winner.add_xp(self.xp_reward_winner)
                prize_place.winner.coin += self.crystal_reward_winner
                prize_place.winner.save()
            elif prize_place.winner_team:
                for member in prize_place.winner_team.members.all():
                    member.add_xp(self.xp_reward_winner)
                    member.coin += self.crystal_reward_winner
                    member.save()

class LiveStream(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='livestreams')
    title = models.CharField(max_length=200)
    url = models.URLField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.hackathon.name}"
    
    class Meta:
        ordering = ['start_time']

class FAQ(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.question} - {self.hackathon.name}"
    
    class Meta:
        ordering = ['order']
    