from django.contrib import admin
from .models import Content, UserProfile

admin.site.register(Content)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'nickname', 'email', 'can_publish_content')
    list_editable = ('can_publish_content',)
    search_fields = ('username', 'nickname', 'email')

