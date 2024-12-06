from rest_framework import serializers
from recipes.models import Recipe, RecipeComponent, ComponentIngredient, RecipeInstruction

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'difficulty', 
                 'time_active', 'time_inactive', 'default_servings',
                 'storage', 'cost', 'spiciness', 'created_by']

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeComponent
        fields = ['recipe', 'name']

class InstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeInstruction
        fields = ['recipe', 'number', 'headline', 'description']