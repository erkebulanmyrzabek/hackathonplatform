from django.db import models
import uuid

class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)  
    name = models.CharField(max_length=100)
    coin = models.IntegerField(default=0)
    hash_code = models.CharField(max_length=16, unique=True, default="temp_value", null=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.hash_code:
            self.hash_code = uuid.uuid4().hex[:16]  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
