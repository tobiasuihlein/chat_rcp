from django.urls import path
from . import views

app_name = 'chefs'

urlpatterns = [
    path('login/', views.login_chef, name='login'),
    path('logout/', views.logout_chef, name='logout'),
]