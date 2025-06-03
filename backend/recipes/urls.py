from django.urls import path
from .views import recipe_redirect_view

app_name = 'recipes'

urlpatterns = [
    path('s/<int:recipe_id>/', recipe_redirect_view, name='recipe-redirect'),
]
