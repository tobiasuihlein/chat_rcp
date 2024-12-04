from django.db import models


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=20)
    time_total = models.IntegerField()
    time_preparation = models.IntegerField()
    time_cooking = models.IntegerField()
    default_servings = models.IntegerField(null=True)
    created_by = models.CharField(max_length=255, default="Claude")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created_at', 'title']


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=25, choices=[('M', 'Main Ingredient'), ('A', 'Additional Ingredient')])
    amount = models.IntegerField(null=True)
    unit = models.CharField(max_length=25)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")

    def __str__(self):
        return self.name

