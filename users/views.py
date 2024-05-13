from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm - initial version - extended the form with RegisterForm
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth.models import User
from .models import Profile


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome {username}, your account is created!')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profilepage(request, username=None):
    username = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'users/profile.html', {'profile': profile, 'username': username})

    # return render(request, 'users/profile.html', {'username': username})

