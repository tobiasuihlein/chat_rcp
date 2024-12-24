from django.urls import path
from . import views

app_name = 'chefs'

urlpatterns = [
    path('login/', views.login_chef, name='login'),
    path('logout/', views.logout_chef, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('toggle-follow/<int:user_id>/', views.follow_toggle, name='follow_toggle'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/upload-image/', views.upload_profile_image, name='upload_profile_image'),
]