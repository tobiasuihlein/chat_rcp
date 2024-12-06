from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('generated-previews', views.previews, name="previews"),
    path('generated-recipe', views.recipe_generated, name="recipe"),
    path('detail/<int:pk>/', views.recipe_detail, name='detail'),
    path('', views.recipe_list, name='list'),
    path('generate', views.home, name="generate"),
    path('generate', views.home, name="home"),
]