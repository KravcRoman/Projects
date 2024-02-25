import time

import rosfitting_parser_control_module as module
from model.product import Product


def parser(workbook):
    sheet_name = "Фланцы12Х18Н10Т Китай"

    products = []
    count_list = [6, 10, 16, 25, 40, 63, 160]

    sheet = workbook[sheet_name]

    category = 'Фланцы ГОСТ 33259-2015, ст. 12х18н10т'
    name = sheet['A3'].value
    for row in sheet.iter_rows(min_row=6, max_row=26, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=10749 CPU:4.6% RAM:0.8%  125MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:4]):

            time.sleep(module.PAUSE)
            # STATUS: PID=10786 CPU:4.9% RAM:0.8%  127MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)

    category = 'Фланцы ГОСТ 12820 и Фланцы ГОСТ 12821, ст. 12х18н10т'
    name = sheet['G3'].value
    for row in sheet.iter_rows(min_row=6, max_row=26, min_col=7, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=10884 CPU:5.8% RAM:0.8%  127MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:7]):

            time.sleep(module.PAUSE)
            # STATUS: PID=10915 CPU:6.3% RAM:0.8%  127MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)
    workbook.close()
    return products
