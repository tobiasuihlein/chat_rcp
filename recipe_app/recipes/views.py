from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from generator.utils.helpers import sort_previews
from generator.services import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import BooleanField, IntegerField
from django.db.models import Avg, Count, Exists, OuterRef, Value, Subquery
from .models import *
from .forms import *
from .services import annotate_recipes
import logging

from recipes.templatetags.number_converter import to_fraction


logger = logging.getLogger(__name__)


from django.db.models import Sum, F
from itertools import groupby
from operator import itemgetter


### Shopping views ###

@login_required
def shopping_list(request):
    shopping_list = ShoppingRecipe.objects.filter(user=request.user)
    recipe_ids = shopping_list.values_list('recipe', flat=True)

    all_items = []
    for recipe_id in recipe_ids:
        items = ComponentIngredient.objects.filter(
            recipe_component__recipe_id=recipe_id
        ).select_related(
            'ingredient',
            'ingredient__category'
        ).values(
            'ingredient__name',
            'ingredient__category__name',
            'unit',
            'amount',
            'ingredient_id'
        )
        all_items.extend(items)

    all_items = sorted(all_items, 
                      key=lambda x: (x['ingredient__category__name'], 
                                   x['ingredient__name'], 
                                   x['unit']))


    # Convert to list and aggregate amounts by ingredient
    aggregated_items = []
    for ingredient_name, group in groupby(all_items, key=lambda x: x['ingredient__name']):
        group_list = list(group)
        # Group by unit and sum amounts
        unit_amounts = {}
        category_name = group_list[0]['ingredient__category__name']
        ingredient_id = group_list[0]['ingredient_id']
        
        for item in group_list:
            unit = item['unit']
            if unit in unit_amounts:
                unit_amounts[unit] += item['amount']
            else:
                unit_amounts[unit] = item['amount']
        
        # Create combined amount string
        amount_parts = []
        for unit, amount in unit_amounts.items():
            fraction_amount = to_fraction(amount)
            amount_parts.append(f"{fraction_amount} {unit}")
        amount_string = " + ".join(amount_parts)

        aggregated_items.append({
            'ingredient_name': ingredient_name,
            'category_name': category_name,
            'amount': amount_string,
            'ingredient_id': ingredient_id
        })

    return render(request, 'recipes/shopping_list.html', {'items': aggregated_items, 'recipes': shopping_list})


### Detail view ###

def recipe_detail(request, slug):
    recipe = get_object_or_404(Recipe.objects.annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings__rating'),
            is_favorite=Exists(
                SavedRecipe.objects.filter(recipe=OuterRef('pk'), user=request.user)
            ) if request.user and request.user.is_authenticated else Value(False, output_field=BooleanField()),
            user_rating=Subquery(RecipeRating.objects.filter(recipe=OuterRef('pk'), author=request.user).values('rating')[:1]
            ) if request.user and request.user.is_authenticated else Value(None, output_field=IntegerField(null=True)),
            rating_id=Subquery(RecipeRating.objects.filter(recipe=OuterRef('pk'), author=request.user).values('id')[:1]
            ) if request.user and request.user.is_authenticated else Value(None, output_field=IntegerField(null=True)),
        ),
        slug=slug
    )
    image_form = RecipeImageForm()
    return render(request, 'recipes/detail.html', {'recipe_id': recipe.id, 'recipe': recipe, 'image_form': image_form})


### List views ###

class RecipeListBaseView(ListView):
    model = Recipe
    template_name = 'recipes/list.html'
    context_object_name = 'recipes'
    
    def get_base_queryset(self):
        raise NotImplementedError
    
    def get_search_input(self):
        return self.request.GET.get("search-input") 
    
    def apply_search(self, queryset, search_input):
        if search_input:
            class FilteredSearchManager(RecipeSearchManager):
                def get_queryset(self):
                    return queryset
            return FilteredSearchManager().advanced_search(search_input)
        return queryset
    
    def sort_recipes(self, queryset):
        raise NotImplementedError

    def apply_annotations(self, queryset):
        return annotate_recipes(queryset, self.request.user)

    def get_queryset(self):
        queryset = self.get_base_queryset()
        search_input = self.get_search_input()
        queryset = self.apply_search(queryset, search_input)
        
        if search_input:
            queryset = queryset.order_by('-search_rank', 'title')
        else:
            queryset = self.sort_recipes(queryset)
            
        return self.apply_annotations(queryset)[:25]

class ExploreView(RecipeListBaseView):
    def get_base_queryset(self):
        return Recipe.objects.all()
    
    def sort_recipes(self, queryset):
        return queryset.order_by('-created_at')

class LibraryView(RecipeListBaseView):
    def get_base_queryset(self):
        return Recipe.objects.filter(favorites__user=self.request.user)
    
    def sort_recipes(self, queryset):
        return queryset.order_by('-favorites__saved_at')
    
class AuthorRecipesView(RecipeListBaseView):
    def get_base_queryset(self):
        author = get_object_or_404(User, username=self.kwargs['author'])
        return Recipe.objects.filter(author=author)
    
    def sort_recipes(self, queryset):
        return queryset.order_by('-updated_at')


### Generate views ###

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
def edit_recipe(request, slug):
    if request.method == 'POST':
        recipe_form = RecipeForm()
        recipe_to_edit = get_object_or_404(Recipe, slug=slug)
        return render(request, 'recipes/create_with_text.html', {'recipe_form': recipe_form, 'recipe': recipe_to_edit})
    else:
        return redirect('recipes:library')




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

            logger.info("Starting database save")
            recipe_object = recipe_to_database(recipe["recipe"][0], recipe_id=None)
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

        context = {"recipe_previews": previews["recipes"], "difficulty_choices": Recipe.Difficulty.choices}
        return render(request, 'recipes/previews.html', context=context)
    
    return render(request, 'recipes/index.html')


@login_required(login_url='chefs:login')
def new_recipe_by_text(request):

    if request.method == "POST":
        try:
            logger.info("Starting recipe generation process by description")
            user_input = request.POST.get("recipe-description")
            recipe_id = request.POST.get("recipe_id")

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
            recipe_object = recipe_to_database(recipe["recipe"][0], recipe_id = recipe_id)
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


### Service views

def add_recipe_to_shopping_list(request, recipe_id):

    recipe = get_object_or_404(Recipe, pk=recipe_id)
    added_recipe = ShoppingRecipe.objects.create(recipe=recipe, user=request.user)

    if added_recipe:
        return JsonResponse({'status': 'recipe_added_to_shopping_list'})
    else:
        return JsonResponse({'status': 'request failed'})
    
def remove_recipe_from_shopping_list(request, shopping_recipe_id):

    shopping_recipe = get_object_or_404(ShoppingRecipe, pk=shopping_recipe_id)
    shopping_recipe.delete()

    return JsonResponse({'status': 'recipe_removed_from_shopping_list'})

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
    

@login_required
def upload_recipe_image(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    
    # Check if user has permission to modify this recipe
    if recipe.author != request.user:
        messages.error(request, "You don't have permission to modify this recipe.")
        return redirect('recipes:detail',  slug=slug)
    
    if request.method == 'POST':
        form = RecipeImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.recipe = recipe
            image.alt_text = request.FILES['image'].name
            image.save()
            
            messages.success(request, 'Image uploaded successfully!')
            return redirect('recipes:detail', slug=slug)
    else:
        form = RecipeImageForm()
    
    return render(request, 'recipes/upload_image.html', {
        'form': form,
        'recipe': recipe
    })