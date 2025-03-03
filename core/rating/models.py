from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User

class Rating(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rating')
    points = models.IntegerField(default=0)
    points_change = models.IntegerField(default=0)
    hackathons_count = models.IntegerField(default=0)
    casecups_count = models.IntegerField(default=0)
    webinars_count = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-points']
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'

    def __str__(self):
        return f"{self.user.username} - {self.points} баллов"

    def update_rank(self):
        """Обновляет ранг пользователя в общем рейтинге"""
        higher_ratings = Rating.objects.filter(points__gt=self.points).count()
        self.rank = higher_ratings + 1
        self.save()

@receiver(post_save, sender=User)
def create_user_rating(sender, instance, created, **kwargs):
    """Создает запись рейтинга при создании нового пользователя"""
    if created:
        Rating.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_rating(sender, instance, **kwargs):
    """Сохраняет рейтинг пользователя при обновлении"""
    try:
        instance.rating.save()
    except Rating.DoesNotExist:
        Rating.objects.create(user=instance)
