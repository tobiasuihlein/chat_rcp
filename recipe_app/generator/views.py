from django.shortcuts import render, redirect
from django.urls import reverse
from .utils.claude import *
from .utils.helpers import sort_previews

def previews(request):

    if request.method == "POST":
    
        ingredients = request.POST.get("ingredients-input").split(',')
        staples = [""]
    
        prompt = create_previews_prompt(ingredients, staples)
        previews = get_previews_from_claude(prompt)
    
        previews["recipes"] = sort_previews(previews["recipes"])

        context = {"recipe_previews": previews["recipes"], "ingredients": ingredients}
        return render(request, 'generator/previews.html', context=context)
    
    return render(request, 'generator/index.html')


def home(request):
    return render(request, 'generator/index.html')


def recipe(request):

    if request.method == "POST":
        try:
            recipe_dict = request.POST.dict()
            prompt = create_recipe_prompt(recipe_dict)
            recipe = get_recipe_from_claude(prompt)
            context = {"recipe": recipe["recipe"][0]}
            return render(request, 'generator/recipe.html', context=context)
        except Exception as e:
            print(f"Error: {e}")
            print("no recipe data provided")
            return redirect('generator:home')
    
    return redirect('generator:home')