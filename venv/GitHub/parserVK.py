import requests
from bs4 import BeautifulSoup

# Ссылка на сайт поиска людей в Краснодаре в возрасте от 35 до 55 лет
url = 'https://vk.com/search?c%5Bage_from%5D=35&c%5Bage_to%5D=55&c%5Bcity%5D=72%2C1&c%5Bname%5D=1&c%5Bper_page%5D=40&c%5Bsection%5D=people'

# Обращение к сайту и получение его содержимого в виде HTML
response = requests.get(url)

# Получение HTML-содержимого
src = response.text

# Запись HTML в файл для проверки
with open('index.html', 'w') as file:
    file.write(src)

# Чтение HTML из файла
with open('index.html') as file:
    src = file.read()

# Обработка HTML-содержимого с помощью BeautifulSoup
soup = BeautifulSoup(src, 'lxml')

# Поиск имен и возрастов
names = soup.find_all(class_= 'si_owner')
years = soup.find_all(class_= 'si_slabel')

# Вывод имен и возрастов в консоль
for a,b in zip(names, years):
    a_text = a.text
    b_text = b.text
    print(a_text + ' ' + b_text)