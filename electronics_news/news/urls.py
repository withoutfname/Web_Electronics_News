from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import ContentDetailView


urlpatterns = [
    path('', views.index, name='index'),            # Главная страница
    path('about/', views.about, name='about'),
    path('profile/', views.profile, name='profile'),
    path('news/', views.news, name='news'),
    path('authorise/', views.authorise, name='authorise'),
    path('register/', views.register, name='register'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('logout/', LogoutView.as_view(next_page='authorise'), name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('publish_content/', views.publish_content, name='publish_content'),
    path('content_detail/<int:id>/', ContentDetailView.as_view(), name='content_detail'),

]
