import requests
from bs4 import BeautifulSoup
import xmltodict
from celery import Celery

# Создаем экземпляр Celery
app = Celery('tasks',
             broker='amqp://guest:guest@localhost:5672//',
             backend='rpc://')

# Функция для сбора ссылок с каждой страницы
def scrape_page(page_number):
    url = f'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber={page_number}'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for item in soup.find_all('a', class_='registry-entry__header-mid__number'):
            link = item.get('href')
            links.append(link)
        return links
    else:
        print(f'Failed to scrape page {page_number}: {response.status_code}')
        return []

# Функция для парсинга XML-формы и извлечения даты публикации
def parse_xml(link):
    xml_url = link.replace('view.html', 'viewXml.html')
    response = requests.get(xml_url)
    if response.status_code == 200:
        xml_data = xmltodict.parse(response.text)
        publish_date = xml_data.get('ns2:fcsNotificationEF', {}).get('publishDTInEIS')
        return publish_date
    else:
        print(f'Failed to parse XML for link {link}: {response.status_code}')
        return None

# Задача Celery для сбора ссылок с каждой страницы
@app.task
def scrape_pages():
    all_links = []
    for page_number in range(1, 3):  # Первые две страницы
        links = scrape_page(page_number)
        all_links.extend(links)
    return all_links

# Задача Celery для парсинга XML-форм и извлечения даты публикации
@app.task
def parse_xmls(links):
    for link in links:
        publish_date = parse_xml(link)
        print(f'Link: {link}, Publish Date: {publish_date}')

# Вызываем задачи Celery
if __name__ == '__main__':
    links_task = scrape_pages.delay()
    parse_xmls.delay(links_task.get())
