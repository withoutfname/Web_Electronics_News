from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import ContentDetailView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('profile/', views.profile, name='profile'),
    path('news/', views.news_reviews, name='news'),
    path('authorise/', views.authorise, name='authorise'),
    path('register/', views.register, name='register'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('logout/', LogoutView.as_view(next_page='authorise'), name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('publish_content/', views.publish_content, name='publish_content'),
    path('content_detail/<int:id>/', ContentDetailView.as_view(), name='content_detail'),
    path('edit_content/<int:content_id>/', views.edit_content, name='edit_content'),
    path('delete_content/<int:content_id>/', views.delete_content, name='delete_content'),
    path('delete_image/<int:image_id>/', views.delete_image, name='delete_image'),
    path('delete_video/<int:video_id>/', views.delete_video, name='delete_video'),
    path('api/content/', views.news_reviews_api, name='news_reviews_api'),

]
