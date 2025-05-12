# Продуктовый помощник Foodgram

## Описание проекта

«Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
Моя роль в разработке этого проета заключалась в создании всей backend части проетка, настройки Docker и CI/CD.

## Технологии

![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)

## Запуск проекта 

Клонируйте репозиторий
``` bash
git clone https://github.com/nunime/foodgram-st.git
```

Создайте .docker.env

Перейдите в директорию с инвраструктурой проекта
``` bash
cd /foodgram-st/infra/
```

Выполните сборку проекта с помощью docker-compose
``` bash
sudo docker compose up --build
```

Откройте в текущей директории ещё один терминал и выполните в нём следующие команды
``` bash
    sudo docker compose exec backend python3 manage.py migrate && \
    sudo docker compose exec backend python3 manage.py loaddata dump.json && \                                                                 
    sudo docker compose exec backend python3 manage.py collectstatic && \
    sudo docker compose exec backend cp -r static/. /collected_static/static/
```