from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from generator.utils.helpers import sort_previews
from generator.services import *
from django.db.models import Avg, Count, Exists, OuterRef, Value
from .models import *
from .forms import *

import logging
logger = logging.getLogger(__name__)

from django.http import JsonResponse

@login_required(login_url='chefs:login')
def toggle_save_recipe(request, recipe_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    saved = SavedRecipe.objects.filter(recipe=recipe, user=request.user)
    
    if saved.exists():
        saved.delete()
        return JsonResponse({'status': 'unsaved'})
    else:
        SavedRecipe.objects.create(recipe=recipe, user=request.user)
        return JsonResponse({'status': 'saved'})


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.user.is_authenticated:
        recipe_saved_by_user = SavedRecipe.objects.filter(recipe=pk, user=request.user).exists()
    else:
        recipe_saved_by_user = False
    return render(request, 'recipes/detail.html', {'recipe_id': recipe.id, 'recipe': recipe, 'recipe_saved_by_user': recipe_saved_by_user})


@login_required(login_url='chefs:login')
def explore(request):
    recipes = Recipe.objects.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings__rating'),
        is_saved=Exists(
            SavedRecipe.objects.filter(recipe=OuterRef('pk'), user=request.user)
        ) if request.user.is_authenticated else Value(False)
    ).order_by('-created_at')
    return render(request, 'recipes/list.html', {'recipes': recipes})


@login_required(login_url='chefs:login')
def library(request):
    recipes = Recipe.objects.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings__rating'),
        is_saved=Exists(
            SavedRecipe.objects.filter(recipe=OuterRef('pk'), user=request.user)
        ) if request.user.is_authenticated else Value(False)
    ).filter(favourites__user=request.user).order_by('-created_at')
    return render(request, 'recipes/list.html', {'recipes': recipes})


@login_required(login_url='chefs:login')
def generate(request):
    return render(request, 'recipes/generate.html')


@login_required(login_url='chefs:login')
def write(request):
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST)
        if recipe_form.is_valid():
            recipe_object = recipe_form.save()
            recipe_object.author = request.user
            language_object, _ = Language.objects.get_or_create(code='de')
            recipe_object.language = language_object
            recipe_object.save()
            messages.info(request, "Rezept gespeichert!")
            return render(request, 'recipes/detail.html', {'recipe_id': recipe_object.id, 'recipe': recipe_object, 'recipe_saved_by_user': False})
        return redirect('recipes:write')

    recipe_form = RecipeForm()
    return render(request, 'recipes/write.html', {'recipe_form': recipe_form})


@login_required(login_url='chefs:login')
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


@login_required(login_url='chefs:login')
def recipe_generated(request):
    if request.method == "POST":
        try:
            logger.info("Starting recipe generation process")
            
            recipe_generator = MistralRecipeGeneratorService()
            recipe_dict = request.POST.dict()
            
            prompt = create_recipe_prompt_by_preview(recipe_dict)
            logger.info("Prompt created successfully")
            
            try:
                recipe = recipe_generator.get_recipe_from_Mistral(prompt)
                logger.info("Recipe generation completed")
            except Exception as e:
                logger.error(f"Recipe generation failed: {str(e)}")
                raise

            logger.info("Starting database save")
            recipe_object = recipe_to_database(recipe["recipe"][0])
            recipe_object.author = User.objects.get(username="MistralAI")
            recipe_object.save()
            logger.info(f"Recipe saved with ID: {recipe_object.pk}")

            return redirect('recipes:detail', pk=recipe_object.pk)
            
        except Exception as e:
            logger.error(f"Detailed error in recipe generation: {str(e)}", exc_info=True)
            messages.error(request, "Sorry, something went wrong while generating your recipe. Please try again.")
            return redirect('recipes:generate')
    
    return redirect('recipes:generate')