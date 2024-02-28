"""
Название программы: Центр Управления Парсерами - ЦУП
Описание: Запуск и контроль системы парсеров
Версия Python: 3.11.4
Автор: surfer_liner
"""

import os
import datetime
import logging

import pytz
import requests
from flask import Flask, request


# FIXME ——————————————————————————————————————————————————————————— SETTINGS ———
'''
При добавлении нового парсера:
1  Добавить в файл расписания запусков (launch_plan.txt) новый парсер с 
   установленным временем запуска в формате: ПАРСЕР_пробел_ВРЕМЯ(чч:мм) мск    
2  Добавить в данном файле, в PARSERS_URLS_DICT парсер и его URL 
3  Добавить в боте в словарь parsers_status_dict новый парсер и начальный статус    
'''

PARSERS_URLS_DICT = {
    'grandline': 'http://91.186.197.118:4202',
    'severstal': 'http://92.63.179.116:4204',
    'rosfitting': 'http://92.63.179.116:4206',
    'sds_center': 'http://92.63.179.116:4208',
    'intormetall': 'http://92.63.179.116:4210',
    'metall_service': 'http://92.63.179.116:4216',
    'inrost_group': 'http://92.63.179.116:4218',
    'russteels' : 'http://92.63.179.116:4220',
    'mmk': 'http://92.63.179.116:4222',
    'santech': 'http://91.186.197.118:4224',
    'nlmk': 'http://91.186.197.118:4226',
    'medexe': 'http://91.186.197.118:4228',
    'transsibmetall': 'http://92.63.179.116:4230',
    'ileko': 'http://92.63.179.116:4232',
    'inoxpoint': 'http://92.63.179.116:4234',
    'listmet': 'http://92.63.179.116:4236',
    'orinnox': 'http://91.186.197.118:4238',
    'pkf': 'http://91.186.197.118:4240',
    'kontinental': 'http://91.186.197.118:4242',
    'steelx': 'http://91.186.197.118:4244',
    'ostm': 'http://91.186.197.118:4246',
}

IP_CMC = '185.178.47.106'
# IP_CMC = '0.0.0.0'

PORT_CMC = 4200

script_path = '/root/metdata/venv/bin/python3 '\
              '/root/metdata/control_center/start_parsers_script.py'
# script_path = '/Users/surfer_liner/python_/projects/metdata/venv/bin/python3 ' \
#               '/Users/surfer_liner/python_/projects/metdata/control_center/' \
#               'start_parsers_script.py'

parsers_logs_folder = 'logs_by_days/'

parsers_start_plan = 'launch_plan.txt'
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_cmc.log',
                    encoding='utf-8', level=logging.ERROR, filemode='w',
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————

# Создаем экземпляр Flask сервера
app = Flask(__name__)


@app.route('/receive_data', methods=['POST'])
def receive_data() -> str:
    '''
    Маршрут принимает POST-запросы с данными от парсеров

    Ожидаемые параметры POST-запроса:
    - parser_name: идентификатор парсера, отправляющего данные
    - status: данные о состоянии парсера
    - error: ошибка, если есть

    Return:
        str - состояние записи в лог-файл
    '''
    try:
        # Извлекаем данные из запроса
        parser_name = request.form.get('parser_name')
        status = request.form.get('status')
        error = request.form.get('error')

        # Формируем текущее время в Москве
        current_moscow_time = pytz.timezone('Europe/metinvest')
        current_moscow_date = datetime.datetime.now(current_moscow_time)
        formatted_time = current_moscow_date.strftime('%H:%M:%S')

        # Формируем имя лог-файла
        file_name = current_moscow_date.strftime('%d-%m-%y.txt')

        # Если есть ошибка - пушим пользователей через тг бота,
        # фиксируем время, имя парсера, его статус и ошибку
        if error is not None:


            # FIXME Когда исправишь - в боте включи кнопки вкл/откл уведомлений
            # Присылаем уведомление об ошибке пользователям, подписанных на
            # уведомления об ошибке через тг-бота
            # with open(parsers_errors, 'a') as f:
            #     error_text = 'Parsers1: ' + parser_name.upper() + '\n'
            #     error_text += 'status: ' + status.title() + '\n'
            #     error_text += 'error: ' + error + '\n\n'
            #     f.write(error_text)
            # import telegram_bot.tg_bot.error_notification
            # error_notification(parser_name=parser_name, status=status, error=error)
            # FIXME Когда исправишь - в боте включи кнопки вкл/откл уведомлений


            # Фиксируем в лог-файл время, имя парсера, его статус и ошибку
            with open(parsers_logs_folder + file_name, 'a+') as f:
                f.write(f'{formatted_time} parser {parser_name.upper()}\n'
                        f'STATUS:\t{status}\n!ERROR:\t{error}\n\n')
            # Ответ клиенту
            return 'Ошибка записана'

        # Иначе, если получены данные о ресурсопотреблении памяти
        elif status == 'memory_data':

            # Извлекаем данные
            parser_name = request.form.get('parser_name')
            pid = request.form.get('PID')
            ram = request.form.get('RAM')
            cpu = request.form.get('CPU')

            # Добавляем к файлу логов к полученному парсеру записи о ресурсах памяти
            with open(parsers_logs_folder + file_name, 'a+') as f:
                f.write(f'{formatted_time} parser {parser_name.upper()}\n'
                        f'STATUS: PID={pid} {cpu} {ram}\n\n')
            # Ответ клиенту
            return 'Данные о памяти записаны'

        # Иначе если получили статус начала парсинга - фиксируем в лог-файл
        # время, имя, парсера и его статус
        elif status == 'Parsing Started':
            with open(parsers_logs_folder + file_name, 'a+') as f:
                f.write(f'{formatted_time} parser {parser_name.upper()}\n'
                        f'STATUS: {status}\n\n')
            # Ответ клиенту
            return 'Парсинг начался'

        # Иначе если получили статус окончания парсинга фиксируем в лог-файл
        # время, имя парсера и его статус

        elif 'Parsing was completed for' in status:
            with open(parsers_logs_folder + file_name, 'a+') as f:
                f.write(f'{formatted_time} parser {parser_name.upper()}\n'
                        f'STATUS: {status}\n\n')
            # Ответ клиенту
            return 'Парсинг выполнен'

        # Иначе если получили статус принудительно окончания - фиксируем в
        # лог-файл время, имя парсера и его статус
        elif status == 'Parsing Stopped (Forced)':
            with open(parsers_logs_folder + file_name, 'a+') as f:
                f.write(f'{formatted_time} parser {parser_name.upper()}\n'
                        f'STATUS: {status}\n\n')
            # Ответ клиенту
            return 'Парсинг остановлен'

    # Ловим ошибку в логике функции
    except Exception as e:
        logging.error(f'in receive_data(): {e}')


def add_cron_job() -> str:
    '''
    Запускает CRON для своевременного запуска парсеров

    Returns:
        str - состояние запуска CRON'а
    '''
    try:
        # Устанавливаем периодичность выполнения кроном скрипта
        period_start_checker = '* * * * *'
        # Команда для баша
        bash = '/bin/bash -c'

        # Формируем команду для запуска задачи в кроне
        command_to_add = f"{period_start_checker} {bash} '{script_path}'"

        # Запускаем команду в кроне
        os.system(f'(crontab -l; echo "{command_to_add}") | crontab -')

        # Проверка вывода
        result = os.system('crontab -l')

        if result == 0:
            return 'Парсеры ожидают своей минуты\nCron запущен, скрипт выполняетя'
        else:
            return 'Cron не запущен'

    # Обработчик ошибок функции
    except Exception as e:
        logging.error(f'in add_cron_job(): {e}')
        return f'При запуске cron произошла ошибка: {e}'


def remove_cron_job() -> str:
    '''
    Останавливает крон
    Перед запуском необходимо убедиться, что скрипт обладает необходимыми
    правами на исполнение

    Returns:
        str - состояние остановки CRON'а
    '''
    try:
        # Формируем команду для удаления задачи из крона
        command_to_remove = f'crontab -r'

        # Удаляем задачи из крона
        os.system(command_to_remove)

        # Пушим в бота
        return "Процесс cron'a остановлен"

    # Ловим ошибку функции
    except Exception as e:
        logging.error(f'in remove_cron_job(): {e}')
        return f"Произошла ошибка при остановке cron'a: {e}"


def finish_parsing_cmc() -> str:
    '''
    Останавливает парсинг на всех парсерах и убивает процесс cron'a

    Returns:
        str - состояние остановки парсеров
    '''
    # Останавливаем парсеры
    try:
        for parser_url in PARSERS_URLS_DICT.values():
            requests.post(parser_url + '/stop_parsing')
        return "Парсеры остановлены\n"

    # Ловим ошибку в логике функции
    except Exception as e:
        logging.error(f'in finish_parsing_cmc(): {e}')
        return f'Произошла ошибка при остановке парсеров: {e}\n\n'


if __name__ == '__main__':
    app.run(IP_CMC, port=PORT_CMC)
