import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import json

# FIXME —————————————————————————————————————————————————————————— SETTINGS ————
import inrost_group_parser_control_module as module

module.parser_pid_saver(os.getpid())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGS ~~~~
import logging
CURRENT_DIR = os.getcwd()
logging.basicConfig(filename=CURRENT_DIR + f'/errors_{module.PARSER_NAME}.log',
                    filemode='w', encoding='utf-8', level=logging.ERROR,
                    format=f'%(levelname)s %(asctime)s %(message)s')
# FIXME —————————————————————————————————————————— ПРИ СОЕДИНЕНИИ С МОДУЛЕМ ————
def write_and_save_json(list_osn):
    """дописывает результат в файл result_inrost.json"""
    try:
        try:
            with open('result_inrost.json', 'r', encoding='utf8') as file:
                parsed_before_inf = json.load(file)
        except Exception:
            parsed_before_inf = []
        all_inf = parsed_before_inf + list_osn
        with open('result_inrost.json', 'w', encoding='utf8') as file:
            json.dump(all_inf, file, ensure_ascii=False)
    except Exception as e:
        logging.error(f'in write_and_save_json: {e}')
        module.send_error_to_cmc(f'in write_and_save_json: {str(e)[:50]}')

try:
    proverka = 1

    goroda = ['', 'ekaterinburg.', 'spb.']
    response = requests.get('https://inrost-group.ru/products/')
    soup = BeautifulSoup(response.text, 'lxml')
    link_list = []
    for all_1 in soup.find('div', class_="block").find_all('div', class_="ptypes__block"):
        all_2 = all_1.find_all('a')

        for link_categ in all_2:

            try:
                link = 'inrost-group.ru'+link_categ.get('href')
                link_list.append(link)
            except:
                pass
    jj = 0
    list_osn = []
    for gorod1 in goroda:

        if 'ekaterinburg' in gorod1 :
            gorod_1 = 'Екатеринбург'
        elif 'spb' in gorod1 :
            gorod_1 = 'Санкт-Петербург'
        elif '' in gorod1:
            gorod_1 = 'Челябинск'
        for link_categ in link_list:
            jj += 1
            lilink = 'https://'+gorod1+link_categ
            # print(lilink)
            response = requests.get(lilink)
            soup = BeautifulSoup(response.text, 'lxml')

            category_all = soup.find('ul', class_="breadcrumbs").find_all('span')
            categ3_lists = []
            # print('category_all     ',category_all)
            for categ__ in category_all:
                categ3_lists.append(categ__.text.replace('\n', '').strip())

            headers_list = []       # здесь шапка ексель
            try:
                for headers_ in soup.find('div', class_="ptbl__head").find_all('div'):
                    headers_name = headers_.text.replace('\t', '').replace('\n', '')
                    headers_list.append(headers_name)
            except AttributeError:
                pass
            try:
                for znachen_all in soup.find('ul', class_="pricetable").find_all('li'):      # здесь характеристики товара
                    # print()
                    # print(gorod_1)
                    try:
                        truba = znachen_all.find('div', class_="ptbl__title").text.replace('\n', '')
                        # print('truba '+truba)
                    except:
                        truba = ''
                    try:
                        stal = znachen_all.find('div', class_="ptbl__steel").text.replace('\n', '')
                        # print('stal '+stal)
                    except:
                        stal = ''
                    try:
                        haracteristics = znachen_all.find('div', class_="ptbl__char").text.replace('\n', '')
                        # print('haracteristics '+haracteristics)
                    except:
                        haracteristics = ''
                    try:
                        price_all = znachen_all.find('div', class_="ptbl__price").text.replace('\n', '').replace('→', '').strip()
                        # print('price_all '+price_all)
                    except:
                        price_all = ''
                    try:
                        price_za_1 = znachen_all.find('div', class_="ptbl__price hd").text.replace('\n', '').strip()
                        # print('price_za_1 '+ price_za_1)
                    except:
                        price_za_1 = ''
                    try:
                        sclad = znachen_all.find('div', class_="ptbl__store").text.replace('\n', '')
                        # print('sclad '+sclad)
                    except:
                        sclad = ''
                    try:
                        na_sclade = znachen_all.find('div', class_="ptbl__av").text.replace('\n', '')
                        # print('na_sclade '+na_sclade)
                    except:
                        na_sclade = ''
                    #####################
                    # print()
                    try:
                        cat0 = categ3_lists[1]
                    except:
                        cat0 = ''
                    try:
                        if categ3_lists[0] == 'Сварные трубы':
                            cat1 == 'Электросварные'
                        else:
                            cat1 = categ3_lists[2]
                    except:
                        cat1 = ''
                    # try:
                    #     cat2 = categ3_lists[3]
                    # except:
                    #     cat2 = ''
                    # ########################
                    try:
                        head0 = headers_list[1]
                    except:
                        head0 = ''

                    try:
                        head1 = headers_list[2]
                    except:
                        head1 = ''

                    try:
                        head2 = headers_list[3]
                    except:
                        head2 = ''

                    try:
                        head3 = headers_list[4]
                    except:
                        head3 = ''

                    try:
                        head4 = headers_list[5]
                    except:
                        head4 = ''

                    try:
                        head5 = headers_list[6]
                    except:
                        head5 = headers_list[7]


                    # print(headers_list)
                    if 1 == proverka:
                        dict_tovar = {
                            'Город': gorod_1,
                            'Основной раздел': cat0,
                            'Подраздел': cat1,
                            #'Подраздел 2': cat2,
                            'Наименование': truba,
                            head0: stal,
                            head1: haracteristics,
                            head2: price_all,
                            head3: price_za_1,
                            head4: sclad,
                            head5: na_sclade,
                        }
                    else:
                        dict_tovar = {
                            'Город': gorod_1,
                            'Основной раздел': cat0,
                            'Подраздел': cat1,
                            #'Подраздел 2': cat2,
                            'Наименование': truba,
                            head2: price_all,
                            head3: price_za_1
                        }

                    list_osn.append(dict_tovar)

                    """ Создание Json """

                    #write_and_save_json(list_osn)


                    # sys.stdout.write(f"\rCтрок в ксв: {len(list_osn)}, Обработано ссылок: {jj}/{len(link_list) * 3 - 8}")
                    # sys.stdout.flush()
            except:
                pass

    df = pd.DataFrame(list_osn)

    df.to_csv('file.csv', sep=';', index=False)
    try:
        with open('name_parameters.txt', 'r', encoding='utf-8') as f:
            columns_to_delete = [line.strip() for line in f.readlines()]

        # Загружаем CSV-файл в DataFrame, пропуская строки с ошибками
        df = pd.read_csv('file.csv', delimiter=';', low_memory=False)

        # Удаляем столбцы, указанные в списке
        df = df.drop(columns=columns_to_delete, axis=1)

        # Сохраняем DataFrame в CSV-файл
        df.to_csv('file.csv', sep=';', index=False)
    except:
        pass
    # Загружаем данные из CSV-файла
    df = pd.read_csv('file.csv', sep=';', low_memory=False)

    module.get_memory_info()

    # Группируем данные по городу
    groups = df.groupby('Город')
    # Создаем отдельный CSV-файл для каждой группы
    for city, group in groups:
        # Удаляем столбец 'Город'
        try:
            group = group.drop('Город', axis=1)
        except:
            pass
        try:
            # Удаляем столбцы с пустыми значениями
            group = group.dropna(axis=1, how='all')
        except:
            pass

        filename = f"{city}.csv"
        group.to_csv(filename, index=False, sep=';')
    os.remove('file.csv')

    module.send_data_to_adapter()
    module.send_end_parsing_status_cmc()

except Exception as e:
    logging.error(f'in inrost_group.py: {e}')
    module.send_error_to_cmc(f'in inrost_group.py: {str(e)[:50]}')
