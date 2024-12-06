from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet)
router.register(r'components', ComponentViewSet)
router.register(r'instructions', InstructionViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
]