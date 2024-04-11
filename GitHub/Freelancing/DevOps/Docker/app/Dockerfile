# Используем базовый образ Python
FROM python

# Устанавливаем зависимости
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Копируем исходный код приложения в контейнер
COPY ./app.py /app.py

# Указываем порт, который будет использоваться в контейнере
EXPOSE 8080

# Запускаем приложение
CMD ["python", "/app.py"]
