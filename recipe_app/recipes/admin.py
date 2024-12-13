from django.contrib import admin
from django.utils.html import format_html
from .models import *

class RecipeImageInline(admin.StackedInline):
    model = RecipeImage
    max_num = 1
    min_num = 0
    can_delete = True
    readonly_fields = ['image_preview']
    fields = ['image', 'image_preview', 'alt_text']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;"/>',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(RecipeImage)
class RecipeImageAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'image_preview', 'upload_datetime']
    list_filter = ['upload_datetime', 'recipe']
    search_fields = ['recipe__name', 'alt_text']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;"/>',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'beverage', 'get_cuisine_types', 'author')
    inlines = [RecipeImageInline]

    def get_cuisine_types(self, obj):
        return ", ".join([cuisine_type.name for cuisine_type in obj.cuisine_types.all()])
    
@admin.register(RecipeComponent)
class RecipeComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'recipe', 'get_ingredients')

    def get_ingredients(self, obj):
        return ", ".join([ingredient.ingredient.name for ingredient in obj.ingredients.all()])

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

@admin.register(RecipeRating)
class RecipeRatingAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'rating', 'author', 'created_at', 'last_change')

@admin.register(SavedRecipe)
class SavedRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'saved_at')