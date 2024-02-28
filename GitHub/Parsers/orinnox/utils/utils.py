import os
import requests
import random
import time
import pytz

from typing import Union
from datetime import datetime


# FIXME —————————————————————————————————————————————————————————— SETTINSG ————
import orinnox_parser_control_module as module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.jog',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————



def get_requests(url):
    try:
        try:
            import requests

            cookies = {
                '_ym_uid': '1699013382347358004',
                '_ym_d': '1699013382',
                '_gid': 'GA1.2.1810991489.1699013382',
                '_ct': '2400000000059912436',
                '_ct_client_global_id': '1ce30845-2d47-5f06-9eb7-b5dd010c0ceb',
                '_ym_isad': '1',
                'cted': 'modId%3Dc8spz9t3%3Bclient_id%3D1775010740.1699013382%3Bya_client_id%3D1699013382347358004',
                '_ga': 'GA1.2.1775010740.1699013382',
                '_ym_visorc': 'w',
                '_ct_ids': 'c8spz9t3%3A58269%3A86648151',
                '_ct_session_id': '86648151',
                '_ct_site_id': '58269',
                'call_s': '%3C!%3E%7B%22c8spz9t3%22%3A%5B1699094363%2C86648151%2C%7B%22308914%22%3A%22896543%22%7D%5D%2C%22d%22%3A2%7D%3C!%3E',
                '_ga_22FSXP5RSW': 'GS1.1.1699092563.3.0.1699092570.53.0.0',
                '_ga_Q5SEEVV46R': 'GS1.1.1699092563.3.0.1699092570.0.0.0',
            }

            headers = {
                'authority': 'www.orinnox.ru',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                # 'cookie': '_ym_uid=1699013382347358004; _ym_d=1699013382; _gid=GA1.2.1810991489.1699013382; _ct=2400000000059912436; _ct_client_global_id=1ce30845-2d47-5f06-9eb7-b5dd010c0ceb; _ym_isad=1; cted=modId%3Dc8spz9t3%3Bclient_id%3D1775010740.1699013382%3Bya_client_id%3D1699013382347358004; _ga=GA1.2.1775010740.1699013382; _ym_visorc=w; _ct_ids=c8spz9t3%3A58269%3A86648151; _ct_session_id=86648151; _ct_site_id=58269; call_s=%3C!%3E%7B%22c8spz9t3%22%3A%5B1699094363%2C86648151%2C%7B%22308914%22%3A%22896543%22%7D%5D%2C%22d%22%3A2%7D%3C!%3E; _ga_22FSXP5RSW=GS1.1.1699092563.3.0.1699092570.53.0.0; _ga_Q5SEEVV46R=GS1.1.1699092563.3.0.1699092570.0.0.0',
                'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            }

            response = requests.get(url, cookies=cookies, headers=headers, timeout=(20, 60))

            response.raise_for_status()
        except Exception as e:
            print(e)
            return False
        return response

    except Exception as e:
        logging.error(f'in get_requests: {e}')
        module.send_error_to_cmc(f'in get_requests: {str(e)[:50]}')

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
        logging.error(f'in get_current_time: {e}')
        module.send_error_to_cmc(f'in get_current_time: {str(e)[:50]}')

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
        logging.error(f'in print_template: {e}')
        module.send_error_to_cmc(f'in print_template: {str(e)[:50]}')

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
            print(print_template("Could not find or create reports folder: {}".format(e)))
            return False

    except Exception as e:
        logging.error(f'in check_reports_folder_exist: {e}')
        module.send_error_to_cmc(f'in check_reports_folder_exist: {str(e)[:50]}')

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
        logging.error(f'in random_sleep: {e}')
        module.send_error_to_cmc(f'in random_sleep: {str(e)[:50]}')