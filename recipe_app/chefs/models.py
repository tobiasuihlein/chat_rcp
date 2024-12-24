from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import FileSystemStorage
import os

class Profile(models.Model):

    class ChefLevel(models.IntegerChoices):
        LEVEL_0 = 0, 'Tellerwäscher'
        LEVEL_1 = 1, 'Chef de Partie'
        LEVEL_2 = 2, 'Sous Chef'
        LEVEL_3 = 3, 'Chef de Cuisine'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    following = models.ManyToManyField(User, blank=True, related_name='follower')
    is_alpha_tester = models.BooleanField(default=True)
    chef_level = models.IntegerField(choices=ChefLevel.choices, default=ChefLevel.LEVEL_0)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def follow(self, user_to_follow):
        """Follow a user if not already following"""
        if user_to_follow not in self.following.all():
            self.following.add(user_to_follow)
    
    def unfollow(self, user_to_unfollow):
        """Unfollow a user if currently following"""
        if user_to_unfollow in self.following.all():
            self.following.remove(user_to_unfollow)
    
    def is_following(self, user):
        """Check if following a specific user"""
        return user in self.following.all()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create Profile automatically when User is created"""
    if created:
        Profile.objects.create(user=instance)


class ImageStorage(FileSystemStorage):
    def get_valid_name(self, name):
        basename, ext = os.path.splitext(name)
        return f"{basename}_{hash(name)}{ext}"

class ProfileImage(models.Model):
    image = models.ImageField(upload_to='profile_images/', storage=ImageStorage(), max_length=500, blank=True, null=True)
    alt_text = models.CharField(max_length=100, blank=True, default="profile image")
    upload_datetime = models.DateTimeField(auto_now_add=True)
    chef = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="image")

    class Meta:
        ordering = ['-upload_datetime']

    def __str__(self):
        return f"Image for {self.chef.user.username}"

    def save(self, *args, **kwargs):
        if self.chef:
            ProfileImage.objects.filter(chef=self.chef).delete()
        super().save(*args, **kwargs)

    @property
    def filename(self):
        return os.path.basename(self.image.name)
