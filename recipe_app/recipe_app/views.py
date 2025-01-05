from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'recipe_app/home.html')

def impressum(request):
    return render(request, 'recipe_app/impressum.html')

def agb(request):
    return render(request, 'recipe_app/agb.html')

def privacy(request):
    return render(request, 'recipe_app/privacy.html')