# Проект "Блог"

Проект "Блог" - это веб-приложение, разработанное на Django, предназначенное для создания и управления блогом. Приложение позволяет пользователям просматривать статьи, добавлять новые статьи, оставлять комментарии и многое другое.

## Инструкция по запуску

1. Установите Python и Django, если они еще не установлены. Можно установить их с помощью pip:

    ```bash
    pip install django
    ```

2. Клонируйте репозиторий:

    ```bash
    git clone <url-репозитория>
    ```

3. Перейдите в директорию проекта:

    ```bash
    cd <название-проекта>
    ```

4. Примените миграции:

    ```bash
    python manage.py migrate
    ```

5. Запустите сервер разработки Django:

    ```bash
    python manage.py runserver
    ```

6. Перейдите по адресу http://127.0.0.1:8000/
7. Перейдите по адресу http://127.0.0.1:8000/create/
8. Создайте Articles в админке, после этого перейдите по адресу http://127.0.0.1:8000/1/

## Логин и пароль

Для доступа к административной панели Django используйте следующие учетные данные:

- Логин: admin
- Пароль: admin

## Дополнительные комментарии

- Важно обеспечить безопасность учетных данных и не передавать их третьим лицам.
- Перед использованием в производственной среде обязательно настройте безопасность вашего приложения и сервера.
- Обновляйте Django и его зависимости регулярно для обеспечения безопасности и стабильной работы приложения.
- Не забудьте создать собственного администратора для продакшн-среды и удалить пользователя с логином `admin` после настройки проекта.