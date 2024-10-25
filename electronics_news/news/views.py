from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm, CustomAuthForm


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
def profile_view(request):
    user = request.user  # Получаем текущего аутентифицированного пользователя
    return render(request, 'profile.html', {'nickname': user.userprofile.nickname})