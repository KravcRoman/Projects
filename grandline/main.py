import os
import sys

import requests
import xml.etree.ElementTree as ET

from utils.utils import print_template, write_offers_to_csv, update_progress
from model.offer import Offer
from model.category import Category, build_category_hierarchy, \
    find_category_by_id, find_parent_categories


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import grandline_parser_control_module as module

module.parser_pid_saver(os.getpid())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format=f'%(levelname)s %(asctime)s %(message)s')
# FIXME —————————————————————————————————————————— ПРИ СОЕДИНЕНИИ С МОДУЛЕМ ————


# Устанавливаем переменную окружения "PROJECT_ROOT" в путь до корневой папки проекта
os.environ['PROJECT_ROOT'] = os.path.dirname(os.path.abspath(__file__))

# URL файла YML
url = 'https://grandline.ru/grandline.yml'


try:
    # Загрузка содержимого файла YML
    # print(print_template("Loading the contents of a YML ({}) file...".format(url)))
    response = requests.get(url)
    # STATUS: PID=7692 CPU:30.3% RAM:3.7%  610MB
    response.raise_for_status()
    # STATUS: PID=7692 CPU:32.8% RAM:3.7%  610MB
    # print(print_template("Download completed!"))
    yml_content = response.content

    # Парсинг XML
    xml_root = ET.fromstring(yml_content)

    # Обработка данных YML
    offers = []
    for offer_element in xml_root.findall('.//offer'):

        # Задержка цикла для снижения нагрузки на CPU
        # time.sleep(module.PAUSE)

        offer = Offer.from_xml_element(offer_element)
        offers.append(offer)
        # STATUS: PID=8051 CPU:5.8% RAM:14.4%  2352MB

    categories = []
    for category_element in xml_root.findall('.//category'):

        # Задержка цикла для снижения нагрузки на CPU
        # time.sleep(module.PAUSE)

        category = Category.from_xml_element(category_element)
        categories.append(category)
        # STATUS: PID=8082 CPU:4.9% RAM:17.1%  2800MB

    # Построение иерархии категорий
    category_hierarchy = build_category_hierarchy(categories)
    processed_lines = 0
    total_lines = len(offers)

    # Вывод информации о предложениях
    for offer in offers:
        try:
            selected_category = find_category_by_id(offer.categoryId,           #       ncalls      tottime   percall cumtime   percall  filename:lineno(function)
                                                    category_hierarchy)         # 211582639/561359   76.140    0.000   76.140    0.000   category.py:42(find_category_by_id)

            # Задержка цикла для снижения нагрузки на CPU
            # time.sleep(module.PAUSE)
            # STATUS: PID=7735 CPU:5.3% RAM:16.5%  2697MB

            if selected_category:
                hierarchy_category = find_parent_categories(category_hierarchy,
                                                            selected_category)
                hierarchy_category.reverse()
                hierarchy_category.append(selected_category.name)
                offer.categoryId = ", ".join(hierarchy_category)
            else:
                offer.categoryId = None
            processed_lines += 1
            update_progress(processed_lines, total_lines,  offer.name)
        except Exception as e:
            logging.error(f'in cycle for offer in offers: {e}')

    module.get_memory_info()

    sys.stdout.write('\n')

    write_offers_to_csv(offers)

    module.send_data_to_adapter()
    module.send_end_parsing_status_cmc()

except Exception as e:
    logging.error(f'in main.py: {e}')
    module.send_error_to_cmc(f'in main.py: {str(e)[:50]}')
