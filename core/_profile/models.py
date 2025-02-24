from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    telegram_id = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    pfp = models.ImageField(upload_to='pfp/')
    sex = models.CharField(max_length=1)
    age = models.IntegerField()
    status = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    about = models.TextField()
    role = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username