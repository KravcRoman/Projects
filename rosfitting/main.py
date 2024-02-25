import os
import time

import openpyxl

from utils.utils import download_file, print_template, write_products_to_csv
from model.product import Product
from sheets import Flancy_09G2S, Flancy_10h17n13m2t, Flancy_12H18N10T_Ispolnenie, Flancy_12H18N10T_Kitaj
from sheets import Flancy_st_20, Krany_nerzh_Rossiya, Krepezh, Otvody_12H18N10T, Perekhody_12H18N10T
from sheets import Trojniki_12H18N10T, Zaglushki_12H18N10T, Flancy_12H18N10T_Rossiya_Lite


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import rosfitting_parser_control_module as module

module.parser_pid_saver(os.getpid())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging

CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format=f'%(levelname)s %(asctime)s %(message)s')
# FIXME —————————————————————————————————————————— ПРИ СОЕДИНЕНИИ С МОДУЛЕМ ————


os.environ['PROJECT_ROOT'] = os.path.dirname(os.path.abspath(__file__))


def start():
    try:
        products: [Product] = []

        if not download_file():
            print_template("Stop. File download error!")
            return False

        workbook = openpyxl.load_workbook('price.xlsx')

        products.extend(Flancy_09G2S.parser(workbook))
        # STATUS: PID=9994 CPU:0.0% RAM:0.8%  127MB
        time.sleep(module.PAUSE)

        products.extend(Flancy_10h17n13m2t.parser(workbook))
        # STATUS: PID=10186 CPU:0.0% RAM:0.8%  124MB
        time.sleep(module.PAUSE)

        products.extend(Flancy_12H18N10T_Ispolnenie.parser(workbook))
        # STATUS: PID=10699 CPU:0.0% RAM:0.8%  126MB
        time.sleep(module.PAUSE)

        products.extend(Flancy_12H18N10T_Kitaj.parser(workbook))
        # STATUS: PID=11003 CPU:0.0% RAM:0.8%  124MB
        time.sleep(module.PAUSE)

        products.extend(Flancy_12H18N10T_Rossiya_Lite.parser(workbook))
        # STATUS: PID=11172 CPU:0.0% RAM:0.8%  125MB
        time.sleep(module.PAUSE)

        products.extend(Flancy_st_20.parser(workbook))
        # STATUS: PID=11487 CPU:4.1% RAM:0.8%  127MB
        time.sleep(module.PAUSE)

        products.extend(Krany_nerzh_Rossiya.parser(workbook))
        # STATUS: PID=11738 CPU:0.0% RAM:0.8%  129MB
        time.sleep(module.PAUSE)

        products.extend(Krepezh.parser(workbook))
        # STATUS: PID=12028 CPU:1.0% RAM:0.8%  127MB
        time.sleep(module.PAUSE)

        products.extend(Otvody_12H18N10T.parser(workbook))
        # STATUS: PID=12174 CPU:3.7% RAM:0.8%  125MB
        time.sleep(module.PAUSE)

        products.extend(Perekhody_12H18N10T.parser(workbook))
        # STATUS: PID=12348 CPU:0.3% RAM:0.8%  125MB
        time.sleep(module.PAUSE)

        products.extend(Trojniki_12H18N10T.parser(workbook))
        # STATUS: PID=12592 CPU:0.1% RAM:0.8%  125MB
        time.sleep(module.PAUSE)

        products.extend(Zaglushki_12H18N10T.parser(workbook))
        # STATUS: PID=12777 CPU:0.0% RAM:0.8%  127MB
        time.sleep(module.PAUSE)

        print(print_template(f"Done! Found {len(products)} products."))
        print(print_template("Save to file..."))

        write_products_to_csv(products)
        # STATUS: PID=12965 CPU:0.1% RAM:0.8%  128MB

        # Отправляем в ЦУП данные о нагрузке на систему
        module.get_memory_info()
        # STATUS: PID=12796 CPU:3.3% RAM:0.8%  127MB

        module.send_data_to_adapter()

        print(print_template("Completed."))

        # Отправлем в ЦУП запрос для изменения статуса парсинга
        # (окончен/ожидает начала парсинга)
        module.send_end_parsing_status_cmc()

    except Exception as e:
        logging.error(f'in main.py: {e}')
        module.send_error_to_cmc(f'in main.py: {str(e)[:50]}')


if __name__ == '__main__':
    start()
