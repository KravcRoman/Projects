import time

import rosfitting_parser_control_module as module
from model.product import Product


def parser(workbook):
    sheet_name = "Фланцы12Х18Н10Т Исполнение"

    products = []
    count_list = [6, 10, 16, 25, 40, 63, 160]

    sheet = workbook[sheet_name]

    category = 'Фланцы с исполнением ГОСТ 33259 - 2015, Фланцы с исполнением ГОСТ 12820, ГОСТ 12821, ст. 12х18н10т с исполнением'
    name = sheet['A2'].value
    for row in sheet.iter_rows(min_row=5, max_row=25, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=10249 CPU:5.7% RAM:0.8%  126MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:4]):

            time.sleep(module.PAUSE)
            # STATUS: PID=10283 CPU:5.5% RAM:0.8%  128MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)

    name = sheet['G2'].value
    for row in sheet.iter_rows(min_row=5, max_row=25, min_col=7, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=10342 CPU:4.8% RAM:0.8%  123MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:7]):

            time.sleep(module.PAUSE)
            # STATUS: PID=10377 CPU:5.4% RAM:0.8%  126MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)

    name = sheet['A30'].value
    for row in sheet.iter_rows(min_row=33, max_row=53, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=10462 CPU:3.1% RAM:0.8%  125MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:4]):

            time.sleep(module.PAUSE)
            # STATUS: PID=10496 CPU:1.3% RAM:0.8%  126MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)

    name = sheet['G30'].value
    for row in sheet.iter_rows(min_row=33, max_row=53, min_col=7, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=10517 CPU:5.0% RAM:0.8%  126MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:7]):

            time.sleep(module.PAUSE)
            # STATUS: PID=10553 CPU:5.5% RAM:0.8%  126MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)
    workbook.close()

    return products


