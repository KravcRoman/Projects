import json
import os
import sqlite3

from utils.utils import print_template


# FIXME —————————————————————————————————————————————————————————— SETTINSG ————
import pkf_parser_control_module as module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.jog',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


FILENAME = "pk-f-ru"


def remove_old_data(reports_folder):
    try:
        report_file_sqlite = os.path.join(reports_folder, 'sqlite', f'{FILENAME}.sqlite')
        report_file_json = os.path.join(reports_folder, 'sqlite', f'{FILENAME}.json')
        report_file_all_json = os.path.join(reports_folder, 'products.json')
        try:
            if os.path.exists(report_file_sqlite):
                print_template(f"Remove old data {report_file_sqlite}...")
                os.remove(report_file_sqlite)
            if os.path.exists(report_file_json):
                print_template(f"Remove old data {report_file_json}...")
                os.remove(report_file_json)
            if os.path.exists(report_file_all_json):
                print_template(f"Remove old data {report_file_all_json}...")
                os.remove(report_file_all_json)
        except Exception as ex:
            print(print_template(f'Error: {ex}'))

    except Exception as e:
        logging.error(f'in remove_old_data: {e}')
        module.send_error_to_cmc(f'in remove_old_data: {str(e)[:50]}')

def save_to_sqlite(products, reports_folder):
    try:
        try:
            report_file = os.path.join(reports_folder, 'sqlite', FILENAME)

            conn = sqlite3.connect(report_file + ".sqlite")
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS json_data (id INTEGER PRIMARY KEY, data TEXT UNIQUE)''')

            for product in products:
                try:
                    data = json.dumps(product, ensure_ascii=False, indent=4)
                    cursor.execute("INSERT OR IGNORE INTO json_data (data) VALUES (?)", (data,))
                except:
                    continue
            conn.commit()
        except Exception as ex:
            print(print_template(f'Error: {ex}'))
            return False

    except Exception as e:
        logging.error(f'in save_to_sqlite: {e}')
        module.send_error_to_cmc(f'in save_to_sqlite: {str(e)[:50]}')

def convert_to_json(reports_folder):
    try:
        try:
            sqlite_report_file = os.path.join(reports_folder, 'sqlite', f'{FILENAME}.sqlite')
            if not os.path.exists(sqlite_report_file):
                return False

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

            print_template(f"Convert to json {sqlite_report_file}...")

            total_report_file = os.path.join(reports_folder, 'products.json')
            with open(total_report_file, 'w', encoding="utf-8") as file:
                json.dump(data_list, file, ensure_ascii=False, indent=4)
            return len(data_list)
        except Exception as ex:
            print(print_template(f'Error: {ex}'))
            return False

    except Exception as e:
        logging.error(f'in convert_to_json: {e}')
        module.send_error_to_cmc(f'in convert_to_json: {str(e)[:50]}')




