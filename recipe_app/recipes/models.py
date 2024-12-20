from django.db import models, connection
from django.utils.text import slugify
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat

class RecipeSearchManager(models.Manager):
    def advanced_search(self, query):
        search_terms = query.split()
        q_objects = Q()
        
        for term in search_terms:
            q_objects |= (
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(components__ingredients__ingredient__name__icontains=term) |
                Q(cuisine_types__name__icontains=term) |
                Q(category__name__icontains=term) |
                Q(diets__name__icontains=term) |
                Q(hashtags__name__icontains=term) |
                Q(instruction_steps__description__icontains=term) |
                Q(cooking_methods__name__icontains=term) |
                Q(tips__tip__icontains=term) |
                Q(author__username__icontains=term)
            )

        # Get distinct recipe IDs in a subquery
        subquery = self.get_queryset().filter(q_objects).values('id').distinct()
        
        # Use those IDs to get the final recipes with ranking
        base_qs = self.get_queryset().filter(id__in=subquery)

        # Add search ranking as a subquery annotation
        rank_case = models.Case(
            models.When(title__icontains=query, then=Value(5)),
            models.When(components__ingredients__ingredient__name__icontains=query, then=Value(4)),
            models.When(components__name__icontains=query, then=Value(4)),
            models.When(description__icontains=query, then=Value(2)),
            models.When(hashtags__name__icontains=query, then=Value(2)),
            models.When(diets__name__icontains=query, then=Value(2)),
            default=Value(1),
            output_field=models.IntegerField(),
        )

        return base_qs.annotate(
            search_rank=models.Subquery(
                base_qs.filter(id=models.OuterRef('id'))
                .annotate(rank=rank_case)
                .values('rank')[:1]
            )
        )


class Language(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.code


class RecipeCategory(models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Diet(models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class CookingMethod(models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    

class CuisineType(models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=100)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name  


class BeverageType(models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    

class Beverage(models.Model):
    name = models.CharField(max_length=50)
    type = models.ForeignKey(BeverageType, on_delete=models.SET_NULL, null=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    

class Hashtag(models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):

    class Difficulty(models.IntegerChoices):
        BEGINNER = 1, 'Simpel'
        ADVANCED = 2, 'Fortgeschritten'
        EXPERT = 3, 'Anspruchsvoll'

    class Spiciness(models.IntegerChoices):
        NOT_SPICY = 0, 'Nicht Scharf'
        MILD = 1, 'Leicht scharf'
        MEDIUM = 2, 'Mittelscharf'
        HOT = 3, 'Sehr scharf'

    class Cost(models.IntegerChoices):
        UNKNOWN = 0, 'Not Specified'
        BUDGET = 1, 'Günstig'
        MODERATE = 2, 'Mittel'
        EXPENSIVE = 3, 'Teuer'


    title = models.CharField(verbose_name="Titel", max_length=255)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(verbose_name="Kurzbeschreibung", blank=True, null=True)
    difficulty = models.IntegerField(verbose_name="Schwierigkeitsgrad", choices=Difficulty.choices)
    default_servings = models.IntegerField(verbose_name="Portionen")
    storage = models.TextField(verbose_name="Aufbewahrung", blank=True, null=True)
    cuisine_types = models.ManyToManyField(verbose_name="Küche", to=CuisineType, related_name="recipes", blank=True)
    equipments = models.ManyToManyField(verbose_name="Ausrüstung", to=Equipment, related_name="recipes", blank=True)
    category = models.ForeignKey(verbose_name="Kategorie", to=RecipeCategory, on_delete=models.SET_NULL, related_name="recipes", null=True)
    diets = models.ManyToManyField(verbose_name="Ernährungsweise", to=Diet, related_name="recipes", blank=True)
    cooking_methods = models.ManyToManyField(verbose_name="Techniken", to=CookingMethod, related_name="recipes", blank=True)
    cost = models.IntegerField(verbose_name="Kosten", choices=Cost.choices, default=Cost.UNKNOWN)
    spiciness = models.IntegerField(verbose_name="Schärfe", choices=Spiciness.choices, default=Spiciness.NOT_SPICY)
    beverage = models.ForeignKey(verbose_name="Getränkeempfehlung", to=Beverage, on_delete=models.SET_NULL, blank=True, null=True)
    hashtags = models.ManyToManyField(verbose_name="Hashtags", to=Hashtag, related_name="recipes", blank=True)
    language = models.ForeignKey(verbose_name="Sprache", to=Language, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(verbose_name="Autor", to=User, on_delete=models.SET_NULL, related_name="recipes", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    search = RecipeSearchManager()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            
            while Recipe.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("recipes:detail", kwargs={"slug": self.slug})

    @property
    def time_total(self):
        result = self.times.aggregate(total_time=models.Sum('value'))
        total = result['total_time']
        return total or 0

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class RecipeTime(models.Model):
    name = models.CharField(max_length=50)
    value = models.IntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='times')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['recipe']


class IngredientCategory(models.Model):
    name = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(IngredientCategory, on_delete=models.SET_NULL, null=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['category']


class RecipeComponent(models.Model):
    name = models.CharField(max_length=100)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="components")


class ComponentIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="commponents")
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    unit = models.CharField(max_length=25)
    note = models.CharField(max_length=50)
    recipe_component = models.ForeignKey(RecipeComponent, on_delete=models.CASCADE, related_name="ingredients")
    item = models.CharField(max_length=50)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.ingredient.name
    
    class Meta:
        ordering = ['recipe_component', 'ingredient']


class RecipeInstruction(models.Model):
    number = models.IntegerField()
    headline = models.CharField(max_length=50)
    description = models.TextField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="instruction_steps")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.headline
    
    class Meta:
        ordering = ['recipe', 'number']


class RecipeTip(models.Model):
    tip = models.TextField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="tips")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.tip
    
    class Meta:
        ordering = ['recipe']


class RecipeRating(models.Model):
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ratings")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="ratings")
    created_at = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['recipe', 'author'], name='unique_rating')]

    def __str__(self):
        return f"{self.recipe.title} {self.rating}"


class ImageStorage(FileSystemStorage):
    def get_valid_name(self, name):
        basename, ext = os.path.splitext(name)
        return f"{basename}_{hash(name)}{ext}"


class RecipeImage(models.Model):
    image = models.ImageField(upload_to='recipe_images/', storage = ImageStorage(), max_length=500, blank=True, null=True)
    alt_text = models.CharField(max_length=100, blank=True, default="recipe image")
    upload_datetime = models.DateTimeField(auto_now_add=True)
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE, related_name="image")

    class Meta:
        ordering = ['-upload_datetime']

    def __str__(self):
        return f"Image for {self.recipe.title}"
    
    def save(self, *args, **kwargs):
        if self.recipe:
            RecipeImage.objects.filter(recipe=self.recipe).delete()
        super().save(*args, **kwargs)

    @property
    def filename(self):
        return os.path.basename(self.image.name)


class SavedRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="favorites")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipe} saved by {self.user}"
    

class ShoppingRecipes(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="shopping_lists")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shopping_recipes")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipe} in shopping list of {self.user}"