import os
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup, Tag
from utils.utils import get_current_time, get_requests


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import nlmk_parser_control_module as module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    level=logging.ERROR, encoding='utf-8', filemode='w',
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


def parsing_region_list():
    """
    Парсит список регионов (городов) с веб-страницы и возвращает их коды.
    Returns:
        list: Список строк, представляющих коды регионов (городов).
    """
    try:
        try:
            cities = []

            url = 'https://nlmk.shop/region/list'
            response = get_requests(url)

            soup = BeautifulSoup(response.text, 'html.Parsers1')
            links = soup.find_all('a', {'data-active': 'true'})

            for link in links:
                cities.append(link['data-fias'])
            return cities
        except Exception:
            return False
    except Exception as e:
        logging.error(f'in parsing_region_list: {e}')
        module.send_error_to_cmc(f'in parsing_region_list: {str(e)[:50]}')

def parsing_product_listing(soup):
    """
    Парсит элемент Tag с информацией о списке продуктов из объекта BeautifulSoup.

    Args:
        soup (BeautifulSoup): Объект BeautifulSoup, представляющий веб-страницу или HTML-код.

    Returns:
        Tag: BeautifulSoup Tag, представляющий список продуктов, или False, если список продуктов не найден.
    """
    try:
        product_listing = soup.find('div', 'd-sm-flex product-listing u-flex-nowrap')
        if product_listing.find('div', 'text-variant-bold fz-20 full-width-padding'):
            return False
        return product_listing
    except Exception as e:
        logging.error(f'in parsing_product_listing: {e}')
        module.send_error_to_cmc(f'in parsing_product_listing: {str(e)[:50]}')

def parsing_products(product_listing: Tag, soup, catalog_link):
    """
    Парсит информацию о продуктах из элемента Tag, представляющего список продуктов.

    Args:
        product_listing (Tag): BeautifulSoup Tag, представляющий список продуктов.

    Returns:
        list: Список словарей, представляющих информацию о продуктах.
              Каждый словарь содержит данные о складах и характеристиках продукта.
    """
    try:
        products_page = []

        try:
            catalog_product = product_listing.find_all('div', 'mb-30 catalog--listing_product')

            for product in catalog_product:
                product_data = {'Категория': None, 'Раздел': None, 'Город': None, 'Склады': [], 'URL товара': catalog_link,
                                'Телефон города': "+78005057685",'Время парсинга (мск)': get_current_time()}

                product_data['Наименование'] = product.find('p', 'catalog--listing_product--info_title mb-10 mb-sm-16').get_text(strip=True)

                product_info = product.find('div', 'catalog--listing_product--info ml-16 ml-sm-35')
                characteristics = product_info.find('ul').find_all('li')

                for characteristic in characteristics:
                    key = characteristic.contents[0].get_text(strip=True)
                    value = characteristic.contents[1].get_text(strip=True)
                    product_data[key] = value

                table_warehouses = product.find('table', 'catalog--listing_warehouses')
                if not table_warehouses:
                    continue

                rows = table_warehouses.find_all('tr')

                header_row = rows[0]
                header_cells = header_row.find_all('th')

                column_headers = [header.contents[0].get_text(strip=True).replace('\xa0', ' ') for header in header_cells[:5]]

                product_warehouse = []

                for warehouse in rows:
                    warehouse_data = {}
                    cells = warehouse.find_all('td')
                    if len(cells) >= 1:
                        for idx, cell in enumerate(cells[:5]):
                            cell = cell.get_text(strip=True).replace('\xa0', ' ').replace('"', "'")
                            warehouse_data[column_headers[idx]] = cell
                        product_warehouse.append(warehouse_data)
                product_data['Склады'] = product_warehouse

                breadcrumbs = soup.find('ul', 'breadcrumbs')

                if breadcrumbs:
                    breadcrumbs_item = breadcrumbs.find_all('li', 'breadcrumbs__item')
                    if len(breadcrumbs_item) > 1:
                        product_data['Раздел'] = breadcrumbs_item[1].get_text(strip=True)
                    if len(breadcrumbs_item) > 2:
                        product_data['Категория'] = breadcrumbs_item[2].get_text(strip=True)

                tooltip = soup.find('a', 'js-header-top__tooltip--toggle')
                if tooltip:
                    product_data['Город'] = tooltip.get_text(strip=True)

                products_page.append(product_data)
            return products_page
        except:
            return False
    except Exception as e:
        logging.error(f'in parsing_products: {e}')
        module.send_error_to_cmc(f'in parsing_products: {str(e)[:50]}')

def parsing_sitemaps(DOMAIN, city):
    """
    Парсит файлы сайт-карты (sitemap) на заданном домене и извлекает ссылки на каталоги сайта для заданного города.

    Args:
        DOMAIN (str): Домен сайта, для которого выполняется парсинг сайт-карты.
        city (str): Город, для которого выполняется парсинг сайт-карты.

    Returns:
        list: Список строк, представляющих URL-адреса каталогов на сайте.
    """
    try:
        url = f'{DOMAIN}/sitemap.xml'

        response = get_requests(url, city)

        if not response:
            return False

        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()
        other_sitemap_links = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")

        sitemap_files = []
        catalog_links = []

        for sitemap_link in other_sitemap_links:
            sitemap_files.append(sitemap_link.text)

        for sitemap in sitemap_files:
            response = get_requests(sitemap, city)
            if not response:
                return False

            tree = ET.ElementTree(ET.fromstring(response.content))
            root = tree.getroot()
            locs = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            for loc in locs:
                if "https://nlmk.shop/catalog" in loc.text:
                    catalog_links.append(loc.text)
        return catalog_links
    except Exception as e:
        logging.error(f'in parsing_sitemaps: {e}')
        module.send_error_to_cmc(f'in parsing_sitemaps: {str(e)[:50]}')