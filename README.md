# Продуктовый помощник Foodgram

Автор проекта: Гавриков Никита

## Описание проекта

«Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
Моя роль в разработке этого проета заключалась в создании всей backend части проетка, настройки Docker и CI/CD.

## Стэк проекта

![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)

## Запуск проекта локально (только Backend)

Склонируйте репозиторий себе на компьютер и перейдите в папку backend:
``` bash
git clone https://github.com/nunime/foodgram-st.git
cd foodgram-st/backend/
```
Выполните миграции:
``` BASH
python manage.py migrate
```
Создайте администратора:
``` BASH
python manage.py createsuperuser
```
### Загрузите в базу данных собранные зарание данные
Загрузить список ингредиентов:
``` BASH
python manage.py load_ingredients
```
---
Теперь можно запускать проект:
``` BASH
python manage.py runserver
```
## Полный запуск проекта

Склонируйте репозиторий себе на компьютер и перейдите в корневую папку проекта:
``` bash
git clone https://github.com/nunime/foodgram-st.git
cd foodgram-st/
```

В корневой папке вам нужно создать `.env` файл (в директории лежит `.env.example` файл, для примера)

Перейдите в папку с инфраструктурой и выполните сборку проекта с помощью docker-compose
``` bash
cd infra/
sudo docker compose up --build
```

Откройте в текущей директории ещё один терминал и выполните в нём следующие команды:
1) Выполнение миграций
``` bash
sudo docker compose exec backend python3 manage.py migrate
```
2) Заполнение базы данных

    - Список ингредиентов:
    ``` BASH
    sudo docker compose exec backend python3 manage.py load_ingredients
    ```

3) Соберите статические файлы backend'а и скопируйте их в директорию `/collected_static/statis/`
``` BASH
sudo docker compose exec backend python3 manage.py collectstatic
```
``` BASH
sudo docker compose exec backend cp -r static/. /collected_static/static/
```
---
Проект успешно запущен, чтобы попасть на сайт, нужно перейти по ссылке [http://localhost/](http://localhost/)