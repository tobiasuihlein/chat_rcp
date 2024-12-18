from rest_framework import serializers
from recipes.models import Recipe, RecipeComponent, RecipeInstruction, SavedRecipe, RecipeRating, RecipeCategory

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'difficulty', 'default_servings',
                 'storage', 'cost', 'spiciness', 'author']

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeComponent
        fields = ['recipe', 'name']

class InstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeInstruction
        fields = ['recipe', 'number', 'headline', 'description']


class SavedRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedRecipe
        fields = ['recipe', 'user']


class RecipeRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeRating
        fields = ['id', 'rating', 'recipe', 'author']


class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = ['id', 'name']