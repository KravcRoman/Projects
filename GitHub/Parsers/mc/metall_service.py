import os
import json
import logging
import datetime
from typing import Generator

from bs4 import BeautifulSoup
import requests
import chardet
import pytz


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import metall_service_parser_control_module as module

module.parser_pid_saver(os.getpid())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    level=logging.ERROR, encoding='utf-8', filemode='w',
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


BASE_URL = 'https://mc.ru'
CATALOGS_URL = BASE_URL + '/price'

JSON_FILENAME = 'products.json'

HTML_P_TAG = 'p'
HTML_A_TAG = 'a'
HTML_TR_TAG = 'tr'
HTML_UL_TAG = 'ul'
HTML_LI_TAG = 'li'
HTML_DIV_TAG = 'div'
HTML_TBODY_TAG = 'tbody'

HTML_CITIES_CLASS = 'menulist'
HTML_PRICE_LISTS_CLASS = 'pagePriceList'

CURRENT_MOSCOW_TIME = 'Время парсинга'
URL = 'URL прайс-листа'
SECTION = 'Раздел'
PHONE = 'Телефон'
CITY = 'Город'



def get_current_moscow_time() -> str:
    try:
        moscow_tz = pytz.timezone('Europe/metinvest')
        current_moscow_time = datetime.datetime.now(moscow_tz)
        return str(current_moscow_time)[:-13]
    except Exception as e:
        logging.error(f'in get_current_moscow_time: {e}')
        module.send_error_to_cmc(f'in get_current_moscow_time: {str(e)[:50]}')

def get_html(url:str) -> str:
    try:
        response = requests.get(url)
        encoding = chardet.detect(response.content)['encoding']
        response.encoding = encoding
        html = response.text
        return html
    except Exception as e:
        logging.error(f'in get_html: {e}')
        module.send_error_to_cmc(f'in get_html: {str(e)[:50]}')

def get_phone_from_price_list(url:str) -> str:
    try:
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.Parsers1')
        div_contents = soup.find(HTML_DIV_TAG, {'id': 'info'})
        if div_contents:
            city_phone = div_contents.find_all(HTML_P_TAG)[0]
            return city_phone.get_text().strip()
        else:
            return f'no phone on {url}'
    except Exception as e:
        logging.error(f'in get_phone_from_price_list: {e}')
        module.send_error_to_cmc(f'in get_phone_from_price_list: {str(e)[:50]}')

def get_cities_catalogs_urls() -> dict:
    try:
        cities_catalogs_urls = {}
        html = get_html(CATALOGS_URL)
        soup = BeautifulSoup(html, 'html.Parsers1')
        ul_tag_contents = soup.find(HTML_UL_TAG, class_=HTML_CITIES_CLASS)
        for li_coontents in ul_tag_contents.find_all(HTML_LI_TAG):
            city = li_coontents.get_text()
            catalog_page_link = li_coontents.find(HTML_A_TAG, href=True)
            catalog_url = catalog_page_link['href']
            cities_catalogs_urls[city] = BASE_URL + catalog_url
        return cities_catalogs_urls
    except Exception as e:
        logging.error(f'in get_cities_catalogs_urls: {e}')
        module.send_error_to_cmc(f'in get_cities_catalogs_urls: {str(e)[:50]}')

def get_price_lists_urls(url:str) -> dict:
    try:
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.Parsers1')
        ul_tag_contents = soup.find(HTML_UL_TAG, class_=HTML_PRICE_LISTS_CLASS)
        dirty_names = []
        names = []
        urls = []
        for li_tag_contents in ul_tag_contents.find_all(HTML_LI_TAG):
            dirty_names.append(li_tag_contents.get_text().replace('\n', '').replace('\r', '').split())
            for a_tag_contents in li_tag_contents.find_all(HTML_A_TAG, href=True):
                catalog_url = a_tag_contents['href']
                if catalog_url[-3:] == 'htm':
                    if catalog_url[:13] != BASE_URL:
                        full_catalog_url = BASE_URL + catalog_url
                        urls.append(full_catalog_url)
                    else:
                        urls.append(catalog_url)
        for name in dirty_names:
            del name[0]
            clear_name = ' '.join(name)
            names.append(clear_name)
        price_lists_urls = dict(zip(names, urls))
        return price_lists_urls
    except Exception as e:
        logging.error(f'in get_price_lists_urls: {e}')
        module.send_error_to_cmc(f'in get_price_lists_urls: {str(e)[:50]}')

def get_products_from_tables(url:str) -> Generator[dict, None, None]:
    try:
        phone = get_phone_from_price_list(url)
        current_moscow_time = get_current_moscow_time()
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.Parsers1')
        tbody_tag_contents = soup.find_all(HTML_TBODY_TAG)
        for tbody_tag_content in tbody_tag_contents:
            table_rows = tbody_tag_content.find_all(HTML_TR_TAG)
            table_name = table_rows[0].get_text().replace('\n', '')
            table_headings = [heading.get_text() for heading in table_rows[1]]
            index = 0
            for heading in table_headings:
                if heading == '\n':
                    del table_headings[index]
                    index += 1
                else:
                    pass
            for product_params in table_rows[2:]:
                params = [param.get_text() for param in product_params]
                index = 0
                for param in params:
                    if param == '\n':
                        del params[index]
                        index += 1
                    else:
                        pass
                product = dict(zip(table_headings, params))
                product[SECTION] = table_name
                product[PHONE] = phone
                product[CURRENT_MOSCOW_TIME] = current_moscow_time
                product[URL] = url
                yield product
    except Exception as e:
        logging.error(f'in get_products_from_tables: {e}')
        module.send_error_to_cmc(f'in get_products_from_tables: {str(e)[:50]}')

def get_products():
    try:
        products = []
        for city, catalog_url in get_cities_catalogs_urls().items():
            for price_list_name, price_list_url in get_price_lists_urls(catalog_url).items():
                for product in get_products_from_tables(price_list_url):
                    products.append(product)
        return products
    except Exception as e:
        logging.error(f'in get_products: {e}')
        module.send_error_to_cmc(f'in get_products: {str(e)[:50]}')

def dump_products_in_json():
    try:
        products = get_products()
        with open(JSON_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f'in dump_products_in_json: {e}')
        module.send_error_to_cmc(f'in dump_products_in_json: {str(e)[:50]}')


dump_products_in_json()

module.get_memory_info()
module.send_data_to_adapter()
module.send_end_parsing_status_cmc()
