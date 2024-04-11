import psutil
import requests
import time

# Параметры для генерации alarm
memory_threshold = 70  # процент памяти, при достижении которого будет отправлен alarm
memory_alarm_url = 'http://example.com/memory-alarm'  # URL для отправки alarm


# Функция для отправки alarm
def send_memory_alarm():
    try:
        response = requests.post(memory_alarm_url)
        print(f"Memory alarm sent: {response.status_code}")
    except Exception as e:
        print(f"Error sending memory alarm: {e}")


# Главный цикл программы
while True:
    # Получаем информацию о потреблении памяти
    memory_usage = psutil.virtual_memory().percent

    # Проверяем, достиг ли уровень потребления памяти порогового значения
    if memory_usage >= memory_threshold:
        # Отправляем alarm
        send_memory_alarm()

    # Ожидаем некоторое время перед следующим циклом
    time.sleep(60)  # 60 секунд
