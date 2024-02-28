from bs4 import BeautifulSoup
from utils.utils import get_current_time, get_requests, print_template, random_sleep
import requests
from collections import OrderedDict


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import ileko_parser_control_module as module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import logging
import os
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    level=logging.ERROR, encoding='utf-8', filemode='w',
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


def parsing_product(url):
    try:
        try:
            random_sleep(0.5)
            response = get_requests(url)
            if not response:
                print_template(f"Error getting product page, skip: {url}")
                random_sleep(1)
                return False

            product = {}

            soup = BeautifulSoup(response.content, 'html.Parsers1')

            page_title = soup.findAll('div', class_='col-md-12')
            page_title = page_title[1].find('h1', id='pagetitle').get_text(strip=True).replace('"', "'").replace('\xa0',' ')

            product_wrapper = soup.find('div', 'section-content-wrapper')
            if not product_wrapper or not page_title:
               print_template(f"Error when parsing the product page, the key element 'section-content-wrapper/pagetitle' is missing, skip. ({url})")
               random_sleep(1)
               return False

            product['Наименование'] = page_title
            product['URL товара'] = url
            product['Время парсинга (мск)'] = get_current_time()

            try:

                char_wrapp = soup.find('div', class_='tab-content')
                char_rows = char_wrapp.find_all('tr', class_='char')

                for char_row in char_rows:
                    char_name = char_row.find('td',  class_='char_name').find('span').get_text(strip=True)
                    char_value = char_row.find('td', class_='char_value').find('span').get_text(strip=True)

                    product[char_name] = char_value
            except :
                try:
                    props_table = soup.find('table',  class_='props_table')
                    char_rows = props_table.find_all('tr', class_='char')

                    for char_row in char_rows:
                        char_name = char_row.find('td', class_='char_name').find('span').get_text(strip=True)
                    char_value = char_row.find('td', class_='char_value').find('span').get_text(strip=True)

                    product[char_name] = char_value
                except :
                    pass

            phone_div = soup.find('div', class_='phone big')

            phone_number = phone_div.find('a').get_text(strip=True)

            product['Телефон'] = phone_number
            breadcrumb_ul = soup.find('ul', id='navigation')

            if breadcrumb_ul:
                breadcrumb_items = breadcrumb_ul.find_all('li')


                if len(breadcrumb_items) >= 3:
                    third_category = breadcrumb_items[2].find('span', itemprop='name').get_text(strip=True)

                if third_category == "Нержавеющий лист":
                    product['Категория'] = 'Листы'
                elif third_category == "Рулоны нержавеющие":
                    product['Категория'] = 'Рулоны'
                elif third_category == "Круги из нержавеющей стали":
                    product['Категория'] = 'Круги'
                elif third_category == "Заготовки из нержавеющих и ферритных марок сталей fdf":
                    product['Категория'] = 'Заготовки для оснастки, пресс-форм и штампов из нержавеющей стали'
                elif third_category == "Заготовки для оснастки, пресс-форм и штампов из нержавеющей стали":
                    product['Категория'] = 'Заготовки для оснастки, пресс-форм и штампов'
                elif third_category == "Труба из обечаек нержавющая":
                    product['Категория'] = 'Труба из обечаек'
                elif third_category == "Плиты из нержавеющей стали":
                    product['Категория'] = 'Плиты стальные'
                elif third_category == "Обечайки из нержавеющей стали":
                    product['Категория'] = 'Обечайки'
                else:
                    product['Категория'] = third_category
            else:
                product['Категория'] = None

            a_elements = soup.select('div.io_wrapper a')

            price = {}

            for a in a_elements:
                city = a.get_text(strip=True)

                href = a.get('href')

                response = get_requests(href)

                if response:
                    soup = BeautifulSoup(response.content, 'html.Parsers1')
                    price_span = soup.find('span', itemprop='price')

                    if price_span:
                        price[city] = price_span.get_text(strip=True)
                    else:
                        price[city] = None
                else:
                    price[city] = None

            product['Цена'] = price


            random_sleep(0.5)

            return product
        except Exception as e:

            return False
    except Exception as e:
        logging.error(f'in parsing_product(): {e}')
        module.send_error_to_cmc(f'in parsing_product(): {str(e)[:50]}')

def parsing_main_page(DOMAIN):
    try:
        url = f'{DOMAIN}/product/'
        response = get_requests(url)

        soup = BeautifulSoup(response.text, 'html.Parsers1')

        sidebar = soup.find('aside', class_='sidebar')

        links = sidebar.find_all('a')
        catalog_links = []

        for link in links:
            href = link.get('href')
            catalog_links.append(href)
        catalog_links = [item for item in catalog_links if item]
        return catalog_links
    except Exception as e:
        logging.error(f'in parsing_main_page(): {e}')
        module.send_error_to_cmc(f'in parsing_main_page(): {str(e)[:50]}')


def get_all_links_products(catalog_list, DOMAIN):
    try:
        all_links = []

        for catalog_item in catalog_list:
            count = 0
            catalog_url = f"{DOMAIN}{catalog_item}"
            session = requests.Session()

            while catalog_url:

                response = session.get(catalog_url)
                soup = BeautifulSoup(response.text, 'html.Parsers1')
                products_table = soup.find('table')

                if products_table:
                    item_name_cells = soup.find_all('td', class_='item-name-cell')

                    for item_name_cell in item_name_cells:
                        link = item_name_cell.find('a', class_='dark_link')
                        if link:
                            link_href = link.get('href')
                            count += 1
                            all_links.append(f'{DOMAIN}{link_href}')

                pagination_ul = soup.find('ul', class_='pagination')

                if pagination_ul:
                    next_page_li = pagination_ul.find('li', class_='next')

                    if next_page_li:
                        next_page_link = next_page_li.find('a')
                        if next_page_link:
                            catalog_url = f'{DOMAIN}{next_page_link.get("href")}'
                        else:
                            break
                    else:
                        break
                else:
                    break
        ordered_dict = OrderedDict.fromkeys(all_links)
        unique_links = list(ordered_dict.keys())
        return unique_links
    except Exception as e:
        logging.error(f'in get_all_links_products(): {e}')
        module.send_error_to_cmc(f'in get_all_links_products(): {str(e)[:50]}')