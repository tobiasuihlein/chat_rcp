from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('previews', views.previews, name="previews"),
    path('recipe', views.recipe_generated, name="recipe"),
    path('', views.home, name="home")
]