from django import forms
from .models import Recipe, RecipeImage


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'difficulty', 'default_servings', 'storage', 'diets', 'cost', 'spiciness', 'hashtags']


class RecipeImageForm(forms.ModelForm):
    class Meta:
        model = RecipeImage
        fields = ['image']