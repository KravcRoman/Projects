import os

from concurrent.futures import ThreadPoolExecutor
from utils.exporter import convert_to_json, remove_old_data, save_to_sqlite, download_price_list
from utils.parser import check_product_in_search, parsing_product_page, parsing_xlsx_file, second_city_check_product_in_search, second_city_parsing_product_page
from utils.utils import check_reports_folder_exist, print_template, random_sleep


# FIXME —————————————————————————————————————————————————————————— SETTINSG ————
import ostm_parser_control_module as module
module.parser_pid_saver(os.getpid())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


os.environ['PROJECT_ROOT'] = os.path.dirname(os.path.abspath(__file__))


def start(workers, second_city):
    try:
        try:
            if second_city:
                price_list = 'https://ost-ya.ru/PriceList/'
            else:
                price_list = 'https://ost-m.ru/PriceList/'

            reports_folder = check_reports_folder_exist()
            if not reports_folder:
                return False

            print_template(f"Download price list...")

            price_list_path = download_price_list(price_list, reports_folder, second_city)
            if not price_list_path:
                return False

            products_xlsx = parsing_xlsx_file(price_list_path)
            if not products_xlsx:
                return False

            print_template(f"Done! Found {len(products_xlsx)} products in .xlsx file")
            batch_size = workers
            batches = [products_xlsx[i:i + batch_size] for i in range(0, len(products_xlsx), batch_size)]

            module.get_memory_info()

            for batch in batches:
                products_search = []
                with ThreadPoolExecutor(max_workers=workers) as executor_search:
                    if second_city:
                        results_check_product_in_search = executor_search.map(second_city_check_product_in_search, batch)
                    else:
                        results_check_product_in_search = executor_search.map(check_product_in_search, batch)

                    for result in results_check_product_in_search:
                        if result and len(result) > 0:
                            products_search.append(result)

                products_parsing = []
                with ThreadPoolExecutor(max_workers=workers) as executor_parse:
                    if second_city:
                        results_parsing_product_page = executor_parse.map(second_city_parsing_product_page, products_search)
                    else:
                        results_parsing_product_page = executor_parse.map(parsing_product_page, products_search)
                    for result in results_parsing_product_page:
                        if result and len(result) > 0:
                            products_parsing.append(result)
                    print_template(f'Save products to sqlite: {len(products_parsing)}')
                    save_to_sqlite(products_parsing, reports_folder)
                return True
        except Exception as ex:
            print_template(f'Error: {ex}')
            return False

    except Exception as e:
        logging.error(f'in start: {e}')
        module.send_error_to_cmc(f'in start: {str(e)[:50]}')

if __name__ == '__main__':
    try:
        reports_folder = check_reports_folder_exist()
        if reports_folder:
            remove_old_data(reports_folder)

            workers_count = 10

            start(workers_count, second_city=True)
            start(workers_count, second_city=False)
            total_count = convert_to_json(reports_folder)
            print(f"Total count: {total_count}")

            module.send_data_to_adapter()
            module.send_end_parsing_status_cmc()

    except Exception as e:
        logging.error(f'in __main__: {e}')
        module.send_error_to_cmc(f'in __main__: {str(e)[:50]}')