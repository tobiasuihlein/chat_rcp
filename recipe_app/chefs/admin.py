from django.contrib import admin
from .models import *

@admin.register(Profile)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'chef_level', 'get_following', 'is_alpha_tester')

    def get_following(self, obj):
        return ", ".join([user.username for user in obj.following.all()])
