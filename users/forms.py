from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            "username": "Username",
            'email': 'Email',
            'password1': "Password",
            'password2': "Confirm password",
        }

# class RegisterForm(UserCreationForm):
#     username = forms.CharField(label='Username', max_length=50)
#     email = forms.EmailField()
#     password1 = forms.CharField()
#     password2 = forms.PasswordInput()
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']

