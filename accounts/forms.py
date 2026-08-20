from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=False, label='Ad')
    last_name = forms.CharField(required=False, label='Soyad')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(label='İstifadəçi adı və ya email')
    password = forms.CharField(widget=forms.PasswordInput, label='Şifrə')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('username')
        password = cleaned.get('password')
        if username and password:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user_obj = None
            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                except User.DoesNotExist:
                    user_obj = None
            self.user = authenticate(username=user_obj.username if user_obj else username, password=password)
            if self.user is None:
                raise forms.ValidationError('İstifadəçi adı və ya şifrə yanlışdır.')
        return cleaned

    def get_user(self):
        return self.user
