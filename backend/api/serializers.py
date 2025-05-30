from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer as DjoserUserSerializer

from recipes.models import Ingredient, Recipe, RecipeIngredient


User = get_user_model()


class StrictBase64ImageField(Base64ImageField):
    def to_internal_value(self, data):
        if data == '':
            raise serializers.ValidationError('This field is required.')
        return super().to_internal_value(data)


class ShortRecipesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(DjoserUserSerializer):
    avatar = StrictBase64ImageField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + (
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.subscriptions.filter(id=obj.id).exists()
        return False


class SubscriptionsUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count', read_only=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('recipes',
                                               'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')

        recipes = obj.recipes.all()

        if limit and limit.isdigit() and int(limit) >= 0:
            recipes = recipes[:int(limit)]

        serializers = ShortRecipesSerializer(
            recipes,
            many=True,
            context={'request': request}
        )

        return serializers.data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=1,
        error_messages={'min_value': 'Количество ингредиента должно быть больше 0'}
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    text = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return obj.shopping_carts.filter(user=request.user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = StrictBase64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=1,
        error_messages={'min_value': 'Время приготовления должно быть больше 0'}
    )

    class Meta:
        model = Recipe
        fields = [
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Ingredients list cannot be empty.')

        ingredients = [item['id'] for item in value]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                'Ingredient is repeat.'
            )

        return value

    def add_recipe_ingredients(self, instance, ingredients):
        ingredients_links = [
            RecipeIngredient(
                recipe=instance,
                ingredient=item['id'],
                amount=item['amount']
            ) for item in ingredients
        ]

        RecipeIngredient.objects.bulk_create(ingredients_links)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self.add_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        instance.recipe_ingredients.all().delete()
        self.add_recipe_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        read_serializer = self.context.get('read_serializer')
        if read_serializer:
            return read_serializer(
                instance,
                context=self.context
            ).data
        return super().to_representation(instance)
