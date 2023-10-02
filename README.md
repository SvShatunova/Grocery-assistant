# praktikum_new_diplom

## Описание

Сайт Foodgram, <Продуктовый помощник>. Это онлайн-сервис и API для него. На этом сайте пользователи могут:
    - публиковать, получать, создавать рецепты
    - подписываться на других пользователей
    - добавлять рецепты в избранное
    - добавлять и скачивать список покупок
    - создавать, удалять и редактировать собственные рецепты

### Технологии

* Django==3.2.3
* djangorestframework==3.12.4
* djangorestframework-simplejwt==5.2.2
* django-filter==23.2
* djoser==2.1.0
* webcolors==1.11.1
* psycopg2-binary==2.9.3
* Pillow==9.0.0
* PyYAML==6.0
* python-dotenv==1.0.0
* gunicorn==20.1.0
* sorl-thumbnail==12.9.0
* django-import-export==3.2.0
* reportlab==4.0.4

## Инструкции по установке

***- Клонируйте репозиторий:***

git clone:

***- Установите и активируйте виртуальное окружение:***

-для MacOS

python3 -m venv venv

-для Windows

python -m venv venv
source venv/bin/activate
source venv/Scripts/activate

***- Установите зависимости из файла requirements.txt:***

pip install -r requirements.txt

***- Примените миграции:***

python manage.py migrate

***- В папке с файлом manage.py выполните команду для запуска локально:***

python manage.py runserver

***- Локально Документация доступна по адресу:***

-http://127.0.0.1/api/docs/

### Собираем контейнерыы

Из папки infra/ разверните контейнеры при помощи docker-compose:

docker-compose up -d --build

Выполните миграции:

docker-compose exec backend python manage.py migrate

Создайте суперпользователя:

docker-compose exec backend python manage.py createsuperuser

Соберите статику:

docker-compose exec backend python manage.py collectstatic

Наполните базу данных ингредиентами и тегами. Выполняйте команду из дериктории где находится файл manage.py:

docker-compose exec backend python manage.py load_data

Остановка проекта:

docker-compose down

### Подготовка к запуску проекта на удаленном сервере

Cоздать и заполнить .env файл в директории infra

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
TOKEN=*
ALLOWED_HOSTS=*

#### Проект доступен по ссылкам

-https://foodgramsv.ddns.net/

-https://foodgramsv.ddns.net/admin/

-createsuperuser
    *login =
    *password =

-user
    *login =
    *password =

##### Автор

Светлана Шатунова
