from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('previews_mockup', views.previews_mockup, name="previews_mockup"),
    path('previews', views.previews, name="previews"),
    path('recipe_mockup', views.recipe_mockup, name="recipe_mockup"),
    path('recipe', views.recipe, name="recipe"),
    path('', views.home, name="home")
]
