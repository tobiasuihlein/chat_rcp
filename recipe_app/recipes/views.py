from django.shortcuts import render, redirect, get_object_or_404 
from django.urls import reverse
from generator.utils.helpers import sort_previews
from generator.services import *
from .models import *


import requests
from concurrent.futures import ThreadPoolExecutor
from django.core.files.base import ContentFile

def login(request):

    return render(request, 'recipes/login.html')


def previews(request):

    if request.method == "POST":
    
        user_input = request.POST.get("ingredients-input")

        recipe_generator = ClaudeRecipeGeneratorService()
    
        prompt = create_previews_prompt(user_input)
        previews = recipe_generator.get_previews_from_Claude(prompt)
    
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
            # recipe_generator = ClaudeRecipeGeneratorService()
            recipe_generator = MistralRecipeGeneratorService()
            author = "Mistral AI"
            image_generator = ImageGeneratorService()
            recipe_dict = request.POST.dict()
            
            # Create prompt first since it's needed for recipe generation
            prompt = create_recipe_prompt_by_preview(recipe_dict)
            
            # Use ThreadPoolExecutor to run API calls concurrently
            with ThreadPoolExecutor() as executor:
                # recipe_future = executor.submit(recipe_generator.get_recipe_from_Claude, prompt)
                recipe_future = executor.submit(recipe_generator.get_recipe_from_Mistral, prompt)
                image_future = executor.submit(image_generator.get_image, recipe_dict)
                
                recipe = recipe_future.result()
                image_url = image_future.result()

            # # Download image
            # response = requests.get(image_url)
            # image_content = response.content
            
            # Save recipe to database
            recipe_object = recipe_to_database(recipe["recipe"][0])
            recipe_object.author = author
            recipe_object.save()
            
            # # Save image
            # recipe_image = RecipeImage(
            #     recipe=recipe_object,
            #     alt_text=f"Image for {recipe_object.title}"
            # )
            # recipe_image.image.save(
            #     f"recipe_{recipe_object.pk}.png",
            #     ContentFile(image_content),
            #     save=True
            # )

            return redirect('recipes:detail', pk=recipe_object.pk)
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return redirect('recipes:home')
    
    return redirect('recipes:home')


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    print(recipe)
    return render(request, 'recipes/detail.html', {'recipe': recipe})


def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/list.html', {'recipes': recipes})