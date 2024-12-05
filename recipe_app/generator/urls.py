from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('previews', views.previews, name="previews"),
    path('recipe-generated', views.recipe_generated, name="recipe-generated"),
    path('', views.home, name="home")
]
