from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import EmailAuthenticationForm, EmailSignUpForm

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