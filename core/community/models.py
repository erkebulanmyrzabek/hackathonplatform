from django.db import models
from user.models import User

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')
    user3 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user3')
    user4 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user4')

    