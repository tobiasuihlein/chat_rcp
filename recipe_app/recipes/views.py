from django.shortcuts import render, redirect, get_object_or_404 
from django.urls import reverse
from generator.utils.helpers import sort_previews
from generator.services import RecipeGeneratorService
from .models import *

def previews(request):

    if request.method == "POST":
    
        user_input = request.POST.get("ingredients-input")

        generator = RecipeGeneratorService()
    
        prompt = generator.create_previews_prompt(user_input)
        previews = generator.get_previews_from_LLM(prompt)
    
        previews["recipes"] = sort_previews(previews["recipes"])

        for recipe in previews["recipes"]:
            print(recipe)

        context = {"recipe_previews": previews["recipes"], "difficulty_choices": Recipe.Difficulty.choices}
        return render(request, 'recipes/previews.html', context=context)
    
    return render(request, 'recipes/index.html')


def home(request):
    return render(request, 'recipes/index.html')


def recipe_generated(request):

    if request.method == "POST":
        try:
            generator = RecipeGeneratorService()
            recipe_dict = request.POST.dict()
            prompt = generator.create_recipe_prompt_by_preview(recipe_dict)
            recipe = generator.get_recipe_from_LLM(prompt)
            recipe_object = generator.recipe_to_database(recipe["recipe"][0])
            print(recipe["recipe"][0])
            return redirect('recipes:detail', pk=recipe_object.pk)
            # context = {"recipe": recipe["recipe"][0], "difficulty_choices": Recipe.Difficulty.choices}
            # return render(request, 'recipes/recipe-generated.html', context=context)
        except Exception as e:
            print(f"Error: {e}")
            return redirect('recipes:home')
    
    return redirect('recipes:home')


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    print(recipe)
    return render(request, 'recipes/detail.html', {'recipe': recipe})


def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/list.html', {'recipes': recipes})