import json
import os
import sqlite3

from utils.utils import print_template


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import nlmk_parser_control_module as module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    level=logging.ERROR, encoding='utf-8', filemode='w',
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


FILENAME = "nlmk-shop"


def remove_old_data(reports_folder, cities):
    try:
        for city in cities:
            try:
                report_file = os.path.join(reports_folder, 'sqlite', f'{city}-{FILENAME}.sqlite')
                if os.path.exists(report_file):
                    print(print_template(f"Remove old data {report_file}..."))
                    os.remove(report_file)
            except:
                print(print_template(f"Error when deleting old file: {report_file}"))
    except Exception as e:
        logging.error(f'in remove_old_data: {e}')
        module.send_error_to_cmc(f'in remove_old_data: {str(e)[:50]}')

def save_to_sqlite(datetime_filename, products, reports_folder):
    """
    Сохраняет данные в базу данных SQLite.
    Args:
        datetime_filename (str): Название файла.
        data (dict or list): Данные для сохранения.
        reports_folder (str): Путь к папке для сохранения файла.
    Returns:
        None
    """
    try:
        try:
            report_file = os.path.join(reports_folder, 'sqlite', datetime_filename + FILENAME)

            conn = sqlite3.connect(report_file + ".sqlite")
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS json_data (id INTEGER PRIMARY KEY, data TEXT)''')

            for product in products:
                try:
                    data = json.dumps(product, ensure_ascii=False, indent=4)
                    cursor.execute("INSERT INTO json_data (data) VALUES (?)", (data,))
                except:
                    continue
            conn.commit()
        except:
            return False
    except Exception as e:
        logging.error(f'in save_to_sqlite: {e}')
        module.send_error_to_cmc(f'in save_to_sqlite: {str(e)[:50]}')

def convert_to_json(reports_folder, cities):
    """
    Конвертирует данные из файлов базы данных SQLite в файлы JSON.
    Args:
        reports_folder (str): Путь к папке, где хранятся файлы отчетов.
        cities (list): Список городов для конвертации данных.
    Returns:
        None
    """
    try:
        total = 0
        for city in cities:
            try:
                sqlite_report_file = os.path.join(reports_folder, 'sqlite', f'{city}-{FILENAME}.sqlite')

                if not os.path.exists(sqlite_report_file):
                    continue

                json_report_file = os.path.join(reports_folder, 'json', f'{city}-{FILENAME}.json')

                conn = sqlite3.connect(sqlite_report_file)
                cursor = conn.cursor()

                cursor.execute("SELECT data FROM json_data")
                rows = cursor.fetchall()
                conn.close()

                data_list = []

                for row in rows:
                    try:
                        data_list.append(json.loads(row[0]))
                    except:
                        continue

                total += len(data_list)

                print(print_template(f"Convert to json {sqlite_report_file}..."))

                with open(json_report_file, 'w', encoding="utf-8") as file:
                    json.dump(data_list, file, ensure_ascii=False, indent=4)
            except:
                continue
        return total
    except Exception as e:
        logging.error(f'in convert_to_json: {e}')
        module.send_error_to_cmc(f'in convert_to_json: {str(e)[:50]}')