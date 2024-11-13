from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('previews', views.previews, name="previews"),
    path('recipe', views.recipe, name="recipe"),
    path('', views.home, name="home")
]
