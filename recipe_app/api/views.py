# views.py
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Recipe
from .serializers import RecipeSerializer


class RecipePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint für Rezepte.
    
    list: Alle Rezepte abrufen
    retrieve: Ein einzelnes Rezept abrufen
    """
    queryset = Recipe.objects.select_related(
        'author', 'language', 'image'
    ).prefetch_related(
        'equipments', 'diets', 'hashtags', 'times',
        'components__ingredients__ingredient',
        'instruction_steps', 'tips', 'ratings__author'
    ).all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'spiciness', 'cost', 'diets', 'author']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    lookup_field = 'slug'