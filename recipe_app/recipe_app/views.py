from django.shortcuts import render


def home(request):
    return render(request, 'recipe_app/home.html')