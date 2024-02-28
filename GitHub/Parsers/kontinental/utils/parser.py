import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from utils.utils import get_current_time, get_requests, print_template, random_sleep

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# FIXME —————————————————————————————————————————————————————————— SETTINSG ————
import kontinental_parser_control_module as module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging
import os
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.jog',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format='%(levelname)s %(asctime)s %(message)s')
# FIXME ————————————————————————————————————————————————————————————————————————



def get_city_prices(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        random_sleep(0.5)
        price_city = {}
        city_names = {
            'kazan.': 'Казань',
            'krd.': 'Краснодар',
            'izh.': 'Ижевск',
            'nsk.': 'Новосибирск',
            'msk.': 'Москва',
            'samara.': 'Самара',
            'spb.': 'Санкт-Петербург',
            'tmn.': 'Тюмень',
            'chel.': 'Челябинск',
            '': 'Екатеринбург'
        }
        cities = ['kazan.', 'krd.', 'izh.', 'nsk.', 'msk.', 'samara.', 'spb.', 'tmn.', 'chel.', '']
        for city in cities:
            try:
                city_url = url.replace("https://kontinental.ru/", f"https://{city}kontinental.ru/")

                response = get_requests(city_url)
                if not response:
                    print_template(f"Error getting product page, skip: {city_url}")
                    random_sleep(0.5)
                    return False

                prices_and_conditions = {}

                soup = BeautifulSoup(response.content, 'html.Parsers1')

                rows_price = soup.find('div', class_='prices')

                try:
                    driver.get(city_url)
                except:
                    pass

                wait = WebDriverWait(driver, 10)
                cost_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "buyer__cost_nds")))
                cost_value = cost_element.get_attribute("value")

                prices_and_conditions["Стоимость (₽) с НДС"] = cost_value
                inner_price = rows_price.find('div', class_='inner')

                rows = inner_price.find_all('div', class_='col-6')

                for row in rows:
                    condition = row.get_text(strip=True)
                    price = row.find('span').get_text()
                    prices_and_conditions[condition] = price

                full_city_name = city_names.get(city, 'Неизвестный')
                price_city[full_city_name] = prices_and_conditions
            except:
                pass
        driver.quit()
        return price_city
    except Exception as e:
        logging.error(f'in get_city_prices: {e}')
        module.send_error_to_cmc(f'in get_city_prices: {str(e)[:50]}')


def parsing_product(url):
    try:
        try:
            random_sleep(0.5)
            response = get_requests(url)
            if not response:
                print_template(f"Error getting product page, skip: {url}")
                random_sleep(0.5)
                return False

            product = {}
            soup = BeautifulSoup(response.content, 'html.Parsers1')

            product_wrapper = soup.find('div', 'prod-descript')
            if not product_wrapper:
                print_template(
                    f"Error when parsing the product page, the key element 'product-wrapper' is missing, skip. ({url})")
                random_sleep(1)
                return False
            product_name = soup.find("div", class_="prod-descript").find("h1")

            product['Наименование'] = product_name.get_text(strip=True).replace('"', "'").replace('\xa0', ' ')
            product['URL товара'] = url
            product['Время парсинга (мск)'] = get_current_time()

            phone_element = soup.find(class_="mgo-num")
            phone_number = phone_element.text
            product['Телефон города'] = phone_number

            price = get_city_prices(url)
            if price is None or not price:
                product['Цена'] = None
            else:
                product['Цена'] = price

            breadcrumb = soup.find('ol', class_='breadcrumb')

            elements = []
            for li in breadcrumb.find_all('li', class_='breadcrumb-item'):
                element_text = li.get_text(strip=True)
                elements.append(element_text)

                if len(elements) >= 3:
                    product['Раздел'] = elements[2]
                    if len(elements) >= 4:
                        product['Категория'] = elements[3]
                    else:
                        product['Категория'] = None
                else:
                    product['Раздел'] = elements[2]
                    if len(elements) >= 4:
                        product['Категория'] = elements[3]
                    else:
                        product['Категория'] = None

            harakteristick = soup.find('div', class_='harakteristick')

            h2 = harakteristick.find('h2', text='Характеристики')

            if h2:
                characteristics = {}
                ul = h2.find_next('ul')

                for li in ul.find_all('li'):
                    span_list = li.find_all('span')
                    if len(span_list) == 2:
                        key = span_list[0].get_text(strip=True)
                        value = span_list[1].get_text(strip=True)
                        characteristics[key] = value

                product['Характеристики'] = characteristics
            else:
                # print("Характеристики не найдены")
                pass
            random_sleep(0.5)
            return product
        except:
            return False
    except Exception as e:
        logging.error(f'in parsing_product: {e}')
        module.send_error_to_cmc(f'in parsing_product: {str(e)[:50]}')

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
                if "https://kontinental.ru/catalog/" in loc.text:
                    catalog_links.append(loc.text)

        if len(catalog_links) > 0:
            catalog_links = list(set(catalog_links))

        return catalog_links
    except Exception as e:
        logging.error(f'in parsing_sitemaps: {e}')
        module.send_error_to_cmc(f'in parsing_sitemaps: {str(e)[:50]}')