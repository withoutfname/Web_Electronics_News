from enum import unique

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.contrib.auth.forms import AuthenticationForm

class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=20, required=True, label="Логин")
    nickname = forms.CharField(max_length=15, required=True, label="Ник")
    birthdate = forms.DateField(required=True, widget=forms.widgets.DateInput(attrs={'type': 'date'}), label="Дата рождения")
    email = forms.EmailField(required=True, label="Электронная почта")  # Переименовал для ясности
    password1 = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")
    consent = forms.BooleanField(required=True, label="Согласие на обработку персональных данных")

    class Meta:
        model = UserProfile
        fields = ['username', 'nickname', 'birthdate', 'email', 'password1', 'password2', 'consent']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Проверка на совпадение паролей
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")

        return cleaned_data




class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Логин'}), label="Логин")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label="Пароль")

