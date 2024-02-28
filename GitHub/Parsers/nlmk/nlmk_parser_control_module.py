import os
import csv
import json
import time
import base64
import logging
import datetime
import subprocess
from typing import Generator, List

from flask import Flask
import requests


# FIXME ——————————————————————————————————————————————————————————— SETTINGS ———
'''
При соединении модуля с парсером В МОДУЛЕ:
1  Присвоить имя парсера, в отведенную переменную

В ПАРСЕРЕ:
2  Адаптировать get_data_from_all_csv_files_in_cur_dir() под логику парсера
   *metall_service исключение

3  Адаптировать get_data_from_json() под структуру JSON-файла
4  Импортируем данный модуль во все файлы парсера, где выполняется логика
5  Добавляем задержки time.sleep(module.PAUSE) во все циклы for / генераторы
6  Добавляем обработчики ошибок во все файлы парсера, где выполняется логика
7  module.send_error_to_cmc(str(e)[:50]) для отправки ошибки
8  module.parser_pid_saver() для передачи PID в модуль методом os.getpid()
9  module.get_memory_info() для передачи данных о PID процессе парсера в модуль
10 module.send_data_to_adapter() для отправки данных в адаптер
11 module.send_end_parsing_status_cmc() отправка запроса о завершении парсинга
12 Локал тест - {'parser_name': ''} в http://127.0.0.1:PORT/start_parsing
13 Обновить файл с зависимостями
14 Перевести IP после тестов на IP сервера 
'''
PARSER_NAME = 'nlmk'

PARSER_FILENAME = 'nlmk.py'

PARSER_IP = '91.186.197.118'
# PARSER_IP = '127.0.0.1'

MODULE_PORT = 4226

ADAPTER_BASE_URL = 'http://176.57.213.189:8000'
ADAPTER_FULL_URL = f'{ADAPTER_BASE_URL}/upload-raw'
ADAPTER_UPLOAD_SESSION_STATUS_URL = f'{ADAPTER_BASE_URL}/!!!'

USERNAME = 'metinvest'
PASSWORD = 'metall'
auth = f'{USERNAME}:{PASSWORD}'
auth_base64 = base64.b64encode(auth.encode('utf-8')).decode('utf-8')

CMC_URL = 'http://185.178.47.106:4200/receive_data'

NUMBER_OF_NESTED_OBJECT = 500
DELAY_IF_SENDING_ERR = 5

PAUSE = 0.1
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~~~
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_module_{PARSER_NAME}.log',
                    encoding='utf-8', level=logging.ERROR, filemode='w',
                    format=f'%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————— ПРИ СОЕДИНЕНИИ С ПАРСЕРОМ ————


app = Flask(__name__)


def send_error_to_cmc(error:str):
    '''
    Отправляет ошибку на сервер ЦУП

    Args:
        error (str): текстовое описание ошибки
    '''
    try:
        parser_data = {
            'parser_name': PARSER_NAME,
            'status': 'Parsing Error',
            'error': str(error),
        }

        requests.post(CMC_URL, data=parser_data)

    except Exception as e:
        logging.error(f'in send_error_to_cmc: {e}')


@app.route('/start_parsing', methods=['POST'])
def start_parsing():
    '''
    Принимает POST-запрос для запуска парсера
    Запускает парсер в отдельном процессе и отправляет запрос на сервер ЦУП
    '''
    try:
        with open('start_time.txt', 'w') as f:
            start_time = datetime.datetime.now()
            f.write(str(start_time))

        process = subprocess.Popen(
            f'nohup python3 {PARSER_FILENAME} &',
            shell=True
        )

        process_id = process.pid
        with open('pid.txt', 'w') as f:
            f.write(str(process_id))

        parser_data = {
            'parser_name': PARSER_NAME,
            'status': 'Parsing Started',
            'error': None,
        }

        requests.post(CMC_URL, data=parser_data)

        return f'Парсер {PARSER_NAME} начал работу'

    except Exception as e:
        logging.error(f'in start_parsing(): {e}')
        send_error_to_cmc(f'in start_parsing(): {str(e)[:50]}')


def send_end_parsing_status_cmc():
    '''
    Отправляет отчет об окончании парсинга на сервер ЦУП
    '''
    try:
        with open('start_time.txt', 'r') as f:
            start_time_string = f.read()

        start_time = datetime.datetime.strptime(
            start_time_string,
            '%Y-%m-%d %H:%M:%S.%f'
        )
        end_time = datetime.datetime.now()
        time_spent = end_time - start_time

        parser_data = {
            'parser_name': PARSER_NAME,
            'status': f'Parsing was completed for {str(time_spent)[:-4]}',
            'error': None,
        }

        requests.post(CMC_URL, data=parser_data)

    except Exception as e:
        logging.error(f'in send_end_parsing_status_cmc(): {e}')
        send_error_to_cmc(f'in send_end_parsing_status_cmc(): {str(e)[:50]}')


@app.route('/stop_parsing', methods=['POST'])
def stop_parsing():
    '''
    Принимает POST-запрос для остановки парсера
    Использует subprocess для остановки парсера, отправляет данные на сервер ЦУП
    '''
    try:
        with open('pid.txt', 'r') as f:
            parser_pid = f.read()

        subprocess.Popen(['pkill', '-f', parser_pid])

        parser_data = {
            'parser_name': PARSER_NAME,
            'status': 'Parsing Stopped (Forced)',
            'error': None,
        }

        requests.post(CMC_URL, data=parser_data)

    except Exception as e:
        logging.error(f'in stop_parsing(): {e}')
        send_error_to_cmc(f'in stop_parsing(): {str(e)[:50]}')


def parser_pid_saver(pid:int):
    """
    Сохраняет PID переданный от парсера

    Args:
        pid (int): фактический id процесса парсера
    """
    try:
        with open('pid.txt', 'w') as f:
            f.write(str(pid))
            f.close()

    except Exception as e:
        logging.error(f'in parser_pid_saver: {e}')
        send_error_to_cmc(f'in parser_pid_saver: {str(e)[:50]}')


def get_memory_info():
    '''
    Фиксирует данные потребляемой памяти парсером в логах ЦУП
    '''
    try:
        with open('pid.txt', 'r') as f:
            pid = f.read()

        command = f'ps -p {pid} -o pid,%cpu,%mem,rss,vsz,args'

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()

        data_string = stdout.decode()

        lines = data_string.split('\n')

        if len(lines) >= 2:
            second_line = lines[1]
            values = second_line.split()

            cpu = float(values[1])
            mem = float(values[2])
            rss = round(float(values[3]) / 1024)
            # vsz = round(float(values[4]) / 1024)

            ram_formatted_str = 'RAM:{:.1f}% {: 1d}MB '.format(mem, rss)
            cpu_formatted_str = f'CPU:{cpu}%'

            data_to_post = {
                'parser_name': PARSER_NAME,
                'status': 'memory_data',
                'error': None,
                'PID': pid,
                'RAM': ram_formatted_str,
                'CPU': cpu_formatted_str,
            }

            requests.post(CMC_URL, data=data_to_post)

        else:
            logging.error('В get_memory_info: недостаточно строк данных для '
                          'обработки из команды ps в терминале')

    except Exception as e:
        logging.error(f'in get_memory_info(): {e}')
        send_error_to_cmc(f'in get_memory_info(): {str(e)[:50]}')


def get_data_from_json() -> list:
    '''
    Получает данные из самого нового CSV файла в указанной папке

    Returns:
        data (list) список словарей с данными из CSV файла
    '''
    try:
        data = []
        reports_json_dir = 'reports/json'
        json_files_in_reports_folder = os.listdir(reports_json_dir)
        for json_file in json_files_in_reports_folder:
            with open(reports_json_dir + '/' + json_file, 'r', encoding='utf-8') as f:
                loaded_products = json.load(f)
            for product in loaded_products:
                data.append(product)

        return data

    except Exception as e:
        logging.error(f'in get_data_from_json(): {e}')
        send_error_to_cmc(f'in get_data_from_json(): {str(e)[:50]}')


def split_into_chunks() -> Generator[List[dict], None, None]:
    '''
    Разбивает данные из последнего CSV файла на порции

    Yields:
        (list) Порции данных (список словарей)
    '''
    try:
        data = get_data_from_json()
        for i in range(0, len(data), NUMBER_OF_NESTED_OBJECT):
            # time.sleep(PAUSE)
            yield data[i:i+NUMBER_OF_NESTED_OBJECT]

    except Exception as e:
        logging.error(f'in split_into_chunks(): {e}')
        send_error_to_cmc(f'in split_into_chunks(): {str(e)[:50]}')


def send_status_of_start_session():
    '''
    Отправляет статус начала выгрузки данных в ручку
    '''
    try:
        status_data = {'upload_session_status': 'started'}
        status_json = json.dumps(status_data)
        requests.post(
            ADAPTER_UPLOAD_SESSION_STATUS_URL,
            data=status_json,
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        logging.error(f'in send_status_of_start_session(): {e}')
        send_error_to_cmc(f'in send_status_of_start_session(): {str(e)[:50]}')


def send_status_of_finished_session():
    '''
    Отправляет статус окончания выгрузки данных в ручку
    '''
    try:
        status_data = {'upload_session_status': 'finished'}
        status_json = json.dumps(status_data)
        requests.post(
            ADAPTER_UPLOAD_SESSION_STATUS_URL,
            data=status_json,
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        logging.error(f'in send_status_of_start_session(): {e}')
        send_error_to_cmc(f'in send_status_of_start_session(): {str(e)[:50]}')


def send_data_to_adapter():
    '''
    Отправляет данные в адаптер, разбивая их на порции и добавляя информацию
    о парсере
    '''
    try:
        session = requests.Session()
        send_status_of_start_session()
        session.auth = (USERNAME, PASSWORD)

        for chunk in split_into_chunks():
            success_send = False
            delay = 0
            count = 0
            while not success_send:
                chunk_with_parser = {
                    'Parsers1': PARSER_NAME,
                    'data': chunk
                }

                chunk_with_parser_json = json.dumps(
                    chunk_with_parser,
                    ensure_ascii=False
                )

                response = session.post(
                    ADAPTER_FULL_URL,
                    data=chunk_with_parser_json.encode('utf-8')
                )

                response_data = response.json()

                if response_data.get('result') == 'ok':
                    success_send = True
                else:
                    count += 1
                    if count == 1:
                        time.sleep(delay)
                        delay = DELAY_IF_SENDING_ERR
                    elif count == 2 or count == 12 or count == 60 or count % 240 == 0:
                        time.sleep(delay)
                        logging.error(
                            f'in send_data_to_adapter() try: {count}, status: '
                            f'{response.status_code}, {response.text}'
                        )
                        send_error_to_cmc(
                            f'in send_data_to_adapter()\ntry: {count}, status: '
                            f'{response.status_code}\n{response.text[:50]}'
                        )
                    elif count > 2:
                        time.sleep(delay)

        session.close()
        send_status_of_finished_session()

    except Exception as e:
        logging.error(f'in send_data_to_adapter(): {e}')
        send_error_to_cmc(f'in send_data_to_adapter(): {str(e)[:50]}')


if __name__ == '__main__':
    app.run(host=PARSER_IP, port=MODULE_PORT)
