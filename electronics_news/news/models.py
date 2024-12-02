from django.db import models
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser

# Create your models here.

class UserProfile(AbstractUser):
    username = models.CharField(max_length=20, unique=True, blank=False)
    nickname = models.CharField(max_length=15, blank=False)
    birthdate = models.DateField(blank=False, null=False)
    avatar = models.ImageField(upload_to='user_avatars', default='user_avatars/default-avatar.png')
    email = models.EmailField(unique=True)
    can_publish_content = models.BooleanField(default=True, verbose_name='Может публиковать контент')

    def clean(self):
        super().clean()


    def __str__(self):
        return self.username

class Content(models.Model):
    CONTENT_TYPES = [
        ('news', 'Новости'),
        ('review', 'Обзор'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    age_restriction = models.BooleanField(default=False, verbose_name="Возрастные ограничения")

    def __str__(self):
        return self.title

class ContentImage(models.Model):
    content = models.ForeignKey(Content, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news_content/news_images/')

class ContentVideo(models.Model):
    content = models.ForeignKey(Content, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to='news_content/news_videos/')







