import json

from bs4 import BeautifulSoup
from utils.utils import get_current_time, get_requests, print_template


# FIXME —————————————————————————————————————————————————————————— SETTINSG ————
import pkf_parser_control_module as module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging
import os
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.jog',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————



def get_products_from_page(DOMAIN, soup):
    try:
        try:
            catalog_section = soup.find('div', 'ns-bitrix c-catalog-section c-catalog-section-catalog-text-1')
            catalog_section_items = catalog_section.find_all('a', 'catalog-section-item-name-wrapper')

            product_links = []
            for item in catalog_section_items:
                product_links.append(f'{DOMAIN}{item["href"]}')
            return product_links
        except:
            return False

    except Exception as e:
        logging.error(f'in get_products_from_page: {e}')
        module.send_error_to_cmc(f'in get_products_from_page: {str(e)[:50]}')

def parsing_category_links(DOMAIN, recursive=False):
    try:
        try:
            BASE_DOMAIN = 'https://pk-f.ru'

            category_links = []
            if not recursive:
                link = f'{BASE_DOMAIN}/catalog'
            else:
                link = DOMAIN
            response = get_requests(link)
            if not response:
                return False

            soup = BeautifulSoup(response.content, 'html.Parsers1')
            catalog_sections = soup.find_all('div', 'catalog-section-list-item intec-grid-item-4 intec-grid-item-1200-3 intec-grid-item-768-2 intec-grid-item-500-1')

            for catalog_section in catalog_sections:
                item_name = catalog_section.find('a', 'catalog-section-list-item-name intec-cl-text-hover')
                if item_name:
                    if not recursive:
                        category_link = f'{DOMAIN}{item_name.get("href")}'
                    else:
                        category_link = f'{BASE_DOMAIN}{item_name.get("href")}'
                    category_links.append(category_link)
                    result = parsing_category_links(category_link, recursive=True)
                    if result:
                        category_links += result

            return category_links
        except:
            return False

    except Exception as e:
        logging.error(f'in parsing_category_links: {e}')
        module.send_error_to_cmc(f'in parsing_category_links: {str(e)[:50]}')

def parsing_pagination(soup):
    try:
        pagination = soup.find('div', 'default-pagination__pages')
        if pagination:
            pagination_pages = pagination.find_all('a')
            second_page = int(pagination_pages[0].get_text(strip=True))
            last_page = int(pagination_pages[-1].get_text(strip=True))

            return True, range(second_page, last_page + 1)
        return False, []

    except Exception as e:
        logging.error(f'in parsing_pagination: {e}')
        module.send_error_to_cmc(f'in parsing_pagination: {str(e)[:50]}')

def parsing_products_on_page(soup):
    try:
        products_links = []
        products_wrapper = soup.find_all('tbody', 'catalog-list2')
        for element in products_wrapper:
            onclick = element.find('h2').get('onclick')
            if 'window.location=' in onclick:
                products_links.append(onclick[17:-2])
        return products_links if len(products_links) > 0 else False

    except Exception as e:
        logging.error(f'in parsing_products_on_page: {e}')
        module.send_error_to_cmc(f'in parsing_products_on_page: {str(e)[:50]}')

def parsing_product_page(url):
    try:
        try:
            response = get_requests(url)
            if not response:
                print_template(f'Error (HTTP) parsing product {url}')
                return False

            soup = BeautifulSoup(response.content, 'html.Parsers1')
            data = soup.find('div', 'ns-bitrix c-catalog-element c-catalog-element-catalog-default-2').get('data-data')

            data = json.loads(data)
            offers = data['offers']
            if not offers or len(offers) == 0:
                product = {'URL товара': url, 'Время парсинга (мск)': get_current_time()}

                title = soup.find('h1', id='pagetitle')
                if title:
                    product['Наименование'] = title.get_text(strip=True).replace('\xa0', ' ')

                phone = soup.find('a', 'widget-container-phone-text intec-cl-text-hover')
                if phone:
                    product['Телефон города'] = phone.get('href')[4:].strip()

                breadcrumb = soup.find('div', 'breadcrumb-wrapper-2 intec-content-wrapper')
                if breadcrumb:
                    breadcrumb_items = breadcrumb.find_all('a', 'breadcrumb-link intec-cl-text-hover')
                    if len(breadcrumb_items) > 2:
                        product['Раздел'] = breadcrumb_items[2].get_text(strip=True)
                    if len(breadcrumb_items) > 3:
                        product['Категория'] = breadcrumb_items[3].get_text(strip=True)

                section_properties = soup.find('div', 'catalog-element-section-properties')
                if section_properties:
                    elements_property = section_properties.find_all('div', 'catalog-element-section-property')
                    for element in elements_property:
                        key = element.find('div', 'catalog-element-section-property-name').get_text(strip=True).replace(
                            '\xa0', ' ')
                        value = element.find('div', 'catalog-element-section-property-value').get_text(strip=True).replace(
                            '\xa0', ' ')
                        if key and value:
                            product[key] = value
                return product
            all_offers = [value for key, value in offers.items()]
            products = []
            for offer in all_offers:
                product = {'URL товара': url, 'Время парсинга (мск)': get_current_time()}

                title = soup.find('h1', id='pagetitle')
                if title:
                    product['Наименование'] = title.get_text(strip=True).replace('\xa0', ' ')

                phone = soup.find('a', 'widget-container-phone-text intec-cl-text-hover')
                if phone:
                    product['Телефон города'] = phone.get('href')[4:].strip()

                breadcrumb = soup.find('div', 'breadcrumb-wrapper-2 intec-content-wrapper')

                if breadcrumb:
                    breadcrumb_items = breadcrumb.find_all('a', 'breadcrumb-link intec-cl-text-hover')
                    if len(breadcrumb_items) > 2:
                        product['Раздел'] = breadcrumb_items[2].get_text(strip=True)
                    if len(breadcrumb_items) > 3:
                        product['Категория'] = breadcrumb_items[3].get_text(strip=True)

                section_properties = soup.find('div', 'catalog-element-section-properties')
                if section_properties:
                    elements_property = section_properties.find_all('div', 'catalog-element-section-property')
                    for element in elements_property:
                        key = element.find('div', 'catalog-element-section-property-name').get_text(strip=True).replace('\xa0', ' ')
                        value = element.find('div', 'catalog-element-section-property-value').get_text(strip=True).replace('\xa0', ' ')
                        if key and value:
                            product[key] = value

                values = offer['values']
                if not values:
                    continue
                for key, value in values.items():
                    catalog_property = soup.find('div', {'data-property': key})
                    if not catalog_property:
                        continue
                    catalog_property_title = catalog_property.find('div', 'catalog-element-offers-property-title')

                    if catalog_property_title:
                        key_to_update = catalog_property_title.get_text(strip=True).replace('\xa0', ' ')

                        catalog_property_value = catalog_property.find('div', {'data-value': value})
                        if catalog_property_value:
                            value_to_update = catalog_property_value.get_text(strip=True).replace('\xa0', ' ')
                            product[key_to_update] = value_to_update
                            product['Цена'] = offer['prices'][0]['base']['display']
                products.append(product)
            return products
        except Exception as ex:
            print(print_template(f'Error: {ex} ({url})'))
            return False

    except Exception as e:
        logging.error(f'in parsing_product_page: {e}')
        module.send_error_to_cmc(f'in parsing_product_page: {str(e)[:50]}')
