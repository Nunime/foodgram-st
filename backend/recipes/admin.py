from django.contrib import admin

from .models import (Recipe, RecipeIngredient, Ingredient,
                     FavoriteRecipes, ShoppingCart)
from django.utils.html import format_html, mark_safe


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        min_cooking_time = Recipe.objects.order_by('cooking_time').first().cooking_time
        max_cooking_time = Recipe.objects.order_by('-cooking_time').first().cooking_time
        median_cooking_time = (min_cooking_time + max_cooking_time) / 2

        return (
            ('fast', f'Быстрые (< {median_cooking_time} мин)'),
            ('medium', f'Средние ({median_cooking_time}–{max_cooking_time} мин)'),
            ('slow', f'Долгие (> {max_cooking_time} мин)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'fast':
            return queryset.filter(cooking_time__lt=self.get_median_cooking_time())
        elif self.value() == 'medium':
            return queryset.filter(
                cooking_time__gte=self.get_median_cooking_time(),
                cooking_time__lte=self.get_max_cooking_time()
            )
        elif self.value() == 'slow':
            return queryset.filter(cooking_time__gt=self.get_max_cooking_time())

    def get_median_cooking_time(self):
        return (self.get_min_cooking_time() + self.get_max_cooking_time()) / 2

    def get_min_cooking_time(self):
        return Recipe.objects.order_by('cooking_time').first().cooking_time

    def get_max_cooking_time(self):
        return Recipe.objects.order_by('-cooking_time').first().cooking_time


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ['name']
    list_filter = ['measurement_unit']


class RecipeIngredientAdminInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['ingredient']
    fields = ['ingredient', 'amount']
    verbose_name_plural = 'Ингредиенты'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'cooking_time',
        'author',
        'get_favorite_count',
        'get_ingredients_list',
        'get_image_preview',
    )
    search_fields = ('name', 'author__username')
    list_filter = (CookingTimeFilter,)
    fieldsets = (
        ('Описание рецепта', {
            'fields': ('name', 'text', 'cooking_time', 'image', 'author')
        }),
    )
    inlines = [RecipeIngredientAdminInline]

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return obj.favorites.count()

    @admin.display(description='Продукты')
    def get_ingredients_list(self, obj):
        ingredients = obj.recipeingredient_set.all()
        html = '<ul>'
        for ingredient in ingredients:
            html += f'<li>{ingredient.ingredient.name} ({ingredient.amount} {ingredient.ingredient.measurement_unit})</li>'
        html += '</ul>'
        return mark_safe(html)

    @admin.display(description='Картинка')
    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return '-'


@admin.register(FavoriteRecipes, ShoppingCart)
class FavoriteAndShoppingCartAdmin(admin.ModelAdmin):
    pass
