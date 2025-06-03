from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import CustomUser, Subscriptions
from recipes.models import FavoriteRecipes, ShoppingCart


class FavoriteRecipesAdminInline(admin.TabularInline):
    model = FavoriteRecipes
    extra = 1
    autocomplete_fields = ['recipe']
    verbose_name_plural = 'Избранные рецепты'


class ShoppingCartAdminInline(admin.TabularInline):
    model = ShoppingCart
    extra = 1
    autocomplete_fields = ['recipe']
    verbose_name_plural = 'Списки покупок'


class SubscriptionsAdminInline(admin.TabularInline):
    model = Subscriptions
    extra = 1
    fk_name = 'user'
    autocomplete_fields = ['subscribe']
    verbose_name_plural = 'Подписки'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_display = [
        'id',
        'username',
        'get_full_name',
        'email',
        'get_avatar_preview',
        'get_recipes_count',
        'get_subscriptions_count',
        'get_subscribers_count'
    ]

    @admin.display(description='ФИО')
    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip()

    @admin.display(description='Аватар')
    @mark_safe
    def get_avatar_preview(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" width="50" height="50">'
        return '-'

    @admin.display(description='Рецептов')
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Подписок')
    def get_subscriptions_count(self, obj):
        return obj.subscriptions.count()

    @admin.display(description='Подписчиков')
    def get_subscribers_count(self, obj):
        return obj.subscribers.count()

    fieldsets = (
        ('About User', {
            'fields': ('username', 'email', 'first_name',
                       'last_name', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff',
                       'is_superuser', 'groups')
        }),
        ('Last Login', {
            'fields': ('date_joined',)
        })
    )

    inlines = [FavoriteRecipesAdminInline, ShoppingCartAdminInline,
               SubscriptionsAdminInline]


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    pass
