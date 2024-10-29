from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import DetailView

from .forms import RegistrationForm, CustomAuthForm, EditProfileForm, ContentForm, ContentImageForm, ContentVideoForm
from .models import Content, ContentImage, ContentVideo, UserProfile
from .forms import ContentForm, ContentImageFormSet, ContentVideoFormSet


# Create your views here.

def about(request):
    return render(request, "about.html")

def index(request):
    return render(request, "index.html")

def news(request):
    return render(request, "news.html")

def profile(request):
    return render(request, "profile.html")


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


def password_reset(request):
    return render(request, "password_reset.html")


@login_required
def profile(request):
    user = request.user  # Получаем текущего пользователя
    published_news = Content.objects.filter(author=user)  # Загружаем новости текущего пользователя

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
            return redirect('profile')  # Перенаправление на страницу профиля
    else:
        edit_profile_form = EditProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'edit_profile_form': edit_profile_form})


@login_required
def publish_content(request):
    if request.method == 'POST':
        content_form = ContentForm(request.POST)
        image_formset = ContentImageFormSet(request.POST, request.FILES, queryset=ContentImage.objects.none())
        video_formset = ContentVideoFormSet(request.POST, request.FILES, queryset=ContentVideo.objects.none())

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
    model = Content  # Указываем модель
    template_name = 'content_detail.html'  # Укажите ваш шаблон
    context_object_name = 'content'  # Имя контекста для шаблона

    def get_object(self):
        # Переопределяем метод, чтобы получить объект по ID
        obj = get_object_or_404(Content, id=self.kwargs['id'])
        return obj

@login_required
def edit_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)

    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Замените на нужный URL после успешного редактирования
    else:
        form = ContentForm(instance=content)

    return render(request, 'edit_content.html', {'form': form, 'content': content})

@login_required
def delete_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.method == 'POST':
        content.delete()
        return redirect('profile')  # Замените на нужный URL после успешного удаления
    return render(request, 'confirm_delete.html', {'content': content})

