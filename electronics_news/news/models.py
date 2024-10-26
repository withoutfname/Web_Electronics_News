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
    email = models.EmailField(unique=True)  # Используйте стандартное поле email

    def clean(self):
        super().clean()  # Вызов родительского метода clean
        # Добавьте свои проверки здесь, если нужно

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
    image = models.ImageField(upload_to='news_content/news_images/', blank=True, null=True)  # Поле для изображений
    video = models.FileField(upload_to='news_content/news_videos/', blank=True, null=True)  # Поле для хранения ссылки на видео

    def __str__(self):
        return self.title


