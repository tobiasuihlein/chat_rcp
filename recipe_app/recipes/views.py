from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from generator.utils.helpers import sort_previews
from generator.services import *
from django.db.models import Avg, Count, Exists, OuterRef, Value, Subquery
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


def recipe_detail(request, slug):
    recipe = get_object_or_404(Recipe.objects.annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings__rating'),
            is_saved=Exists(
                SavedRecipe.objects.filter(recipe=OuterRef('pk'), user=request.user)
            ) if request.user.is_authenticated else Value(False),
            user_rating=Subquery(RecipeRating.objects.filter(recipe=OuterRef('pk'), author=request.user).values('rating')[:1]
            ) if request.user.is_authenticated else Value(None),
            rating_id=Subquery(RecipeRating.objects.filter(recipe=OuterRef('pk'), author=request.user).values('id')[:1]
            ) if request.user.is_authenticated else Value(None),
        ),
        slug=slug
    )
    return render(request, 'recipes/detail.html', {'recipe_id': recipe.id, 'recipe': recipe})


@login_required(login_url='chefs:login')
def explore(request):
    if request.method == "POST":
        search_input = request.POST.get("search-input")
        base_query = Recipe.search.advanced_search(search_input)
    else:
        base_query = Recipe.objects.all().order_by('-created_at')

    recipes = base_query.annotate(
        avg_rating=models.Subquery(
            RecipeRating.objects.filter(recipe=models.OuterRef('id'))
            .values('recipe')
            .annotate(avg=Avg('rating'))
            .values('avg')[:1]
        ),
        rating_count=models.Subquery(
            RecipeRating.objects.filter(recipe=models.OuterRef('id'))
            .values('recipe')
            .annotate(count=Count('rating', distinct=True))
            .values('count')[:1]
        ),
        is_saved=Exists(
            SavedRecipe.objects.filter(recipe=OuterRef('pk'), user=request.user)
        )
    )

    # Only order by search_rank if we're searching
    if request.method == "POST" and request.POST.get("search-input"):
        recipes = recipes.order_by('-search_rank', 'title')
    
    categories = RecipeCategory.objects.all()
    cuisine_types = CuisineType.objects.all()

    return render(request, 'recipes/list.html', {
        'recipes': recipes, 
        'categories': categories, 
        'cuisine_types': cuisine_types
    })


@login_required(login_url='chefs:login')
def library(request):
    if request.method == "POST":
        search_input = request.POST.get("search-input")
        base_query = Recipe.search.advanced_search(search_input)
        print(f"search: {search_input}")
    else:
        base_query = Recipe.objects.all()
    recipes = base_query.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings__rating'),
        is_saved=Exists(
            SavedRecipe.objects.filter(recipe=OuterRef('pk'), user=request.user)
        ) if request.user.is_authenticated else Value(False)
    ).filter(favorites__user=request.user).order_by('-created_at')
    return render(request, 'recipes/list.html', {'recipes': recipes})


@login_required(login_url='chefs:login')
def generate(request):
    return render(request, 'recipes/generate.html')


@login_required(login_url='chefs:login')
def create_recipe_with_text(request):
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
        return redirect('recipes:create_with_text')

    recipe_form = RecipeForm()
    return render(request, 'recipes/create_with_text.html', {'recipe_form': recipe_form})


@login_required(login_url='chefs:login')
def create_recipe_with_image(request):
    if request.method == 'POST':
        try:
            if 'photo' not in request.FILES:
                return JsonResponse({
                    'error': 'No photo provided'
                }, status=400)
            
            photo = request.FILES['photo']
            
            recipe_generator = PixtralHandler()

            prompt = create_recipe_prompt_for_image()
            logger.info("Prompt created successfully")

            try:
                recipe = recipe_generator.process_image(photo, prompt)
                logger.info("Recipe generation completed")
            except Exception as e:
                logger.error(f"Recipe generation failed: {str(e)}")
                raise

            print(recipe)

            logger.info("Starting database save")
            recipe_object = recipe_to_database(recipe["recipe"][0])
            recipe_object.author = request.user
            recipe_object.save()
            logger.info(f"Recipe saved with ID: {recipe_object.pk}")

            return redirect('recipes:detail', slug=recipe_object.slug)
            
        except Exception as e:
            print("Error:", str(e))  # Debug logging
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return render(request, 'recipes/create_with_image.html')


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
def new_recipe_by_text(request):

    if request.method == "POST":
        try:
            logger.info("Starting recipe generation process by description")
            user_input = request.POST.get("recipe-description")

            recipe_generator = MistralRecipeGeneratorService()
            
            prompt = create_recipe_prompt_by_description(user_input)
            print(prompt)
            logger.info("Prompt created successfully")

            try:
                recipe = recipe_generator.get_recipe_from_Mistral(prompt)
                logger.info("Recipe generation completed")
            except Exception as e:
                logger.error(f"Recipe generation failed: {str(e)}")
                raise

            logger.info("Starting database save")
            recipe_object = recipe_to_database(recipe["recipe"][0])
            recipe_object.author = request.user
            recipe_object.save()
            logger.info(f"Recipe saved with ID: {recipe_object.pk}")

            return redirect('recipes:detail', slug=recipe_object.slug)
        
        except Exception as e:
            logger.error(f"Detailed error in recipe generation: {str(e)}", exc_info=True)
            messages.error(request, "Sorry, something went wrong while generating your recipe. Please try again.")
            return redirect('recipes:create_with_text')
        
    return redirect('recipes:create_with_text')


@login_required(login_url='chefs:login')
def recipe_generated(request):
    if request.method == "POST":
        try:
            logger.info("Starting recipe generation process by preview")
            
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

            return redirect('recipes:detail', slug=recipe_object.slug)
            
        except Exception as e:
            logger.error(f"Detailed error in recipe generation: {str(e)}", exc_info=True)
            messages.error(request, "Sorry, something went wrong while generating your recipe. Please try again.")
            return redirect('recipes:generate')
    
    return redirect('recipes:generate')


@login_required
def rate_recipe(request, recipe_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        recipe = Recipe.objects.get(pk=recipe_id)
        data = json.loads(request.body)
        rating = int(data.get('rating'))
        
        if not 1 <= rating <= 5:
            return JsonResponse({'error': 'Invalid rating'}, status=400)
        
        # Update or create rating
        rating_obj, created = RecipeRating.objects.update_or_create(
            recipe=recipe,
            author=request.user,
            defaults={'rating': rating}
        )
        
        # Get updated stats
        avg_rating = recipe.ratings.aggregate(Avg('rating'))['rating__avg']
        rating_count = recipe.ratings.count()
        
        return JsonResponse({
            'avg_rating': round(avg_rating, 1),
            'rating_count': rating_count
        })
        
    except Recipe.DoesNotExist:
        return JsonResponse({'error': 'Recipe not found'}, status=404)
    except (ValueError, KeyError):
        return JsonResponse({'error': 'Invalid data'}, status=400)