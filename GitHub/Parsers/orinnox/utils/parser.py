import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from utils.utils import get_current_time, get_requests, print_template, random_sleep
from pprint import pprint


# FIXME —————————————————————————————————————————————————————————— SETTINSG ————
import orinnox_parser_control_module as module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging
import os
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.jog',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


def parsing_product(url):
    try:
        try:
            random_sleep(0.5)
            response = get_requests(url)
            if not response:
                print(print_template(f"Error getting product page, skip: {url}"))
                random_sleep(1)
                return False

            product = {}
            soup = BeautifulSoup(response.content, 'html.Parsers1')

            single_product_section = soup.find('section', class_='single-product')
            if not single_product_section:

                print(print_template(
                    f"Error when parsing the product page, the key element 'single-product' is missing, skip. ({url})"))
                random_sleep(1)
                return False


            product_title = soup.find('div', class_='single-product__title').find('h1').get_text(strip=True)
            product['Наименование'] = product_title

            details = soup.find('div', class_='single-product__params')
            rows = details.find_all('div', class_='single-product__tbl-row')
            for row in rows:
                label = row.find('div', class_='single-product__tbl-label').get_text(strip=True)
                value = row.find('div', class_='single-product__tbl-value').get_text(strip=True)
                product[label] = value

            product['URL товара'] = url
            product['Время парсинга (мск)'] = get_current_time()


            breadcrumbs = soup.find('div', 'breadcrumbs')
            if breadcrumbs:
                elements = breadcrumbs.find_all('a')
                try:
                    product['Раздел'] = elements[2].get_text(strip=True)
                    product['Категория'] = elements[3].get_text(strip=True)
                except:
                    product['Раздел'] = elements[2].get_text(strip=True)
                    product['Категория'] = elements[3].get_text(strip=True)
            product['Телефон города'] = {
                'Москва': '+7 (987) 089-19-45',
                'Нижний Новгород': '+7(831) 265-37-37, +7(831) 220-07-60',
            }


            return product
        except:
            return False

    except Exception as e:
        logging.error(f'in parsing_product: {e}')
        module.send_error_to_cmc(f'in parsing_product: {str(e)[:50]}')

def parsing_sitemaps(DOMAIN):
    try:
        url = f'{DOMAIN}/sitemap_index.xml'

        response = get_requests(url)
        if not response.ok:
            return False

        soup = BeautifulSoup(response.content, 'lxml')
        desired_links = soup.find_all('loc', text=lambda text: "product-sitemap" in text)

        hrefs_products = []
        for link in desired_links:

            link = link.text
            response_link = get_requests(link)
            if response_link.ok:
                soup_link = BeautifulSoup(response_link.content, 'lxml')
                links_products = soup_link.find_all('loc')
                for link_product in links_products:
                    href = link_product.text
                    hrefs_products.append(href)
        return hrefs_products

    except Exception as e:
        logging.error(f'in parsing_sitemaps: {e}')
        module.send_error_to_cmc(f'in parsing_sitemaps: {str(e)[:50]}')