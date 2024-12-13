from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import EmailAuthenticationForm, EmailSignUpForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Profile
from django.contrib.auth.models import User

def login_chef(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.user_cache)
            next_url = request.POST.get('next', 'home')
            return redirect(next_url)

    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'registration/login.html', {
        'form': form,
        'next': request.GET.get('next', 'home')
    })


from django.contrib.auth import login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.user_cache)
            return redirect('home')
    else:
        form = EmailAuthenticationForm(request)
    return render(request, 'registration/login.html', {'form': form})


@login_required
def logout_chef(request):
    logout(request)
    return render(request, 'registration/logout.html')


def signup_view(request):
    if request.method == 'POST':
        form = EmailSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = EmailSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def follow_toggle(request, user_id):
    user_to_toggle = get_object_or_404(User, id=user_id)
    if request.user.id != user_id:  # Prevent self-following
        profile = request.user.profile
        
        if profile.is_following(user_to_toggle):
            profile.unfollow(user_to_toggle)
            is_following = False
        else:
            profile.follow(user_to_toggle)
            is_following = True
        
        return JsonResponse({
            'success': True,
            'is_following': is_following,
            'follower_count': user_to_toggle.profile.followers.count()
        })
    return JsonResponse({'success': False, 'error': 'Cannot follow yourself'})

@login_required
def following_list(request, username):
    user = get_object_or_404(User, username=username)
    following = user.following.all()
    return render(request, 'following_list.html', {'following': following})

@login_required
def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    followers = user.profile.followers.all()
    return render(request, 'followers_list.html', {'followers': followers})