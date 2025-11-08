from rest_framework import serializers
from recipes.models import (
    Recipe, RecipeTime, RecipeComponent, ComponentIngredient,
    RecipeInstruction, RecipeTip, RecipeRating, RecipeImage,
    Equipment, Diet, Hashtag, Ingredient, Language
)

from django.contrib.auth.models import User

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['code', 'name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name']


class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = ['id', 'name']


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['id', 'name']


class RecipeTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTime
        fields = ['name', 'value']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'category']


class ComponentIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    
    class Meta:
        model = ComponentIngredient
        fields = ['ingredient', 'amount', 'unit', 'note', 'item']


class RecipeComponentSerializer(serializers.ModelSerializer):
    ingredients = ComponentIngredientSerializer(many=True, read_only=True)
    
    class Meta:
        model = RecipeComponent
        fields = ['id', 'name', 'ingredients']


class RecipeInstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeInstruction
        fields = ['number', 'headline', 'description']


class RecipeTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTip
        fields = ['tip']


class RecipeRatingSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = RecipeRating
        fields = ['rating', 'author', 'created_at']


class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeImage
        fields = ['image', 'alt_text']


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    language = LanguageSerializer(read_only=True)
    equipments = EquipmentSerializer(many=True, read_only=True)
    diets = DietSerializer(many=True, read_only=True)
    hashtags = HashtagSerializer(many=True, read_only=True)
    times = RecipeTimeSerializer(many=True, read_only=True)
    components = RecipeComponentSerializer(many=True, read_only=True)
    instruction_steps = RecipeInstructionSerializer(many=True, read_only=True)
    tips = RecipeTipSerializer(many=True, read_only=True)
    ratings = RecipeRatingSerializer(many=True, read_only=True)
    image = RecipeImageSerializer(read_only=True)
    time_total = serializers.IntegerField(read_only=True)
    
    # Human-readable choices
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    spiciness_display = serializers.CharField(source='get_spiciness_display', read_only=True)
    cost_display = serializers.CharField(source='get_cost_display', read_only=True)
    
    # Average rating
    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'difficulty',
            'difficulty_display',
            'default_servings',
            'storage',
            'cost',
            'cost_display',
            'spiciness',
            'spiciness_display',
            'time_total',
            'author',
            'language',
            'created_at',
            'updated_at',
            'equipments',
            'diets',
            'hashtags',
            'times',
            'components',
            'instruction_steps',
            'tips',
            'ratings',
            'average_rating',
            'rating_count',
            'image',
        ]
    
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings:
            return round(sum(r.rating for r in ratings) / len(ratings), 2)
        return None
    
    def get_rating_count(self, obj):
        return obj.ratings.count()