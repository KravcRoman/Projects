import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import mmk_parser_control_module as module
import os
module.parser_pid_saver(os.getpid())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    level=logging.ERROR, encoding='utf-8', filemode='w',
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


def join_url(url):
    """складывает кусочки url в полную версию"""
    try:
        base_url = 'https://market.mmk.ru/'
        full_url = urljoin(base_url, url)
        return full_url
    except Exception as e:
        logging.error(f'in join_url: {e}')
        module.send_error_to_cmc(f'in join_url: {str(e)[:50]}')

def collect_category_urls():
    """собирает ссылки на все категории предоставленные на главной странице"""
    try:
        base_url = 'https://market.mmk.ru/'
        response = requests.get(base_url)
        response.raise_for_status()
        time.sleep(1)
        soup = BeautifulSoup(response.text, 'lxml')
        category_blocks = soup.findAll('div', class_="c-b__i")
        category_urls = [join_url(category_block.a.get('href')) for category_block in category_blocks]
        return category_urls
    except Exception as e:
        logging.error(f'in collect_category_urls: {e}')
        module.send_error_to_cmc(f'in collect_category_urls: {str(e)[:50]}')

def parse_products_on_page(category_url, page, count, category):
    """парсит 1 страницу и возвращает лист со спарсенными продуктами"""
    try:
        parsed_inf = []
        params = {
            'cnt': 30,
            'PAGEN_1': page
        }
        response = requests.get(category_url, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        product_blocks = soup.findAll('div', class_="c-list__i")
        for product_block in product_blocks:
            count += 1
            url = get_url(product_block)
            characteristics_dict = parse_characteristics(product_block)
            name = get_name(product_block)
            parsed_time = time.strftime("%Y-%m-%d %H:%M:%S")
            storages = parse_storages(product_block)
            for storage in storages:
                product_inf = {
                    **characteristics_dict,
                    **storage,
                    'url': url,
                    'Время': parsed_time,
                    'Категория': category,
                    'Наименование': name
                }
                parsed_inf.append(product_inf)
        return parsed_inf, count
    except Exception as e:
        logging.error(f'in parse_products_on_page: {e}')
        module.send_error_to_cmc(f'in parse_products_on_page: {str(e)[:50]}')

def parse_characteristics(product_block):
    """из блока-html продукта вытаскивает его характеристики,далее преобразовывает в словарь и возвращает. """
    try:
        try:
            characteristics = list(product_block.find('div', class_='c-list-param__items').stripped_strings) + \
                             list(product_block.find('div', class_='c-list-param__list').stripped_strings)
        except AttributeError:
            try:
                characteristics = list(product_block.find('div', class_='c-list-param__items').stripped_strings)
            except AttributeError:
                characteristics = []

        characteristics_dict = {}
        for n, characterictic in enumerate(characteristics):
            if n % 2 == 0:
                characteristics_dict[characterictic] = characteristics[n+1]
        return characteristics_dict
    except Exception as e:
        logging.error(f'in parse_characteristics: {e}')
        module.send_error_to_cmc(f'in parse_characteristics: {str(e)[:50]}')

def parse_storages(product_block):
    """Парсит склады, где в наличие этот товар, возвращает список из словарей. Последний склад в списке `под заказ`"""
    try:
        storages_bloks = product_block.findAll('div', class_="c-list__line")
        value = ''.join(list(product_block.find('div', class_="c-list__cell c-list__cell--quality").span.stripped_strings)[1:])
        storages = []
        if len(storages_bloks) == 1:
            price = storages_bloks[0].find('span', class_="b-price__current").get('data-price').strip()
            storages.append({
                'Город': 'Магнитогорск',
                'Цена': price,
                'Количество': '-',
                'Единица': value
            })
        else:
            for storages_block in storages_bloks[:-1]:
                try:
                    storage = storages_block.find('div', class_="c-list__cell c-list__cell--stock").text.strip()
                    price = storages_block.find('span', class_="b-price__current").get('data-price').strip()
                    availability = storages_block.find('div', class_="c-list__cell c-list__cell--quality").find('div', class_="c-list__cell-quality").find('div', class_="tooltip__icon").text.strip()
                    storages.append({
                        'Город': storage,
                        'Цена': price,
                        'Количество': availability,
                        'Единица': value
                    })
                except AttributeError:
                    storage = storages_block.find('div', class_="c-list__cell c-list__cell--stock").text.strip()
                    price = storages_block.find('span', class_="b-price__current").get('data-price').strip()
                    availability = storages_block.find('div', class_="c-list__cell c-list__cell--quality").find('div', class_="c-list__cell-quality").div.span.text.strip()
                    storages.append({
                        'Город': storage,
                        'Цена': price,
                        'Количество': availability,
                        'Единица': value
                    })
        return storages
    except Exception as e:
        logging.error(f'in parse_storages: {e}')
        module.send_error_to_cmc(f'in parse_storages: {str(e)[:50]}')

def get_url(product_block):
    """возвращает url"""
    try:
        url = product_block.find('div', class_="c-list__head").a.get('href')
        return join_url(url)
    except Exception as e:
        logging.error(f'in get_url: {e}')
        module.send_error_to_cmc(f'in get_url: {str(e)[:50]}')

def get_name(product_block):
    """возвращает название"""
    try:
        catalog = product_block.find('div', class_="c-list__head").a.get('title')
        return catalog
    except Exception as e:
        logging.error(f'in get_name: {e}')
        module.send_error_to_cmc(f'in get_name: {str(e)[:50]}')

def write_and_save_json(parsed_inf):
    """дописывает результат в файл result_mmk.json"""
    try:
        try:
            with open('result_mmk.json', 'r', encoding='utf8') as file:
                parsed_before_inf = json.load(file)
        except Exception:
            parsed_before_inf = []
        all_inf = parsed_before_inf + parsed_inf
        with open('result_mmk.json', 'w', encoding='utf8') as file:
            json.dump(all_inf, file, ensure_ascii=False)
    except Exception as e:
        logging.error(f'in write_and_save_json: {e}')
        module.send_error_to_cmc(f'in write_and_save_json: {str(e)[:50]}')

def get_num_pages_and_category_name(category_url):
    try:
        params = {
            'cnt': 30,
            'PAGEN_1': 1
        }
        response = requests.get(category_url, params=params)
        response.raise_for_status()
        time.sleep(3)
        soup = BeautifulSoup(response.text, 'lxml')
        num_products = int(soup.find('div', id="all_count_catalog").text.split()[0][1:])
        category = ''.join(list(soup.find('div', class_="b-breadcrumbs").stripped_strings))
        return num_products // 30 + 1, category
    except Exception as e:
        logging.error(f'in get_num_pages_and_category_name: {e}')
        module.send_error_to_cmc(f'in get_num_pages_and_category_name: {str(e)[:50]}')

def main():
    try:
        count = 0
        category_urls = collect_category_urls()
        for category_url in category_urls:
            parsed_inf = []
            num_pages, category = get_num_pages_and_category_name(category_url)
            for page in range(1, num_pages + 1):
                parsed_page, count = parse_products_on_page(category_url, page, count, category)
                parsed_inf.append(parsed_page)
                print(count)
            write_and_save_json(parsed_inf)
    except Exception as e:
        logging.error(f'in main: {e}')
        module.send_error_to_cmc(f'in main: {str(e)[:50]}')


if __name__=='__main__':
    try:
        main()

        module.send_data_to_adapter()
        module.send_end_parsing_status_cmc()

    except Exception as e:
        logging.error(f'in __main__: {e}')
        module.send_error_to_cmc(f'in __main__: {str(e)[:50]}')