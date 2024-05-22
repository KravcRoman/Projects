from django.core.management.base import BaseCommand
from django.utils import timezone
import requests
from ...models import Exchange_Rate
import schedule
import time

class Command(BaseCommand):
    help = 'Извлекаем курсы валют из json ЦБ'

    def handle(self, *args, **kwargs):
        self.fetch_rates()

    def fetch_rates(self):
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        response = requests.get(url)
        data = response.json()
        today = timezone.now().date()
        for key, value in data['Valute'].items():
            charcode = value['CharCode']
            rate = value['Previous']  # Используйте 'Previous' для вчерашнего курса (потому что цб выводит данные на следующий день)
            # rate = value['Value']
            Exchange_Rate.objects.update_or_create(
                charcode=charcode,
                date=today,  # это выводит за сегодняшнюю дату. Если мы выбрали это, то rate = value['Previous'] (потому что цб выводит данные на следующий день)
                # date=data["Date"][:9],   # это выводит запрос на дату, которая указа в запросе. Если мы выбрали это, то rate = value['Value']
                defaults={'rate': rate}
            )
        self.stdout.write(self.style.SUCCESS('Курсы валют обновлены'))

def run_command():
    cmd = Command()
    cmd.handle()

# Настройка расписания
schedule.every().day.at("00:00").do(run_command)  # Запуск в полночь каждый день

# Запуск планировщика в бесконечном цикле
while True:
    schedule.run_pending()
    time.sleep(60)  # Проверка каждую минуту





# ручной запуск
    # def handle(self, *args, **kwargs):
    #     url = "https://www.cbr-xml-daily.ru/daily_json.js"
    #     response = requests.get(url)
    #     data = response.json()
    #     today = timezone.now().date()
    #     for key, value in data['Valute'].items():
    #         charcode = value['CharCode']
    #         rate = value['Previous']
    #         #rate = value['Value']
    #         Exchange_Rate.objects.update_or_create(
    #             charcode=charcode,
    #             date=today,  # это выводит на сегодняшнюю дату. Если мы выбрали это, то rate = value['Previous'] (потому что цб выводит данные на следующий день)
    #             # date=data["Date"][:9],   # это выводит запрос на дату, которая указа в запросе. Если мы выбрали это, то rate = value['Value']
    #         # чтоб обновились данные в бд в терминале надо написать - python manage.py fetch_exchange_rates
    #             defaults={'rate': rate}
    #         )
    #     self.stdout.write(self.style.SUCCESS('Курсы валют обновлены'))
