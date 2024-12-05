from django.shortcuts import render, redirect
from django.urls import reverse
from generator.utils.helpers import sort_previews
from generator.services import RecipeGeneratorService

def previews(request):

    if request.method == "POST":
    
        ingredients = request.POST.get("ingredients-input").split(',')
        staples = [""]

        generator = RecipeGeneratorService()
    
        prompt = generator.create_previews_prompt(ingredients, staples)
        previews = generator.get_previews_from_LLM(prompt)
    
        previews["recipes"] = sort_previews(previews["recipes"])

        context = {"recipe_previews": previews["recipes"], "ingredients": ingredients}
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
            generator.recipe_to_database(recipe["recipe"][0])
            print(recipe["recipe"][0])
            context = {"recipe": recipe["recipe"][0]}
            return render(request, 'recipes/recipe.html', context=context)
        except Exception as e:
            print(f"Error: {e}")
            return redirect('recipes:home')
    
    return redirect('recipes:home')