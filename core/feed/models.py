from django.db import models
from django.core.files.storage import FileSystemStorage
from community.models import Team
from django.conf import settings
import os
from django.utils import timezone

def post_image_path(instance, filename):
    # Получаем расширение файла
    ext = filename.split('.')[-1]
    # Если объект уже создан, используем его ID, иначе используем временную метку
    if instance.pk:
        return f'post_{instance.pk}.{ext}'
    return filename

def webinar_image_path(instance, filename):
    ext = filename.split('.')[-1]
    if instance.pk:
        return f'webinar_{instance.pk}.{ext}'
    return filename

def casecup_image_path(instance, filename):
    ext = filename.split('.')[-1]
    if instance.pk:
        return f'casecup_{instance.pk}.{ext}'
    return filename

def event_image_path(instance, filename):
    ext = filename.split('.')[-1]
    if instance.pk:
        return f'event_{instance.pk}.{ext}'
    return filename

post_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'post_img'),  
    base_url='/static/img/post_img'
)

webinar_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'webinar_img'),  
    base_url='/static/img/webinar_img'
)

casecup_img_url = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'static', 'img', 'casecup_img'),  
    base_url='/static/img/casecup_img'
)

class Post(models.Model):
    header = models.CharField(max_length=100)
    body = models.TextField()
    image = models.ImageField(storage=post_img_url, upload_to=post_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cat = models.ForeignKey('feed.Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.header
    
    def save(self, *args, **kwargs):
        # Если объект уже существует, удаляем старое изображение при загрузке нового
        if self.pk:
            try:
                old_instance = Post.objects.get(pk=self.pk)
                if old_instance.image and self.image != old_instance.image:
                    old_instance.image.delete(save=False)
            except Post.DoesNotExist:
                pass
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Webinar(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    start_registration = models.DateField(default=timezone.now)
    end_registration = models.DateField(default=timezone.now)
    image = models.ImageField(storage=webinar_img_url, upload_to=webinar_image_path)
    cat = models.ForeignKey('feed.Category', on_delete=models.CASCADE)
    participants = models.ManyToManyField('user.User', related_name='webinars', blank=True)
    max_participants = models.PositiveIntegerField(default=100)

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = Webinar.objects.get(pk=self.pk)
                if old_instance.image and self.image != old_instance.image:
                    old_instance.image.delete(save=False)
            except Webinar.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    @property
    def is_registration_open(self):
        now = timezone.now().date()
        return self.start_registration <= now <= self.end_registration and self.participants_count < self.max_participants

    @property
    def participants_count(self):
        return self.participants.count()

    def __str__(self):
        return self.name

class Casecup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(storage=casecup_img_url, upload_to=casecup_image_path)
    cat = models.ForeignKey('feed.Category', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = Casecup.objects.get(pk=self.pk)
                if old_instance.image and self.image != old_instance.image:
                    old_instance.image.delete(save=False)
            except Casecup.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class Event(models.Model):
    EVENT_TYPES = [
        ('hackathon', 'Хакатон'),
        ('casecamp', 'Кейс-чемпионат'),
        ('webinar', 'Вебинар'),
    ]

    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateTimeField()
    participants_count = models.IntegerField(default=0)
    format = models.CharField(max_length=100)  # онлайн/офлайн
    image = models.ImageField(upload_to=event_image_path, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = Event.objects.get(pk=self.pk)
                if old_instance.image and self.image != old_instance.image:
                    old_instance.image.delete(save=False)
            except Event.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.title
