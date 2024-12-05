from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from . import translation
from .models import *

@admin.register(Recipe)
class RecipeAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'difficulty', 'category', 'get_cuisine_types', 'spiciness', 'created_at', 'created_by')

    def get_cuisine_types(self, obj):
        return ", ".join([cuisine_type.name for cuisine_type in obj.cuisine_types.all()])

@admin.register(IngredientCategory)
class IngredientCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'type', 'recipe')

@admin.register(RecipeInstruction)
class RecipeInstructionAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'number', 'headline')

@admin.register(RecipeCategory)
class RecipeCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Diet)
class DietAdmin(admin.ModelAdmin):
    pass

@admin.register(CookingMethod)
class CookingMethodAdmin(admin.ModelAdmin):
    pass