from django.urls import path
from . import views

app_name = 'chefs'

urlpatterns = [
    path('login/', views.login_chef, name='login'),
    path('logout/', views.logout_chef, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('follow/<int:user_id>/', views.follow_toggle, name='follow_toggle'),
    path('<str:username>/following/', views.following_list, name='following_list'),
    path('<str:username>/followers/', views.followers_list, name='followers_list'),
]