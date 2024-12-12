from django import forms
from .models import Recipe

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'difficulty', 'time_active', 'time_inactive',
                  'default_servings', 'storage', 'cuisine_types',
                  'category', 'diets', 'cooking_methods', 'cost', 'spiciness',
                  'beverage', 'hashtags']