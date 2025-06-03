from rest_framework import viewsets, status
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework import serializers
from django.urls import reverse

from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, FavoriteRecipes)
from users.models import Subscriptions
from .serializers import (IngredientSerializer, RecipeWriteSerializer,
                          RecipeReadSerializer, ShortRecipesSerializer,
                          SubscriptionsUserSerializer)
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path=('me/avatar'),
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == 'PUT':
            if not request.data.get('avatar'):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            response = self.partial_update(request, *args, **kwargs)
            response.data = {'avatar': response.data.get('avatar')}
            return response
        elif request.method == 'DELETE':
            user = request.user
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(
            subscriptions__user=user
        )

        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsUserSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        user = request.user
        sub_user = self.get_object()

        if request.method == 'POST':
            if user == sub_user:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя'
                )

            subscription, created = Subscriptions.objects.get_or_create(
                user=user,
                subscribe=sub_user
            )

            if not created:
                raise serializers.ValidationError(
                    f'Вы уже подписаны на пользователя {sub_user.username}'
                )

            serializer = SubscriptionsUserSerializer(
                sub_user, context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        get_object_or_404(
            Subscriptions,
            user=user,
            subscribe=sub_user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _handle_m2m_action(self, request, model):
        user = request.user
        recipe = self.get_object()

        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=user,
                recipe=recipe
            )

            if not created:
                raise serializers.ValidationError(
                    f'{model._meta.verbose_name} уже существует'
                )

            serializer = ShortRecipesSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        get_object_or_404(
            model,
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self._handle_m2m_action(
            request,
            ShoppingCart
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        from datetime import datetime
        
        shopping_cart = request.user.shopping_carts.select_related(
            'recipe', 'recipe__author'
        )
        
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=shopping_cart.values('recipe')
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')

        recipes = shopping_cart.all()

        current_date = datetime.now().strftime('%d.%m.%Y')
        
        shopping_list = '\n'.join([
            f'Список покупок на {current_date}',
            f'Пользователь: {request.user.username}',
            '',
            'Продукты к покупке:',
            *[
                f'{i}. {item["ingredient__name"].capitalize()} - '
                f'{item["total_amount"]} {item["ingredient__measurement_unit"]}'
                for i, item in enumerate(ingredients, start=1)
            ],
            '',
            'Продукты для рецептов:',
            *[
                f'- {recipe.recipe.name} (автор: {recipe.recipe.author.username})'
                for recipe in recipes
            ]
        ])

        return FileResponse(
            shopping_list,
            as_attachment=True,
            filename='shopping_list.txt'
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self._handle_m2m_action(
            request,
            FavoriteRecipes
        )

    @action(
        detail=True,
        methods=['get'],
        url_path=('get-link')
    )
    def get_short_link(self, request, pk=None):
        if not Recipe.objects.filter(id=pk).exists():
            raise Http404('Рецепт не найден')
            
        relative_url = reverse('recipe-redirect', kwargs={'recipe_id': pk})
        full_path = request.build_absolute_uri(relative_url)

        data = {
            'short-link': full_path
        }
        return Response(data)
