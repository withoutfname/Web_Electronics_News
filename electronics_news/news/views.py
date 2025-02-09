from lib2to3.fixes.fix_input import context

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views.generic import DetailView
from .forms import (
    RegistrationForm,
    CustomAuthForm,
    EditProfileForm,
    ContentForm,
    ContentImageFormSet,
    ContentVideoFormSet
)
from .models import Content, ContentImage, ContentVideo, UserProfile

# Create your views here.

def about(request):
    return render(request, "about.html")

def index(request):
    latest_news = Content.objects.order_by('-created_at')[:6]
    return render(request, 'index.html', {'latest_news': latest_news})

def register(request):
    if request.method == 'POST':
        register_form = RegistrationForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect('authorise')  # Перенаправление на страницу входа
        else:
            messages.error(request, "Ошибка при регистрации. Пожалуйста, проверьте форму.")
    else:
        register_form = RegistrationForm()

    return render(request, 'registration.html', {'register_form': register_form})

def authorise(request):
    if request.method == 'POST':
        form = CustomAuthForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')  # Замените на нужный вам URL
    else:
        form = CustomAuthForm()

    return render(request, 'authorization.html', {'auth_form': form})

@login_required
def profile(request):
    user = request.user
    published_news = Content.objects.filter(author=user)
    return render(request, 'profile.html', {
        'nickname': user.nickname,
        'published_news': published_news,
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        edit_profile_form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if edit_profile_form.is_valid():
            edit_profile_form.save()
            return redirect('profile')
    else:
        edit_profile_form = EditProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'edit_profile_form': edit_profile_form})

@login_required
def publish_content(request):
    if not request.user.can_publish_content:
        messages.error(request, "У вас нет прав на публикацию контента.")
        return redirect('profile')

    if request.method == 'POST':
        content_form = ContentForm(request.POST)
        image_formset = ContentImageFormSet(request.POST, request.FILES)
        video_formset = ContentVideoFormSet(request.POST, request.FILES)

        if content_form.is_valid() and image_formset.is_valid() and video_formset.is_valid():
            content = content_form.save(commit=False)
            content.author = request.user
            content.save()

            for form in image_formset:
                if form.cleaned_data.get('image'):
                    image = form.save(commit=False)
                    image.content = content
                    image.save()

            for form in video_formset:
                if form.cleaned_data.get('video'):
                    video = form.save(commit=False)
                    video.content = content
                    video.save()

            messages.success(request, "Контент успешно опубликован.")
            return redirect('profile')
    else:
        content_form = ContentForm()
        image_formset = ContentImageFormSet(queryset=ContentImage.objects.none())
        video_formset = ContentVideoFormSet(queryset=ContentVideo.objects.none())

    return render(request, 'publish_content.html', {
        'content_form': content_form,
        'image_formset': image_formset,
        'video_formset': video_formset,
    })

@login_required
def content_detail(request, id):
    content = get_object_or_404(Content, id=id)
    return render(request, 'content_detail.html', {'content': content})

class ContentDetailView(DetailView):
    model = Content
    template_name = 'content_detail.html'
    context_object_name = 'content'

    def get_object(self):
        return get_object_or_404(Content, id=self.kwargs['id'])

@login_required
def edit_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    existing_images = content.images.all()
    existing_videos = content.videos.all()

    available_slots = 5
    remaining_image_slots = available_slots - existing_images.count()
    remaining_video_slots = available_slots - existing_videos.count()

    available_image_slots = list(range(remaining_image_slots))
    available_video_slots = list(range(remaining_video_slots))


    if request.method == 'POST':

        content.title = request.POST.get('title')
        content.content = request.POST.get('content')
        content.save()


        for image in existing_images:
            if f'delete_image_{image.id}' in request.POST:
                image.delete()
                messages.success(request, f'Изображение {image.id} успешно удалено.')


        if 'images' in request.FILES:
            for file in request.FILES.getlist('images'):
                if remaining_image_slots > 0:
                    ContentImage.objects.create(content=content, image=file)
                    remaining_image_slots -= 1


        for video in existing_videos:
            if f'delete_video_{video.id}' in request.POST:
                video.delete()
                messages.success(request, f'Видео {video.id} успешно удалено.')


        if 'videos' in request.FILES:
            for file in request.FILES.getlist('videos'):
                ContentVideo.objects.create(content=content, video=file)

        messages.success(request, 'Контент успешно обновлён.')
        return redirect('edit_content', content_id=content.id)

    return render(request, 'edit_content.html', {
        'content': content,
        'existing_images': existing_images,
        'existing_videos': existing_videos,
        'available_image_slots': available_image_slots,
        'available_video_slots': available_video_slots,
    })

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ContentImage, id=image_id)
    image.delete()
    return redirect('edit_content')

@login_required
def delete_video(request, video_id):
    video = get_object_or_404(ContentVideo, id=video_id)
    video.delete()
    return redirect('edit_content')

@login_required
def delete_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.method == 'POST':
        content.delete()
        messages.success(request, 'Контент успешно удален.')
        return redirect('profile')
    return render(request, 'confirm_delete.html', {'content': content})

@login_required
def delete_media(request, media_id, media_type):
    if media_type == 'image':
        media = get_object_or_404(ContentImage, id=media_id)
    elif media_type == 'video':
        media = get_object_or_404(ContentVideo, id=media_id)
    else:
        return redirect('profile')

    if request.method == 'POST':
        media.delete()
        messages.success(request, f'{media_type.capitalize()} успешно удалено.')
        return redirect('edit_content', content_id=media.content.id)

    return render(request, 'confirm_delete_media.html', {'media': media, 'media_type': media_type})

def password_reset(request):
    return render(request, 'password_reset.html')


def news_reviews(request):

    search_query = request.GET.get('search', '')


    news_list = Content.objects.filter(type='news').order_by('-created_at')
    if search_query:
        news_list = news_list.filter(
            content__icontains=search_query
        ) | news_list.filter(
            title__icontains=search_query
        )


    news_paginator = Paginator(news_list, 5)
    news_page_number = request.GET.get('news_page')
    news_page_obj = news_paginator.get_page(news_page_number)

    context = {
        'news_page_obj': news_page_obj,
        'search': search_query,
    }

    return render(request, 'news.html', context)

def reviews(request):
    reviews = Content.objects.filter(type='review').order_by('-created_at')
    paginator = Paginator(reviews, 5)
    page_number = request.GET.get('page')
    reviews_page_obj = paginator.get_page(page_number)
    return render(request, 'reviews.html', {'reviews_page_obj': reviews_page_obj})



def review_list_api(request):
    page = request.GET.get('page', 1)
    reviews = Content.objects.filter(type='review').order_by('-created_at')
    paginator = Paginator(reviews, 2)
    page_obj = paginator.get_page(page)

    data = {
        'reviews': list(page_obj.object_list.values('id', 'title', 'content', 'created_at', 'author__username', 'author__nickname', 'author__id')),
        'has_next': page_obj.has_next(),
    }
    return JsonResponse(data)

def community(request):
    search_query = request.GET.get('search', '').strip()

    users = UserProfile.objects.annotate(content_count = Count('content'))
    if search_query:
        users = users.filter(Q(nickname__icontains=search_query))
    context = {
        'users' : users,
    }
    return render(request, 'community.html', context)

def user_detail(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)
    context = {
        "user" : user
    }
    return render(request, "user_detail.html", context)