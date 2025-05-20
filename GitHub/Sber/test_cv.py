"""
Программа должна выполнять 3 задачи:

1. Раз в 5 секунд обращаться по адресу https://vibe.sirotinsky.com/long_task?seconds=3 и выводить полученный json ответ в консоль
2. Раз в 10 секунд обращаться по адресу https://api.nasdaq.com/api/company/AAPL/company-profile и сохранять результат в файл json
3. Раз в 15 секунд обращаться по адресу https://cbr.ru/currency_base/daily/, в полученном HTML документе собрать данные о стоимости валюты {тикер (2 столбец): стоимость (5 стобец)} сохранять результат в файл json
"""

# Code



if __name__ == "__main__":
    # Code
    pass


import multiprocessing
import time
import requests
import json
from bs4 import BeautifulSoup

def fetch_json(url):
    """Функция для получения JSON-данных по указанному URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при получении данных с {url}: {e}")
        return None

def fetch_html(url):
    """Функция для получения HTML-страницы по указанному URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Ошибка при получении HTML с {url}: {e}")
        return None

def task_1():
    """Раз в 5 секунд получает JSON-ответ по API и выводит в консоль."""
    url = "https://vibe.sirotinsky.com/long_task?seconds=3"
    while True:
        data = fetch_json(url)
        if data:
            print("Task 1 Response:", data)
        time.sleep(5)

def task_2():
    """Раз в 10 секунд получает данные о компании и сохраняет в JSON-файл."""
    url = "https://api.nasdaq.com/api/company/AAPL/company-profile"
    while True:
        data = fetch_json(url)
        if data:
            with open("company_profile.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("Task 2: Данные сохранены в company_profile.json")
        time.sleep(10)

def task_3():
    """Раз в 15 секунд получает HTML-страницу ЦБ РФ и парсит курс валют."""
    url = "https://cbr.ru/currency_base/daily/"
    while True:
        html = fetch_html(url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            currency_data = {}

            table = soup.find("table", class_="data")
            if table:
                rows = table.find_all("tr")[1:]
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 5:
                        currency_ticker = cols[1].text.strip()
                        currency_value = cols[4].text.strip()
                        currency_data[currency_ticker] = currency_value

            with open("currency_rates.json", "w", encoding="utf-8") as f:
                json.dump(currency_data, f, ensure_ascii=False, indent=4)
            print("Task 3: Данные сохранены в currency_rates.json")
        time.sleep(15)

def main():
    """Запускает все задачи в отдельных процессах."""
    processes = [
        multiprocessing.Process(target=task_1),
        multiprocessing.Process(target=task_2),
        multiprocessing.Process(target=task_3)
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

if __name__ == "__main__":
    main()