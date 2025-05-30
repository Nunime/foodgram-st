from django.contrib import admin
from django.utils.html import mark_safe
from .models import Recipe, RecipeIngredient, Ingredient, FavoriteRecipes, ShoppingCart


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        min_recipe = Recipe.objects.order_by('cooking_time').first()
        max_recipe = Recipe.objects.order_by('-cooking_time').first()

        if not min_recipe or not max_recipe or min_recipe == max_recipe:
            return ()

        self.min_cooking_time = min_recipe.cooking_time
        self.max_cooking_time = max_recipe.cooking_time
        self.median_cooking_time = (self.min_cooking_time + self.max_cooking_time) / 2

        return (
            ('fast', f'Быстрые (< {self.median_cooking_time} мин)'),
            ('medium', f'Средние ({self.median_cooking_time}-{self.max_cooking_time} мин)'),
            ('slow', f'Долгие (> {self.max_cooking_time} мин)'),
        )

    def queryset(self, request, queryset):
        if not hasattr(self, 'median_cooking_time'):
            return queryset

        if self.value() == 'fast':
            return queryset.filter(cooking_time__lt=self.median_cooking_time)
        elif self.value() == 'medium':
            return queryset.filter(
                cooking_time__gte=self.median_cooking_time,
                cooking_time__lte=self.max_cooking_time
            )
        elif self.value() == 'slow':
            return queryset.filter(cooking_time__gt=self.max_cooking_time)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'get_recipes_count')

    @admin.display(description='Рецептов')
    def get_recipes_count(self, obj):
        return obj.ingredient_recipes.count()
    search_fields = ['name', 'measurement_unit']
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
    list_filter = (CookingTimeFilter, 'author')
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
        ingredients = obj.recipe_ingredients.prefetch_related('ingredient').all()
        ingredients_list = [
            f'{item.ingredient.name} ({item.amount} {item.ingredient.measurement_unit})'
            for item in ingredients
        ]
        return mark_safe('<br>'.join(ingredients_list))

    @admin.display(description='Картинка')
    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50">')
        return '-'


@admin.register(FavoriteRecipes, ShoppingCart)
class FavoriteAndShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    raw_id_fields = ('user', 'recipe')
