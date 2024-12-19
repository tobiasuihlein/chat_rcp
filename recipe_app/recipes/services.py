from django.db.models import Avg, Count, Exists, OuterRef, Value
from .models import *

def annotate_recipes(recipes, user):
    annotated_recipes = recipes.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings__rating'),
        is_favorite=Exists(SavedRecipe.objects.filter(recipe=OuterRef('pk'), user=user)
            ) if user else Value(False)
    )
    return annotated_recipes