# Простое приложение на Python с REST API и NoSQL базой данных
Этот проект представляет собой простое приложение на Python, использующее Flask для реализации REST API, и NoSQL базу данных (MongoDB) для хранения данных.


## Установка
1. Установите Docker на свой компьютер, если он еще не установлен. Инструкции можно найти на официальном сайте Docker.

2. Склонируйте этот репозиторий на свой компьютер:
    ```bash
    git clone https://github.com/example/repository.git
    ```

3. Перейдите в каталог с проектом:
    ```bash
    cd repository
    ```
 
4. Запустите приложение с помощью Docker Compose:
    ```bash
    docker-compose up --build 
    ```



## Использование
После успешного запуска приложение будет доступно по адресу http://localhost:8080.

## Создание нового значения ключ-значение
Отправьте POST запрос на http://localhost:8080/keyvalue с JSON телом вида:

    {
      "key": "example_key",
      "value": "example_value"
    }

## Изменение значения ключ-значение
Отправьте PUT запрос на http://localhost:8080/keyvalue с JSON телом вида:

    {
      "key": "example_key",
      "value": "new_value"
    }

## Чтение значения ключ-значение
Отправьте GET запрос на http://localhost:8080/keyvalue?key=example_key.


## Структура проекта
<ul>
    <li> <b> docker-compose.yml</b>: Файл для настройки и запуска контейнеров с приложением и базой данных. </li>
    <li> <b> app/</b>: Директория, содержащая файлы приложения. </li>
    <li> <b> app.py</b>: Основной файл приложения на Python с реализацией REST API. </li>
    <li> <b> requirements.txt</b>: Файл со списком зависимостей Python. </li>
</ul>

## Зависимости
<li> <b> Flask</b>: Фреймворк для создания веб-приложений на Python. </li>
<li> <b> PyMongo</b>: Библиотека для работы с MongoDB из Python. </li>
