from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.http import Http404

from .models import Recipe


@require_GET
def recipe_redirect_view(request, recipe_id):
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise Http404(f'Рецепт с id={recipe_id} не найден')
    return redirect(f'/recipes/{recipe_id}/')
