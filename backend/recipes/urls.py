from django.urls import path
from .views import recipe_redirect_view, redirect_to_recipe

app_name = 'recipes'

urlpatterns = [
    path('s/<int:recipe_id>/', recipe_redirect_view, name='recipe-redirect'),
    path('hex/<int:recipe_id>/', redirect_to_recipe, name='recipe-hex-redirect'),
]
