from django.db.models import Avg, Count, Exists, OuterRef, Value
from django.db.models import BooleanField
from .models import *

def annotate_recipes(recipes, user):
    annotated_recipes = recipes.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings__rating'),
        is_favorite=Exists(SavedRecipe.objects.filter(recipe=OuterRef('pk'), user=user)
            ) if user and user.is_authenticated else Value(False, output_field=BooleanField())
    )
    return annotated_recipes