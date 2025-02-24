from django.db import models

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField('profile.User', through='Membership')

    def __str__(self):
        return self.name
    
class Friend(models.Model):
    user = models.ForeignKey('profile.User', on_delete=models.CASCADE)
    friend = models.ForeignKey('profile.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.user