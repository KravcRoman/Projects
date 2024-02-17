import requests
from bs4 import BeautifulSoup

#url = "https://23met.ru/price/armatura_a1/6"
#response = requests.get(url)
#soup = BeautifulSoup(response, 'lxml')


with open('x.html','r',encoding='utf-8') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')
# Поиск имен и возрастов
price = soup.find_all('span', class_='cost')
price2 = soup.find_all('td', class_='td_cost2')
price3 = soup.find_all('span', class_='cost2')
yslovie = soup.find_all('td', class_='td_cost2')
yslovie2 = soup.find_all('small', class_='yslovie2')

price = list(price)

filters = soup.find_all('tr')
filters1 = list(filters[0])
b = 0

for i in range(len(price)):
    filters2 = list(filters[i+1])
    if len(filters2[3]) < 1:
        print(i+1, *filters1[1], '-', *filters2[1],'|', *filters1[3], '-', 'нет данных','|', *filters1[5], '-', *filters2[5])
        if len(price2[i]) > 0:
            print('Цена за 1т.', '-', *price[i], 'руб. с НДС.', 'Цена при покупке', *yslovie2[b], '-', *price3[b],
                  'руб. с НДС')
            b += 1
        elif 'звоните' in price[i]:
            print('Звоните, чтоб узнать цену')
        elif len(price2[i]) == 0:
            print('Цена за 1т.', '-', *price[i], 'руб. с НДС')


    elif len(filters2[5]) < 1:
        print(i+1, *filters1[1], '-', *filters2[1],'|', *filters1[3], '-', *filters2[3],'|', *filters1[5], '-', 'нет данных')
        if len(price2[i]) > 0:
            print('Цена за 1т.', '-', *price[i], 'руб. с НДС.', 'Цена при покупке', *yslovie2[b], '-', *price3[b],
                  'руб. с НДС')
            b += 1
        elif 'звоните' in price[i]:
            print('Звоните, чтоб узнать цену')
        elif len(price2[i]) == 0:
            print('Цена за 1т.', '-', *price[i], 'руб. с НДС')


    else:
        print(i+1, *filters1[1], '-', *filters2[1],'|', *filters1[3], '-', *filters2[3],'|', *filters1[5], '-', *filters2[5])
        if len(price2[i]) > 0:
            print('Цена за 1т.', '-', *price[i], 'руб. с НДС.', 'Цена при покупке', *yslovie2[b], '-', *price3[b],
                  'руб. с НДС')
            b += 1
        elif 'звоните' in price[i]:
            print('Звоните, чтоб узнать цену')
        elif len(price2[i]) == 0:
            print('Цена за 1т.', '-', *price[i], 'руб. с НДС')
