from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
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


def news_reviews(request):

    news_list = Content.objects.filter(type='news').order_by('-created_at')
    review_list = Content.objects.filter(type='review').order_by('-created_at')

    news_paginator = Paginator(news_list, 5)
    review_paginator = Paginator(review_list, 5)

    news_page_number = request.GET.get('news_page')
    review_page_number = request.GET.get('review_page')

    news_page_obj = news_paginator.get_page(news_page_number)
    review_page_obj = review_paginator.get_page(review_page_number)

    context = {
        'news_page_obj': news_page_obj,
        'review_page_obj': review_page_obj,
    }
    return render(request, 'news.html', context)

def password_reset(request):
    return render(request, 'password_reset.html')


def news_reviews_api(request):
    # Получаем параметры из URL
    content_type = request.GET.get('type')  # Тип контента ('news' или 'review')
    page_number = request.GET.get('page', 1)  # Номер страницы (по умолчанию 1)
    per_page = 5  # Количество элементов на странице

    if content_type == 'news':
        content_queryset = Content.objects.filter(type='news').order_by('-created_at')
    else:
        content_queryset = Content.objects.filter(type='review').order_by('-created_at')

    paginator = Paginator(content_queryset, per_page)
    page_obj = paginator.get_page(page_number)

    data = {
        'results': [
            {
                'id': content.id,
                'title': content.title,
                'author': content.author.username,
                'created_at': content.created_at.strftime('%d.%m.%Y'),
                'content': content.content[:100]  # Обрезаем для превью
            } for content in page_obj
        ],
        'has_next': page_obj.has_next(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    }

    return JsonResponse(data)
