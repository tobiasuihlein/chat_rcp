from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('generate/previews', views.previews, name="previews"),
    path('generate/recipe', views.recipe_generated, name="recipe"),
    path('detail/<slug:slug>/', views.recipe_detail, name='detail'),
    path('toggle-save/<int:recipe_id>/', views.toggle_save_recipe, name='toggle_save_recipe'),
    path('recipes/rate/<int:recipe_id>/', views.rate_recipe, name='rate_recipe'),
    path('explore/', views.ExploreView.as_view(), name='explore'),
    path('library/', views.LibraryView.as_view(), name='library'),
    path('chefs/<str:author>/', views.AuthorRecipesView.as_view(), name='author_recipes'),
    path('generate/', views.generate, name="generate"),
    path('create/text/', views.create_recipe_with_text, name="create_with_text"),
    path('create/image/', views.create_recipe_with_image, name="create_with_image"),
    path('new_recipe/text/', views.new_recipe_by_text, name="new_recipe_by_text"),
    path('edit_recipe/<slug:slug>', views.edit_recipe, name="edit_recipe"),
    path('shopping-list', views.shopping_list, name='shopping_list'),
    path('add-recipe-to-shopping-list/<int:recipe_id>/', views.add_recipe_to_shopping_list, name='add_recipe_to_shopping_list'),
    path('remove-recipe-from-shopping-list/<int:shopping_recipe_id>/', views.remove_recipe_from_shopping_list, name='remove_recipe_from_shopping_list'),
    path('recipe/<slug:slug>/upload-image/', views.upload_recipe_image, name='upload_recipe_image'),

]