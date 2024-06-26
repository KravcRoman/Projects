import os
import sys
from concurrent.futures import ThreadPoolExecutor

from utils.exporter import convert_to_json, remove_old_data, save_to_sqlite
from utils.parser import parsing_product,  parsing_main_page,get_all_links_products
from utils.utils import check_reports_folder_exist,print_template


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import ileko_parser_control_module as module
module.parser_pid_saver(os.getpid())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    level=logging.ERROR, encoding='utf-8', filemode='w',
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


os.environ['PROJECT_ROOT'] = os.path.dirname(os.path.abspath(__file__))
futures = []

def start():
    try:
        DOMAIN = 'https://ileko.com'

        reports_folder = check_reports_folder_exist()

        if not reports_folder:
            sys.exit(1)

        remove_old_data(reports_folder)

        module.get_memory_info()

        print(print_template("Parse links to categories ..."))
        catalog_list = parsing_main_page(DOMAIN)
        all_links_products = get_all_links_products(catalog_list, DOMAIN)

        all_links_products.reverse()
        if not all_links_products:
            print(print_template("Error when parsing links to categories from the site!"))
            return False
        i = 0
        print(print_template("Parse links to products ..."))
        with ThreadPoolExecutor(max_workers=15) as executor:
            results = []
            for product in all_links_products:
                future = executor.submit(parsing_product, product)
                results.append(future)
            for future in results:
                result = future.result()
                if result:
                    print_template(f"Saving in sqlite new product:  {result['Наименование']} ({result['URL товара']})")
                    save_to_sqlite(result, reports_folder)
                    i += 1
        total_count = convert_to_json(reports_folder)
        print(print_template(f"Total count: {total_count}"))
    except Exception as e:
        logging.error(f'in start(): {e}')
        module.send_error_to_cmc(f'in start(): {str(e)[:50]}')


if __name__ == '__main__':
    try:
        start()

        module.send_data_to_adapter()
        module.send_end_parsing_status_cmc()

    except Exception as e:
        logging.error(f'in __main__(): {e}')
        module.send_error_to_cmc(f'in __main__(): {str(e)[:50]}')