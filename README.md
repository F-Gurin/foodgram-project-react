# Foodgram (yandex-practicum-project)

Foodgram - онлайн сервис для публикации кулинарных рецептов. Пользователи могут создавать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное» и скачивать список продуктов для приготовления выбранных блюд.

Проект доступен по адресу: http://foodgramio.sytes.net/

Login Superuser: Practicum
Password: yandex2022

### Технологии
Python 3.7
Django 3.2.13

### Установка и начало работы:
1. Установите Docker согласно [инструкции для вашей ОС](https://docs.docker.com/engine/install/). 
2. Склонируйте данный репозиторий: 
   ```
   git@github.com:capralg/foodgram-project-react.git
   ```
3. При необходимости измените настройки Django-приложения.   
  Создайте файл `.env` в корневой директории проекта и укажите в нем следующие переменные:
   * `DEBUG` - True/False для debug-режима
   * `ALLOWED_HOSTS`- список адресов по которым приложение принимает запросы. Для запуска на локальной машине укажите localhost;
  
4. Для работы с приложением используйте следующие команды в [директории infra](infra):
   * Запуск контейнеров: 
     ```
     docker-compose up -d --build
     ```
   * Создание суперюзера Django: 
     ```
     docker-compose exec backend python manage.py createsuperuser

     ``` 
   * Загрузка исходных данных из файла в БД (файл с данными есть в репозитории): 
     ```
     docker-compose exec backend python manage.py  load_ingredients < dump.json
     ```
   * Остановка контейнеров: 
     ```
     docker-compose down
     ```

### Автор
e-mail: f.v.gurin@gmail.com
Telegram: @f_gurin