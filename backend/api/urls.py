from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, IngredientViewSet, RecipeViewSet


router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
