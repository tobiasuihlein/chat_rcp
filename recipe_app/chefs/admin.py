from django.contrib import admin
from .models import *

@admin.register(Profile)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'chef_level', 'get_followers', 'is_alpha_tester')

    def get_followers(self, obj):
        return ", ".join([follower.username for follower in obj.followers.all()])
