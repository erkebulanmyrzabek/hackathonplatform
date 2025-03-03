from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.validators import MinValueValidator
import os

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

    class Meta:
        ordering = ['place']
        unique_together = ['hackathon', 'place']

    def __str__(self):
        return f"{self.hackathon.name} - {self.place} место"

class Hackathon(models.Model):
    STATUS_CHOICES = [
        ('anonce', 'Анонс'),
        ('start_registration', 'Регистрации'),
        ('end_registration', 'Регистрация завершена'),
        ('started', 'Проводится'),
        ('determining_stage', 'Определение победителей'),
        ('finished', 'Завершенный'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=100, choices=[('online', 'Онлайн'), ('offline', 'Офлайн'), ('hybrid', 'Гибридный')], default='online')

    start_registation = models.DateField(null=True, blank=True)
    end_registration = models.DateField(null=True, blank=True)
    anonce_start = models.DateField(null=True, blank=True)
    start_hackathon = models.DateField(null=True, blank=True)
    end_hackathon = models.DateField(null=True, blank=True)

    image = models.ImageField(storage=hackathon_img_url, upload_to=hackathon_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='anonce')
    participants = models.ManyToManyField(User, related_name='hackathons')
    tags = models.ManyToManyField(Tag, related_name='hackathons', blank=True)
    prize_pool = models.IntegerField(default=0)
    number_of_winners = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1)])
    participants_count = models.PositiveIntegerField(default=0)

    def update_participants_count(self):
        self.participants_count = self.participants.count()
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
    