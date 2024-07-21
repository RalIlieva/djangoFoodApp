from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm - initial version - extended the form with RegisterForm
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth.models import User
from .models import Profile
from food.models import Item


def register(request):
    if request.method == 'POST':
        print('Form submitted')
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            print(f'User {username} created successfully')
            messages.success(request, f'Welcome {username}, your account is created!')
            return redirect('login')
        else:
            print('Form is not valid', form.errors)
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profilepage(request, username=None):
    username = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    items = Item.objects.filter(user_name=user)
    return render(request, 'users/profile.html', {'profile': profile, 'username': username, 'items': items})
