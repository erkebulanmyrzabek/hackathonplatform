from django.db import models

# Create your models here.
class Post(models.Model):
    header = models.CharField(max_length=100)
    body = models.TextField()
    image = models.ImageField(upload_to='post_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat = models.ForeignKey('feed.Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.header
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
    