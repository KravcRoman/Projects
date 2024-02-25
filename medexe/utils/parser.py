import os
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from utils.utils import get_current_time, get_requests, print_template, random_sleep


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import medexe_parser_control_module as module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import logging
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

            page = soup.find('div', 'page')
            product_wrapper = soup.find('div', 'price-wrap')
            if not product_wrapper or not page:
                print_template(f"Error when parsing the product page, the key element 'product-wrapper/page' is missing, skip. ({url})")
                random_sleep(1)
                return False

            product['Наименование'] = page.find('h1').get_text(strip=True).replace('"', "'").replace('\xa0', ' ')
            product['URL товара'] = url
            product['Время парсинга (мск)'] = get_current_time()
            product['Телефон города'] = soup.find('div', 'header-info').find('a', 'phone')['href'][4:]
            product['Артикул'] = product_wrapper.find('span', 'articul').get_text(strip=True).replace('Код: ', '')

            price_meta = product_wrapper.find('div', id='full_price').find("meta", itemprop="price")["content"]
            price_span = product_wrapper.find('div', 'price_1').find("span").get_text(strip=True)

            product['Цена'] = price_span if price_meta == '0' else price_meta

            breadcrumbs = soup.find('div', 'breadcrumbs')
            if breadcrumbs:
                elements = breadcrumbs.find_all('a')
                if len(elements) >= 2:
                    product['Раздел'] = elements[2].get_text(strip=True)
                if len(elements) > 3:
                    if 'Цены' not in elements[3].get_text(strip=True):
                        product['Категория'] = elements[3].get_text(strip=True)
                    else:
                        if 'https://medexe.ru/production/catches' in url:
                            if 'чугун' in product['Наименование']:
                                product['Категория'] = 'Задвижки чугунные'
                            if 'клиновая' in product['Наименование']:
                                product['Категория'] = 'Задвижки стальные'
                        else:
                            product['Категория'] = elements[2].get_text(strip=True)

            table = soup.find("table", class_="features")
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) == 2:
                        characteristic_name = cells[0].text.strip().replace('"', "'").replace('\xa0', ' ').replace('\n', ' ')
                        characteristic_value = cells[1].text.strip().replace('"', "'").replace('\xa0', ' ').replace('\n', ' ')
                        product[characteristic_name] = characteristic_value
                random_sleep(0.5)
            return product
        except Exception as ex:
            return False
    except Exception as e:
        logging.error(f'in parsing_product(): {e}')
        send_error_to_cmc(f'in parsing_product(): {str(e)[:50]}')


def parsing_sitemaps(DOMAIN):
    try:
        url = f'{DOMAIN}/sitemap.xml'

        response = get_requests(url)

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
            response = get_requests(sitemap)
            if not response:
                return False

            tree = ET.ElementTree(ET.fromstring(response.content))
            root = tree.getroot()
            locs = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            for loc in locs:
                if "https://medexe.ru/production" in loc.text:
                    catalog_links.append(loc.text)

        if len(catalog_links) > 0:
            catalog_links = list(set(catalog_links))
        return catalog_links
    except Exception as e:
        logging.error(f'in parsing_sitemaps(): {e}')
        send_error_to_cmc(f'in parsing_sitemaps(): {str(e)[:50]}')
