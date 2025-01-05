from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import EmailAuthenticationForm, EmailSignUpForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Profile
from .forms import ProfileImageForm
from django.contrib.auth.models import User
from django.template.defaultfilters import date


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
        'next': request.GET.get('next', 'recipes:explore')
    })


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
        })
    return JsonResponse({'success': False, 'error': 'Cannot follow yourself'})


@login_required
def profile_view(request, username):
    user = User.objects.get(username=username)
    image_form = ProfileImageForm()
    context = {
        'chef': user.profile,
        'username': user.username,
        'user_id': user.id,
        'date_joined': date(request.user.date_joined, 'd.m.Y'),
        'chef_level': user.profile.get_chef_level_display(),
        'following': user.profile.following.all(),
        'follower': user.follower.all(),
        'is_following': user.follower.filter(id=request.user.id).exists(),
        'image_form': image_form,
    }
    return render(request, 'chefs/profile.html', context=context)


@login_required
def upload_profile_image(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    
    # Check if user has permission to modify this profile
    if profile.user != request.user:
        messages.error(request, "You don't have permission to modify this profile.")
        return redirect('chefs:profile',  username=profile.user.username)
    
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.chef = profile
            image.alt_text = request.FILES['image'].name
            image.save()
            
            messages.success(request, 'Image uploaded successfully!')
            return redirect('chefs:profile',  username=profile.user.username)
    else:
        form = ProfileImageForm()
    
    return redirect('chefs:profile',  username=profile.user.username)