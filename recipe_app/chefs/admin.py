from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(Profile)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'chef_level', 'get_following', 'is_alpha_tester')

    def get_following(self, obj):
        return ", ".join([user.username for user in obj.following.all()])

@admin.register(ProfileImage)
class ProfileImageAdmin(admin.ModelAdmin):
    list_display = ['chef', 'image_preview', 'upload_datetime']
    list_filter = ['upload_datetime', 'chef']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;"/>',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'