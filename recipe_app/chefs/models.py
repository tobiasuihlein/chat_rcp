from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):

    class ChefLevel(models.IntegerChoices):
        LEVEL_0 = 0, 'Tellerwäscher'
        LEVEL_1 = 1, 'Chef de Partie'
        LEVEL_2 = 2, 'Sous Chef'
        LEVEL_3 = 3, 'Chef de Cuisine'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, blank=True, related_name='following')
    is_alpha_tester = models.BooleanField(default=True)
    chef_level = models.IntegerField(choices=ChefLevel.choices, default=ChefLevel.LEVEL_0)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def follow(self, user_to_follow):
        """Follow a user if not already following"""
        if user_to_follow not in self.followers.all():
            self.followers.add(user_to_follow)
    
    def unfollow(self, user_to_unfollow):
        """Unfollow a user if currently following"""
        if user_to_unfollow in self.followers.all():
            self.followers.remove(user_to_unfollow)
    
    def is_following(self, user):
        """Check if following a specific user"""
        return user in self.followers.all()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create Profile automatically when User is created"""
    if created:
        Profile.objects.create(user=instance)
