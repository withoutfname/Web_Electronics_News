from enum import unique

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory

from .models import UserProfile, Content, ContentImage, ContentVideo
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


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nickname', 'avatar']  # Укажите нужные поля






class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'content', 'type', 'age_restriction']

class ContentImageForm(forms.ModelForm):
    class Meta:
        model = ContentImage
        fields = ['image']

class ContentVideoForm(forms.ModelForm):
    class Meta:
        model = ContentVideo
        fields = ['video']

ContentImageFormSet = inlineformset_factory(Content, ContentImage, form=ContentImageForm, extra=5, can_delete=True)
ContentVideoFormSet = inlineformset_factory(Content, ContentVideo, form=ContentVideoForm, extra=5, can_delete=True)

from django.views.generic import DetailView
from .models import Content

class ContentDetailView(DetailView):
    model = Content
    template_name = 'content_detail.html'  # Adjust as necessary
    context_object_name = 'content'



