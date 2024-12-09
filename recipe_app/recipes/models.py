from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


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


class CuisineSubtype(models.Model):
    name = models.CharField(max_length=50)
    cuisine_type = models.ForeignKey(CuisineType, on_delete=models.SET_NULL, related_name="subtypes", null=True)
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
        UNKNOWN = 0, 'Not Specified'
        BEGINNER = 1, 'Einfach'
        INTERMEDIATE = 2, 'Fortgeschritten'
        ADVANCED = 3, 'Profi'
        EXPERT = 4, 'Sterneküche'

    class Spiciness(models.IntegerChoices):
        UNKNOWN = 0, 'Not Specified'
        NOT_SPICY = 1, 'Not Spicy'
        MILD = 2, 'Mild'
        MEDIUM = 3, 'Medium'
        HOT = 4, 'Hot'

    class Cost(models.IntegerChoices):
        UNKNOWN = 0, 'Not Specified'
        BUDGET = 1, 'Budget'
        MODERATE = 2, 'Moderate'
        MID_RANGE = 3, 'Mid-Range'
        PREMIUM = 4, 'Premium'


    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    difficulty = models.IntegerField(choices=Difficulty.choices, default=Difficulty.UNKNOWN)
    time_active = models.IntegerField()
    time_inactive = models.IntegerField(blank=True, default=0)
    default_servings = models.IntegerField()
    storage = models.TextField(blank=True, null=True)
    cuisine_types = models.ManyToManyField(CuisineType, related_name="recipes", blank=True)
    cuisine_subtypes = models.ManyToManyField(CuisineSubtype, related_name="recipes", blank=True)
    category = models.ForeignKey(RecipeCategory, on_delete=models.SET_NULL, related_name="recipes", null=True)
    diets = models.ManyToManyField(Diet, related_name="recipes", blank=True)
    cooking_methods = models.ManyToManyField(CookingMethod, related_name="recipes", blank=True)
    cost = models.IntegerField(choices=Cost.choices, default=Cost.UNKNOWN)
    spiciness = models.IntegerField(choices=Spiciness.choices, default=Spiciness.UNKNOWN)
    beverage_recommendation = models.ForeignKey(Beverage, on_delete=models.SET_NULL, blank=True, null=True)
    hashtags = models.ManyToManyField(Hashtag, related_name="recipes", blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    author = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def time_total(self):
        return self.time_active + self.time_inactive

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


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
