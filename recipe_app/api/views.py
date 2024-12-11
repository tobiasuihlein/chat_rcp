 
from rest_framework import viewsets
from recipes.models import Recipe
from .serializers import *
from recipes.models import *

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class ComponentViewSet(viewsets.ModelViewSet):
    queryset = RecipeComponent.objects.all()
    serializer_class = ComponentSerializer

class InstructionViewSet(viewsets.ModelViewSet):
    queryset = RecipeInstruction.objects.all()
    serializer_class = InstructionSerializer

class SavedRecipeViewSet(viewsets.ModelViewSet):
    queryset = SavedRecipe.objects.all()
    serializer_class = SavedRecipeSerializer