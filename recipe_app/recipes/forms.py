from django import forms
from .models import Recipe

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'difficulty', 'default_servings', 'storage', 'diets', 'cost', 'spiciness', 'hashtags']