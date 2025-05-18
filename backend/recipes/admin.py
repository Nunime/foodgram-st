from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import Recipe, RecipeIngredient, Ingredient, FavoriteRecipes, ShoppingCart


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        min_recipe = Recipe.objects.order_by('cooking_time').first()
        max_recipe = Recipe.objects.order_by('-cooking_time').first()

        if not min_recipe or not max_recipe:
            return ()

        min_cooking_time = min_recipe.cooking_time
        max_cooking_time = max_recipe.cooking_time
        median_cooking_time = (min_cooking_time + max_cooking_time) / 2

        return (
            ('fast', f'Быстрые (< {median_cooking_time} мин)'),
            ('medium', f'Средние ({median_cooking_time}-{max_cooking_time} мин)'),
            ('slow', f'Долгие (> {max_cooking_time} мин)'),
        )

    def queryset(self, request, queryset):
        min_cooking_time = self.get_min_cooking_time()
        max_cooking_time = self.get_max_cooking_time()
        median_cooking_time = (min_cooking_time + max_cooking_time) / 2

        if self.value() == 'fast':
            return queryset.filter(cooking_time__lt=median_cooking_time)
        elif self.value() == 'medium':
            return queryset.filter(
                cooking_time__gte=median_cooking_time,
                cooking_time__lte=max_cooking_time
            )
        elif self.value() == 'slow':
            return queryset.filter(cooking_time__gt=max_cooking_time)

    def get_min_cooking_time(self):
        recipe = Recipe.objects.order_by('cooking_time').first()
        return recipe.cooking_time if recipe else 0

    def get_max_cooking_time(self):
        recipe = Recipe.objects.order_by('-cooking_time').first()
        return recipe.cooking_time if recipe else float('inf')


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
        return obj.favorited_by.count()

    @admin.display(description='Продукты')
    def get_ingredients_list(self, obj):
        ingredients = obj.ingredients.prefetch_related('ingredient').all()
        html = '<ul>'
        for item in ingredients:
            html += f'<li>{item.ingredient.name} ({item.amount} {item.ingredient.measurement_unit})</li>'
        html += '</ul>'
        return mark_safe(html)

    @admin.display(description='Картинка')
    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50">', obj.image.url)
        return '-'


@admin.register(FavoriteRecipes, ShoppingCart)
class FavoriteAndShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    raw_id_fields = ('user', 'recipe')
