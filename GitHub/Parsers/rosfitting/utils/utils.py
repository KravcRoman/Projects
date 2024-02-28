import os
import time
from datetime import datetime

import csv
import requests
import rosfitting_parser_control_module as module
from bs4 import BeautifulSoup


# FIXME ——————————————————————————————————————————————————————————————— LOGS ———
import logging

# Определяем текущую директорию
CURRENT_DIR = os.getcwd()

# Настройка логов
logging.basicConfig(filename=CURRENT_DIR + f'/errors_utils.log',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format=f'%(levelname)s %(asctime)s %(message)s')
# FIXME —————————————————————————————————————————— ПРИ СОЕДИНЕНИИ С МОДУЛЕМ ————


def print_template(message) -> str:
    try:
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"\r{current_date}: {message}"
        return message

    # Ловим ошибку
    except Exception as e:
        logging.error(f'in print_template(): {e}')
        module.send_error_to_cmc(f'in print_template(): {e}')


def download_file():
    try:
        url = 'https://rosfitting.ru/price/'
        response = requests.get(url)
        response.raise_for_status()
        # STATUS: PID=9052 CPU:11.2% RAM:0.3%  49MB
        soup = BeautifulSoup(response.content, 'html.Parsers1')
        xlsx_link = soup.find('a', text='скачать xlsx')
        if xlsx_link:
            xlsx_url = xlsx_link['href']
        else:
            return False

        response = requests.get(xlsx_url)

        with open('price.xlsx', 'wb') as file:
            file.write(response.content)
            # STATUS: PID=9069 CPU:3.7% RAM:0.3%  54MB
        return True

    # Ловим ошибку
    except Exception as e:
        logging.error(f'in download_file(): {e}')
        module.send_error_to_cmc(f'in download_file(): {e}')


def check_reports_folder_exist() -> str:
    try:
        root_folder = os.environ.get('PROJECT_ROOT')
        reports_folder = os.path.join(root_folder, "reports")

        if not os.path.exists(reports_folder):
            os.makedirs(reports_folder)
        return reports_folder

    # Ловим ошибку
    except Exception as e:
        logging.error(f'in check_reports_folder_exist(): {e}')
        module.send_error_to_cmc(f'in check_reports_folder_exist(): {e}')


def write_products_to_csv(products):
    try:
        reports_folder = check_reports_folder_exist()
        # STATUS: PID=9089 CPU:4.3% RAM:0.8%  128MB

        current_datetime = datetime.now()
        current_datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

        csv_file_path = os.path.join(reports_folder, f"{current_datetime_str}.csv")
        # STATUS: PID=9108 CPU:3.2% RAM:0.8%  126MB

        headers = list(vars(products[0]).keys())
        # STATUS: PID=9108 CPU:2.5% RAM:0.8%  126MB

        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            # STATUS: PID=9136 CPU:3.3% RAM:0.8%  127MB

            writer.writerow(headers)
            # STATUS: PID=9136 CPU:8.2% RAM:0.8%  127MB

            for product in products:

                time.sleep(module.PAUSE)
                # STATUS: PID=9154 CPU:10.6% RAM:0.8%  128MB

                values = [getattr(product, prop) for prop in headers]
                # STATUS: PID=9316 CPU:10.6% RAM:0.8%  126MB

                writer.writerow(values)
                # STATUS: PID=9449 CPU:7.5% RAM:0.8%  124MB

    # Ловим ошибку функции
    except Exception as e:
        logging.error(f'in write_products_to_csv(): {e}')
        module.send_error_to_cmc(f'in write_products_to_csv(): {e}')
