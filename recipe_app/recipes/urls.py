from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('generate/previews', views.previews, name="previews"),
    path('generate/recipe', views.recipe_generated, name="recipe"),
    path('detail/<slug:slug>/', views.recipe_detail, name='detail'),
    path('toggle-save/<int:recipe_id>/', views.toggle_save_recipe, name='toggle_save_recipe'),
    path('recipes/rate/<int:recipe_id>/', views.rate_recipe, name='rate_recipe'),
    path('explore/', views.explore, name='explore'),
    path('library/', views.library, name='library'),
    path('generate/', views.generate, name="generate"),
    path('create/text/', views.create_recipe_with_text, name="create_with_text"),
    path('create/image/', views.create_recipe_with_image, name="create_with_image"),
    path('new_recipe/text/', views.new_recipe_by_text, name="new_recipe_by_text"),
]