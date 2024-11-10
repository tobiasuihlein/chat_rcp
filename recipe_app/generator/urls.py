from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('previews_mockup', views.previews_mockup, name="previews_mockup"),
    path('previews', views.previews, name="previews"),
    path('', views.home, name="home")
]
