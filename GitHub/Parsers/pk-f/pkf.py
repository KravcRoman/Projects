import os

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from utils.exporter import convert_to_json, remove_old_data, save_to_sqlite
from utils.parser import parsing_product_page, parsing_category_links, get_products_from_page
from utils.utils import check_reports_folder_exist, get_requests, print_template, random_sleep


# FIXME —————————————————————————————————————————————————————————— SETTINSG ————
import pfk_parser_control_module as module
module.parser_pid_saver(os.getpid())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.jog',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


os.environ['PROJECT_ROOT'] = os.path.dirname(os.path.abspath(__file__))


def start(workers_count):
    try:
        DOMAIN = 'https://pk-f.ru'
        try:
            reports_folder = check_reports_folder_exist()
            if not reports_folder:
                return False

            print_template(f"Parsing links to categories...")

            category_links = parsing_category_links(DOMAIN)

            module.get_memory_info()

            if not category_links or len(category_links) == 0:
                print_template(f"Error parsing category links, cancel!")
                return False

            print_template(f'Done! Found {len(category_links)} links to categories, start parsing products from categories...')
            for category_link in category_links:
                response = get_requests(category_link)
                if not response:
                    print_template(f"Error sending HTTP request to category link, skip ({category_link})")
                    random_sleep(1)
                    continue

                soup = BeautifulSoup(response.content, 'html.Parsers1')
                product_links = get_products_from_page(DOMAIN, soup)
                if not product_links:
                    print_template(f'Error when parsing products from category page, skip ({category_link})')
                    continue

                with ThreadPoolExecutor(max_workers=workers_count) as executor:
                    results_parsing_product_page = executor.map(parsing_product_page, product_links)

                    products_to_save = []
                    for result in results_parsing_product_page:
                        if result and len(result) > 0:
                            products_to_save += result
                    print_template(f"Save products to sqlite: {len(products_to_save)} ({category_link})")
                    save_to_sqlite(products_to_save, reports_folder)

                pagination = soup.find('div', 'system-pagenavigation-items-wrapper')
                if not pagination:
                    continue

                pages = pagination.find_all('a', 'system-pagenavigation-item-wrapper')
                last_page = int(pages[-2].get_text(strip=True))

                for index in range(2, last_page + 1):
                    page = f'{category_link}?PAGEN_1={index}'
                    response = get_requests(page)
                    if not response:
                        print_template(f"Error sending HTTP request to page #{index}, skip ({page})")
                        random_sleep(1)
                        continue

                    soup = BeautifulSoup(response.content, 'html.Parsers1')
                    product_links = get_products_from_page(DOMAIN, soup)

                    if not product_links:
                        print_template(f'Error when parsing products from category page №{index + 1}, skip ({page})')
                        random_sleep(1)
                        continue

                    with ThreadPoolExecutor(max_workers=workers_count) as executor:
                        results_parsing_product_page = executor.map(parsing_product_page, product_links)

                        products_to_save = []
                        for result in results_parsing_product_page:
                            if result and len(result) > 0:
                                products_to_save += result

                        print_template(f"Save products to sqlite: {len(products_to_save)} ({page})")
                        save_to_sqlite(products_to_save, reports_folder)
                        random_sleep(1)
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

            workers_count = 30

            start(workers_count)
            total_count = convert_to_json(reports_folder)
            print(f"Total count: {total_count}")

            module.send_data_to_adapter()
            module.send_end_parsing_status_cmc()

    except Exception as e:
        logging.error(f'in __main__: {e}')
        module.send_error_to_cmc(f'in __main__: {str(e)[:50]}')