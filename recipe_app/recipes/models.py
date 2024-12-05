from django.db import models


class RecipeCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Diet(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CookingMethod(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

class CuisineType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CuisineSubtype(models.Model):
    name = models.CharField(max_length=50)
    cuisine_type = models.ForeignKey(CuisineType, on_delete=models.SET_NULL, related_name="subtypes", null=True)

    def __str__(self):
        return self.name
    

class Hashtag(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):

    class Difficulty(models.IntegerChoices):
        UNKNOWN = 0, 'Not Specified'
        BEGINNER = 1, 'Beginner'
        INTERMEDIATE = 2, 'Intermediate'
        ADVANCED = 3, 'Advanced'
        EXPERT = 4, 'Expert'

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
    description = models.TextField()
    difficulty = models.IntegerField(choices=Difficulty.choices, default=Difficulty.UNKNOWN)
    time_total = models.IntegerField()
    time_preparation = models.IntegerField()
    time_cooking = models.IntegerField()
    default_servings = models.IntegerField()
    storage = models.TextField()
    cuisine_types = models.ManyToManyField(CuisineType, related_name="recipes")
    cuisine_subtypes = models.ManyToManyField(CuisineSubtype, related_name="recipes")
    category = models.ForeignKey(RecipeCategory, on_delete=models.SET_NULL, related_name="recipes", null=True)
    diets = models.ManyToManyField(Diet, related_name="recipes")
    cooking_methods = models.ManyToManyField(CookingMethod, related_name="recipes")
    cost = models.IntegerField(choices=Cost.choices, default=Cost.UNKNOWN)
    spiciness = models.IntegerField(choices=Spiciness.choices, default=Spiciness.UNKNOWN)
    hashtags = models.ManyToManyField(Hashtag, related_name="recipes")
    created_by = models.CharField(max_length=255, default="Claude")
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created_at']


class IngredientCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(IngredientCategory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['category']


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="recipes")
    type = models.CharField(max_length=25, choices=[('M', 'Main Ingredient'), ('A', 'Additional Ingredient')])
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    unit = models.CharField(max_length=25)
    note = models.CharField(max_length=255)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")

    def __str__(self):
        return self.ingredient.name
    
    class Meta:
        ordering = ['recipe', 'type', 'ingredient']


class RecipeInstruction(models.Model):
    number = models.IntegerField()
    headline = models.CharField(max_length=50)
    description = models.TextField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="instruction_steps")

    def __str__(self):
        return self.headline
    
    class Meta:
        ordering = ['recipe', 'number']

