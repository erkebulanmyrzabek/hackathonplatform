from django.contrib import admin
from .models import Post, Category, Webinar, Casecup

# Register your models here.

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Webinar)
admin.site.register(Casecup)