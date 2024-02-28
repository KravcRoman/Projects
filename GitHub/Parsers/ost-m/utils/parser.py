import openpyxl
import urllib.parse

from bs4 import BeautifulSoup
from utils.utils import get_current_time, get_requests, print_template


# FIXME —————————————————————————————————————————————————————————— SETTINSG ————
import ostm_parser_control_module as module
module.parser_pid_saver(os.getpid())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging
import os
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.jog',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————



def parsing_xlsx_file(price_list_path):
    try:
        workbook = openpyxl.load_workbook(price_list_path)
        sheet = workbook.active

        products = []

        for row in sheet.iter_rows(min_row=8, values_only=True):
            non_empty_count = sum(1 for cell in row if cell)
            if non_empty_count >= 2:
                product = {
                    'Наименование': str(row[1]).replace('"', "'").replace('\xa0', ' ').strip(),
                    'Артикул': str(row[0]).replace('"', "'").replace('\xa0', ' ').strip(),
                    'Ед. изм.': str(row[2]).replace('"', "'").replace('\xa0', ' ').strip(),
                    'Цена': str(row[3]).replace('"', "'").replace('\xa0', ' ').strip()
                }
                products.append(product)
        return products

    except Exception as e:
        logging.error(f'in parsing_xlsx_file: {e}')
        module.send_error_to_cmc(f'in parsing_xlsx_file: {str(e)[:50]}')

def second_city_check_product_in_search(product: dict):
    try:
        try:
            name = product.get("Наименование")
            if not name:
                return False

            encoded_name = urllib.parse.quote(name.encode('windows-1251'))
            url = f'https://ost-ya.ru/search/?q={encoded_name}'

            response = get_requests(url)
            if response is False:
                print_template(f'Error (HTTP) parsing product {url}')
                return False

            soup = BeautifulSoup(response.content, 'html.Parsers1')
            section = soup.find('section', 'search-result')
            if not section:
                return False

            articles = section.find_all('article', 'search-item')

            if len(articles) > 0:
                for article in articles:
                    article_header = article.find('h4')
                    if article_header.get_text(strip=True).replace('"', "'").replace('\xa0', ' ').replace(' ', '') == name.replace('"', "'").replace('\xa0', ' ').replace(' ', ''):
                        link = article_header.find('a').get('href')
                        product['URL товара'] = f'https://ost-ya.ru{link}'
                        return product
                    else:
                        continue
            else:
                return False
        except Exception as ex:
            print(print_template(f'Error: {ex} ({product.get("URL товара")})'))
            return False

    except Exception as e:
        logging.error(f'in second_city_check_product_in_search: {e}')
        module.send_error_to_cmc(f'in second_city_check_product_in_search: {str(e)[:50]}')

def check_product_in_search(product: dict):
    try:
        try:
            article = product.get("Артикул")
            if not article:
                return False

            url = f'https://ost-m.ru/catalog/?q={article}'
            response = get_requests(url)
            if response is False:
                print_template(f'Error (HTTP) parsing product {url}')
                return False

            soup = BeautifulSoup(response.content, 'html.Parsers1')
            table = soup.find('div', 'table-responsive')

            if not table:
                return False

            tr = table.find_all('tr')
            if len(tr) > 1:
                link = tr[1].find('a').get('href')
                product['URL товара'] = f'https://ost-m.ru{link}'
                return product
            else:
                return False
        except Exception as ex:
            print(print_template(f'Error: {ex} ({product.get("URL товара")})'))
            return False

    except Exception as e:
        logging.error(f'in check_product_in_search: {e}')
        module.send_error_to_cmc(f'in check_product_in_search: {str(e)[:50]}')

def second_city_parsing_product_page(product: dict):
    try:
        try:
            url = product.get('URL товара')
            if not url:
                return False

            response = get_requests(url)
            if response is False:
                print_template(f'Error (HTTP) parsing product {url}')
                return False

            soup = BeautifulSoup(response.content, 'html.Parsers1')

            breadcrumbs = soup.find('nav', 'path')
            if breadcrumbs:
                breadcrumb_items = breadcrumbs.find_all('a', '')
                if breadcrumb_items:
                    if len(breadcrumb_items) > 1:
                        product['Раздел'] = breadcrumb_items[1].get_text(strip=True)
                    if len(breadcrumb_items) > 2:
                        product['Категория'] = breadcrumb_items[2].get_text(strip=True)

            detailed_desc = soup.find('div', 'detailed-desc')
            if not detailed_desc:
                return False

            elements_p = detailed_desc.find_all('p')
            for element in elements_p:
                if 'Артикул' in element.get_text(strip=True):
                    product['Артикул'] = element.get_text(separator='', strip=True).replace('Артикул:', '')
                    continue

                element = element.get_text(separator='#', strip=True)
                characteristics = element.split('#')
                if len(characteristics) > 0:
                    for attribute in characteristics:
                        if 'Описание' in attribute:
                            continue
                        if ':' in attribute:
                            attribute = attribute.replace('"', "'").replace('\xa0', ' ')
                            attribute_split = attribute.split(':')
                            product[str(attribute_split[0]).strip()] = ' '.join(attribute_split[1:]).strip()
                        else:
                            continue
            product['Время парсинга (мск)'] = get_current_time()
            return product
        except Exception as ex:
            print(print_template(f'Error: {ex} ({product.get("URL товара")})'))
            return False

    except Exception as e:
        logging.error(f'in second_city_parsing_product_page: {e}')
        module.send_error_to_cmc(f'in second_city_parsing_product_page: {str(e)[:50]}')

def parsing_product_page(product):
    try:
        try:
            url = product.get('URL товара')
            if not url:
                return False

            response = get_requests(url)
            if response is False:
                print_template(f'Error (HTTP) parsing product {url}')
                return False

            soup = BeautifulSoup(response.content, 'html.Parsers1')

            breadcrumbs = soup.find('div', 'breadcrumbs')
            if breadcrumbs:
                breadcrumb_items = breadcrumbs.find_all('div', 'bx-breadcrumb-item')
                if breadcrumb_items:
                    if len(breadcrumb_items) > 1:
                        product['Раздел'] = breadcrumb_items[1].find('span', itemprop="name").get_text(strip=True)
                    if len(breadcrumb_items) > 2:
                        product['Категория'] = breadcrumb_items[2].find('span', itemprop="name").get_text(strip=True)

            detailed_desc = soup.find('div', 'detailed-desc')
            if not detailed_desc:
                return False

            elements_p = detailed_desc.find_all('p')
            for element in elements_p:
                if 'Артикул' in element.get_text(strip=True):
                    product['Артикул'] = element.get_text(separator='', strip=True).replace('Артикул:', '')
                    continue
                element = element.get_text(separator='#', strip=True)
                characteristics = element.split('#')
                if len(characteristics) > 0:
                    for attribute in characteristics:
                        if 'Описание' in attribute:
                            continue
                        if ':' in attribute:
                            attribute = attribute.replace('"', "'").replace('\xa0', ' ')
                            attribute_split = attribute.split(':')
                            product[str(attribute_split[0]).strip()] = ' '.join(attribute_split[1:]).strip()
                        else:
                            continue
            product['Время парсинга (мск)'] = get_current_time()
            return product
        except Exception as ex:
            print(print_template(f'Error: {ex}'))
            return False

    except Exception as e:
        logging.error(f'in parsing_product_page: {e}')
        module.send_error_to_cmc(f'in parsing_product_page: {str(e)[:50]}')