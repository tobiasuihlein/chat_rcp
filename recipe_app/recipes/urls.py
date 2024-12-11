from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('generate/previews', views.previews, name="previews"),
    path('generate/recipe', views.recipe_generated, name="recipe"),
    path('detail/<int:pk>/', views.recipe_detail, name='detail'),
    path('toggle-save/<int:recipe_id>/', views.toggle_save_recipe, name='toggle_save_recipe'),
    path('explore/', views.explore, name='explore'),
    path('library/', views.library, name='library'),
    path('generate/', views.generate, name="generate"),
]