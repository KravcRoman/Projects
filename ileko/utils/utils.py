import os
import requests
import random
import time
import pytz

from typing import Union
from datetime import datetime


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import ileko_parser_control_module as module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    level=logging.ERROR, encoding='utf-8', filemode='w',
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


def get_requests(url):
    try:
        try:
            response = requests.get(url, timeout=(20, 60))
            response.raise_for_status()
        except:
            return False
        return response
    except Exception as e:
        logging.error(f'in get_requests(): {e}')
        module.send_error_to_cmc(f'in get_requests(): {str(e)[:50]}')

def get_current_time(file=False):
    """
    Возвращает текущую дату и время в формате "ГГГГ-ММ-ДД ЧЧ:ММ:СС" или в формате для использования в имени файла.
    Args:
        file (bool): Если True, возвращает дату и время в формате, подходящем для имени файла.
                     Если False (по умолчанию), возвращает дату и время в стандартном формате.
    Returns:
        str: Строка с текущей датой и временем.
    Example:
        get_current_time()  # Возвращает "2023-10-27 15:45:30"
        get_current_time(file=True)  # Возвращает "-2023-10-27-15-45-30-"
    """
    try:
        moscow_tz = pytz.timezone('Europe/metinvest')

        current_datetime = datetime.now(moscow_tz)
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        if file:
            formatted_datetime = current_datetime.strftime("-%Y-%m-%d-%H-%M-%S-")
        return formatted_datetime
    except Exception as e:
        logging.error(f'in get_current_time(): {e}')
        module.send_error_to_cmc(f'in get_current_time(): {str(e)[:50]}')

def print_template(message) -> str:
    """
    Форматирует сообщение с текущей датой и временем и возвращает его как строку.
    Args:
        message (str): Сообщение для форматирования.
    Returns:
        str: Строка с текущей датой и временем, а также переданным сообщением.
    """
    try:
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"\r{current_date}: {message}"
        return message
    except Exception as e:
        logging.error(f'in print_template(): {e}')
        module.send_error_to_cmc(f'in print_template(): {str(e)[:50]}')

def check_reports_folder_exist() -> Union[str, bool]:
    """
    Проверяет наличие папки для отчетов и создает ее, если она не существует.
    Returns:
        Union[str, bool]: Возвращает путь к папке для отчетов, если папка успешно создана или уже существует.
                         Возвращает False в случае ошибки.
    """
    try:
        try:
            root_folder = os.environ.get('PROJECT_ROOT')
            reports_folder = os.path.join(root_folder, "reports")
            reports_folder_sql = os.path.join(reports_folder, "sqlite")
            reports_folder_json = os.path.join(reports_folder, "json")
            if not os.path.exists(reports_folder):
                os.makedirs(reports_folder)

            if not os.path.exists(reports_folder_sql):
                os.makedirs(reports_folder_sql)

            if not os.path.exists(reports_folder_json):
                os.makedirs(reports_folder_json)

            return reports_folder
        except Exception as e:
            print_template("Could not find or create reports folder: {}".format(e))
            return False
    except Exception as e:
        logging.error(f'in check_reports_folder_exist(): {e}')
        module.send_error_to_cmc(f'in check_reports_folder_exist(): {str(e)[:50]}')

def random_sleep(seconds: float):
    """
    Приостанавливает выполнение программы на случайное количество времени, добавляя случайное значение к указанным секундам.
    Args:
        seconds (int): Количество секунд, на которое следует приостановить выполнение.
    Returns:
        None
    """
    try:
        random_value = random.uniform(0.01, 2)
        time.sleep(seconds + random_value)
    except Exception as e:
        logging.error(f'in random_sleep(): {e}')
        module.send_error_to_cmc(f'in random_sleep(): {str(e)[:50]}')