from modeltranslation.translator import register, TranslationOptions
from .models import *

@register(Recipe)
class RecipeTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'storage')

@register(RecipeCategory)
class RecipeCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Diet)
class DietTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(CookingMethod)
class CookingMethodTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(CuisineType)
class CuisineTypeTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(CuisineSubtype)
class CuisineSubtypeTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Hashtag)
class HashtagTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(IngredientCategory)
class IngredientCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Ingredient)
class IngredientTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(RecipeInstruction)
class RecipeInstructionTranslationOptions(TranslationOptions):
    fields = ('headline', 'description')