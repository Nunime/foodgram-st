import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из JSON в базу данных'

    def handle(self, *args, **options):
        filename = 'data/ingredients.json'
        try:
            with open(filename, 'r', encoding='utf-8') as ingredients_data:
                ingredients = json.load(ingredients_data)

            ingredient_objects = [
                Ingredient(**item)
                for item in ingredients
            ]

            created_ingredients = Ingredient.objects.bulk_create(
                ingredient_objects,
                ignore_conflicts=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно добавлено {len(created_ingredients)} ингредиентов!'
                )
            )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f'Ошибка при загрузке ингредиентов из файла {filename}: {e}'
                )
            )
