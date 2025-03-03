from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.validators import MinValueValidator
import os

from user.models import User

hackathon_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'hackathon_img'),  
    base_url='/static/img/hackathon_img'
)

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
    start_registation = models.DateField(null=True, blank=True)
    end_registration = models.DateField(null=True, blank=True)
    anonce_start = models.DateField(null=True, blank=True)
    start_hackathon = models.DateField(null=True, blank=True)
    end_hackathon = models.DateField(null=True, blank=True)
    image = models.ImageField(storage=hackathon_img_url, upload_to='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='anonce')
    participants = models.ManyToManyField(User, related_name='hackathons')
    tags = models.CharField(max_length=255, default='')  # теги будут храниться как строка с разделителями
    prize_pool = models.IntegerField(default=0)
    number_of_winners = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1)])

    def get_tags(self):
        return self.tags.split(',') if self.tags else []

    def set_tags(self, tags_list):
        self.tags = ','.join(tags_list)

    def __str__(self):
        return self.name
    