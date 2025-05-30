from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django.http import Http404

from .models import Recipe


@require_GET
def recipe_redirect_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return redirect('recipe-detail', pk=recipe.id)


@require_GET
def redirect_to_recipe(request, recipe_id):
    try:
        recipe_pk = int(recipe_id, 16)
    except ValueError:
        raise Http404('Неверный формат идентификатора рецепта')
    
    recipe = get_object_or_404(Recipe, id=recipe_pk)
    return redirect('recipe-detail', pk=recipe.id)
