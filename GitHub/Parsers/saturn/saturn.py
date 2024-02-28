import requests
import asyncio
import aiohttp
import time
import json
from bs4 import BeautifulSoup
import time
import concurrent.futures
import tqdm
from urllib.parse import urljoin


# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import saturn_parser_control_module as module
import os
module.parser_pid_saver(os.getpid())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    level=logging.ERROR, encoding='utf-8', filemode='w',
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————


def collect_all_catalogs_url():
    """собирает вcе ссылки на каталоги(все города)"""
    try:
        city_urls = collect_city_urls()
        all_catalogs_url = []
        for city_url in city_urls:
            catalog_urls = get_catalogs_urls(city_url)
            for catalog_url in catalog_urls:
                url = urljoin(city_url, catalog_url)
                all_catalogs_url.append(url)
        return all_catalogs_url
    except Exception as e:
        logging.error(f'in collect_all_catalogs_url(): {e}')
        module.send_error_to_cmc(f'in collect_all_catalogs_url(): {str(e)[:50]}')



def collect_city_urls():
    """собирает ссылки для всех доступных городов"""
    try:
        response = requests.get('https://msk.saturn.net/')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        url_blocks = soup.findAll('div', class_='_city_list-block')
        city_urls = []
        for url_block in url_blocks:
            for city_url in url_block.findAll('a'):
                city_urls.append(city_url.get('href'))
        return city_urls
    except Exception as e:
        logging.error(f'in collect_city_urls(): {e}')
        module.send_error_to_cmc(f'in collect_city_urls(): {str(e)[:50]}')



def get_catalogs_urls(city_url):
    """для каждого города собирает ссылки на каталоги с товарами"""
    try:
        response = requests.get(city_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        catalog_urls = [catalog.a.get('href') for catalog in soup.findAll('li', class_='list-item list-item-level1')[:9]]
        return catalog_urls
    except Exception as e:
        logging.error(f'in get_catalogs_urls(): {e}')
        module.send_error_to_cmc(f'in get_catalogs_urls(): {str(e)[:50]}')



def get_product_urls(pages_text, catalog_url):
    """Собирает все ссылки продуктов, в 1 странице"""
    try:
        product_urls = []
        soup = BeautifulSoup(pages_text, 'lxml')
        product_urls += [urljoin(catalog_url, block.a.get('href')) for block in
                         soup.find('div', class_='block-goods-list').findAll('div', class_='goods-card')]
        return product_urls
    except Exception as e:
        logging.error(f'in get_product_urls(): {e}')
        module.send_error_to_cmc(f'in get_product_urls(): {str(e)[:50]}')



async def parse_catalog_pages_texts(catalog_url):
    "парсит в 1 сессии все html-страницы каталога"
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(catalog_url)
            response_text = await response.text()
            soup = BeautifulSoup(response_text, 'lxml')
            pages = int(soup.find('nav', class_='_page_catalog-load-more load-more block-paginator').findAll('li')[-2].text.strip())
            pages_texts = []
            pages_texts.append([response_text, catalog_url])
            for page in range(2, pages + 1):
                params = {
                    'page': page
                }
                async with session.get(url=catalog_url, params=params) as response:
                    response_text = [await response.text(), catalog_url]
                    pages_texts.append(response_text)
        return pages_texts
    except Exception as e:
        logging.error(f'in parse_catalog_pages_texts(): {e}')
        module.send_error_to_cmc(f'in parse_catalog_pages_texts(): {str(e)[:50]}')



async def parse_response_text(product_url):
    "парсит html коды страниц"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=product_url) as response:
                response_text = [await response.text(), product_url]
        return response_text
    except Exception as e:
        logging.error(f'in parse_response_text(): {e}')
        module.send_error_to_cmc(f'in parse_response_text(): {str(e)[:50]}')



def parse_product(product_page, product_url):
    "парсит страницу продукта"
    try:
        products = []
        soup = BeautifulSoup(product_page, 'lxml')

        # далее обработка soup
        try:
            characteristic = get_characteristic(soup)
        except AttributeError:
            characteristic = {}
        prices_inf = get_prices(soup)
        catalog, category = get_catalog_and_category(soup)
        parsed_time = time.strftime("%Y-%m-%d %H:%M:%S")
        number = get_number(soup)
        city = get_city(soup)
        product_inf = {
            **characteristic,
            **prices_inf,
            'Каталог': catalog,
            'Раздел': category,
            'Город': city,
            'URL': product_url,
            'Время': parsed_time,
            'Телефон': number
        }
        products.append(product_inf)
        return products
    except Exception as e:
        logging.error(f'in parse_product(): {e}')
        module.send_error_to_cmc(f'in parse_product(): {str(e)[:50]}')



def split_list(all_product_urls, length):
    """делит все ссылки на куски по length штук"""
    try:
        splitted_urls = []
        first_index = 0
        for i in list(range(len(all_product_urls)))[::length]:
            if i:
                splitted_urls.append(all_product_urls[first_index:i])
            first_index = i
        splitted_urls.append(all_product_urls[first_index:])
        return splitted_urls
    except Exception as e:
        logging.error(f'in split_list(): {e}')
        module.send_error_to_cmc(f'in split_list(): {str(e)[:50]}')



def get_city(soup):
    try:
        city = soup.find('span', class_='b_title').text.strip()
        return city
    except Exception as e:
        logging.error(f'in get_city(): {e}')
        module.send_error_to_cmc(f'in get_city(): {str(e)[:50]}')



def get_number(soup):
    try:
        number = soup.find('button', class_='_region-phone btn-link btn _show-callback-window').text
        return number
    except Exception as e:
        logging.error(f'in get_number(): {e}')
        module.send_error_to_cmc(f'in get_number(): {str(e)[:50]}')



def get_catalog_and_category(soup):
    try:
        catalog_inf = list(soup.find('div', class_='path_block').stripped_strings)
        catalog = "-".join(catalog_inf)
        category = catalog_inf[-1]
        return catalog, category
    except Exception as e:
        logging.error(f'in get_catalog_and_category(): {e}')
        module.send_error_to_cmc(f'in get_catalog_and_category(): {str(e)[:50]}')



def get_prices(soup):
    try:
        price_block = soup.find('div', class_='price-wrapper _atc-price-wrapper')
        prices_inf = price_block.findAll('span', class_="_currency")
        prices_dict = {}
        for n, text in enumerate(prices_inf):
            if n:
                prices_dict[f'Цена{n}'] = list(text.parent.stripped_strings)[0]
            else:
                prices_dict[f'Цена'] = list(text.parent.stripped_strings)[0]
        return prices_dict
    except Exception as e:
        logging.error(f'in get_prices(): {e}')
        module.send_error_to_cmc(f'in get_prices(): {str(e)[:50]}')



def get_characteristic(soup):
    try:
        characteristics_blocks = soup.find('table', class_='_goods-params-table params').findAll('tr')
        characteristics_dict = {}
        for characteristic_block in characteristics_blocks:
            characteristic_block_texts = characteristic_block.findAll('td')
            characteristics_dict[' '.join(list(characteristic_block_texts[0].stripped_strings))] = ' '.join(
                list(characteristic_block_texts[1].stripped_strings))
        return characteristics_dict
    except Exception as e:
        logging.error(f'in get_characteristic(): {e}')
        module.send_error_to_cmc(f'in get_characteristic(): {str(e)[:50]}')



def write_and_save_json(filename, parsed_inf):
    """дописывает результат в файл result_saturn.json"""
    try:
        try:
            with open(filename, 'r', encoding='utf8') as file:
                parsed_before_inf = json.load(file)
        except Exception:
            parsed_before_inf = []
        all_inf = parsed_before_inf + parsed_inf
        with open(filename, 'w', encoding='utf8') as file:
            json.dump(all_inf, file, ensure_ascii=False)
    except Exception as e:
        logging.error(f'in write_and_save_json(): {e}')
        module.send_error_to_cmc(f'in write_and_save_json(): {str(e)[:50]}')



async def main():
    "принцип работы записан в README.md"
    try:
        time1 = time.time()
        all_catalogs_urls = collect_all_catalogs_url()
        print('собрал все каталоги у всех городов')

        tasks = []
        all_product_urls = []
        splitted_catalog_urls = split_list(all_catalogs_urls, 10)

        for catalog_urls in tqdm.tqdm(splitted_catalog_urls, total=len(splitted_catalog_urls)):
            for catalog_url in catalog_urls:
                pages_texts_catalog_url = asyncio.create_task(parse_catalog_pages_texts(catalog_url))
                tasks.append(pages_texts_catalog_url)
            await asyncio.gather(*tasks)
            pages = []
            for catalog in tasks:
                for page in catalog.result():
                    page_texts = page[0]
                    catalog_url = page[1]
                    pages.append([page_texts, catalog_url])

            with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
                future_to_url = (executor.submit(get_product_urls, page_text, catalog_url) for page_text, catalog_url in pages)
                for future in concurrent.futures.as_completed(future_to_url):
                    try:
                        product_urls = future.result()
                    except Exception as ex:
                        print('ошибка при обработке каталога')
                        print(ex)
                        product_urls = []
                    finally:
                        all_product_urls += product_urls
            write_and_save_json('url_products.json', all_product_urls)

        print('закончил парсинг ссылок на продукты')
        print('всего продуктов:', len(all_product_urls))
        print('спарсено за', time.time()-time1)

        with open('url_products.json', 'r') as file:
            product_urls = json.load(file)
        splitted_urls = split_list(product_urls, 100)
        for product_urls in tqdm.tqdm(splitted_urls, total=len(splitted_urls)):
            tasks = []
            for product_url in product_urls:
                tasks.append(asyncio.create_task(parse_response_text(product_url)))
            await asyncio.gather(*tasks)

            products = []
            with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
                future_to_url = (executor.submit(parse_product, response_text.result()[0], response_text.result()[1]) for response_text in tasks)
                for future in concurrent.futures.as_completed(future_to_url):
                    try:
                        products_list = future.result()
                    except Exception as ex:
                        print('ошибка при обработке товара')
                        print(ex)
                        products_list = []
                    finally:
                        all_product_urls += products_list
                    products_list = future.result()
                    products += products_list
            write_and_save_json('products.json', products)
        print('закончил парсинг, время выполнения:', time.time()-time1)
    except Exception as e:
        logging.error(f'in main(): {e}')
        module.send_error_to_cmc(f'in main(): {str(e)[:50]}')



if __name__=='__main__':
    try:
        module.get_memory_info()

        asyncio.run(main())

        module.send_data_to_adapter()
        module.send_end_parsing_status_cmc()

    except Exception as e:
        logging.error(f'in __main__(): {e}')
        module.send_error_to_cmc(f'in __main__(): {str(e)[:50]}')

