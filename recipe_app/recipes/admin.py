from django.contrib import admin
from .models import *

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'beverage_recommendation', 'get_cuisine_types', 'created_by')

    def get_cuisine_types(self, obj):
        return ", ".join([cuisine_type.name for cuisine_type in obj.cuisine_types.all()])

@admin.register(IngredientCategory)
class IngredientCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'language')

@admin.register(RecipeCategory)
class RecipeCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Diet)
class DietAdmin(admin.ModelAdmin):
    pass

@admin.register(CookingMethod)
class CookingMethodAdmin(admin.ModelAdmin):
    pass

@admin.register(Beverage)
class BeverageAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')