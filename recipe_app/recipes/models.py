from django.db import models


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
        BEGINNER = 1, 'Easy'
        ADVANCED = 2, 'Advanced'
        EXPERT = 3, 'Expert'

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
    time_active = models.IntegerField()
    time_inactive = models.IntegerField()
    default_servings = models.IntegerField()
    storage = models.TextField()
    cuisine_types = models.ManyToManyField(CuisineType, related_name="recipes")
    cuisine_subtypes = models.ManyToManyField(CuisineSubtype, related_name="recipes")
    category = models.ForeignKey(RecipeCategory, on_delete=models.SET_NULL, related_name="recipes", null=True)
    diets = models.ManyToManyField(Diet, related_name="recipes")
    cooking_methods = models.ManyToManyField(CookingMethod, related_name="recipes")
    cost = models.IntegerField(choices=Cost.choices, default=Cost.UNKNOWN)
    spiciness = models.IntegerField(choices=Spiciness.choices, default=Spiciness.UNKNOWN)
    beverage_recommendation = models.ForeignKey(Beverage, on_delete=models.SET_NULL, null=True)
    hashtags = models.ManyToManyField(Hashtag, related_name="recipes")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    created_by = models.CharField(max_length=255, default="Claude")
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def time_total(self):
        return self.time_active + self.time_inactive

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created_at']


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


class RecipeMainIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="recipes_main")
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    unit = models.CharField(max_length=25)
    note = models.CharField(max_length=255)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="main_ingredients")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.ingredient.name
    
    class Meta:
        ordering = ['recipe', 'ingredient']


class RecipeAdditionalIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="recipes_additional")
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    unit = models.CharField(max_length=25)
    note = models.CharField(max_length=255)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="additional_ingredients")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.ingredient.name
    
    class Meta:
        ordering = ['recipe', 'ingredient']


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


