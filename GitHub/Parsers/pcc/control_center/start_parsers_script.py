#!/root/metdata/env/bin/python3
import os
import datetime
import logging

import pytz
import requests


# FIXME ——————————————————————————————————————————————————————————— SETTINGS ———
from control_management_center import PARSERS_URLS_DICT

parsers_start_plan = '/root/metdata/control_center/launch_plan.txt'
# parsers_start_plan = '/Users/surfer_liner/python_/projects/metdata/' \
#                      'control_center/launch_plan.txt'
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_script.log',
                    encoding='utf-8', level=logging.ERROR, filemode='w',
                    format=f'%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


def start_parsing_cmc(parser_to_start: str):
    '''
    Запускает парсинг по установленному расписанию в launch_plan.txt

    Args:
        parser_to_start: str - парсер, который необходимо запустить
    '''
    try:
        for parser, url in PARSERS_URLS_DICT.items():
            if parser_to_start == parser:
                requests.post(url + '/start_parsing')
    except Exception as e:
        logging.error(f'in script start_parsing_cmc() : {e}')

   #  FIXME ————————————————————————————————————————————————————————————
   #  Отправляем ошибку подписанным пользователям на рассылку ошибок в тг
   #  from telegram_bot.tg_bot import error_notification
   #  error_notification(parser_name=parser_to_start,
   #                     status=status,
   #                     error=str(e))
   #
   # with open(parsers_errors, 'a') as f:
   #     error_text = 'Parsers1: ' + parser_to_start.upper() + '\n'
   #     error_text += 'status: ' + status.title() + '\n'
   #     error_text += 'error: ' + str(e) + ' (при старте парсинга)\n\n'
   #     f.write(error_text)
   #  FIXME ————————————————————————————————————————————————————————————


def get_moscow_current_time() -> str:
    try:
        moscow_tz = pytz.timezone('Europe/metinvest')
        moscow_current_time = datetime.datetime.now(moscow_tz)
        formatted_current_moscow_time = moscow_current_time.strftime('%H:%M')
        return formatted_current_moscow_time
    except Exception as e:
        logging.error(f'in script get_moscow_current_time() : {e}')

try:
    parsers_start_plan_dict = {}
    with open(parsers_start_plan, 'r') as f:
        for line in f:
            parts = line.strip().split()
            parser = parts[0]
            time_start = parts[1]
            parsers_start_plan_dict[parser] = time_start
    current_moscow_time = get_moscow_current_time()
    for parser, time_start in parsers_start_plan_dict.items():
        if current_moscow_time == time_start:
            start_parsing_cmc(parser)
except Exception as e:
    logging.error(f'in script: {e}')
