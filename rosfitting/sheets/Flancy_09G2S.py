import time

import rosfitting_parser_control_module as module
from model.product import Product

def parser(workbook):
    sheet_name = "Фланцы 09Г2С"

    products = []
    count_list = [6, 10, 16, 25, 40, 63, 160]

    sheet = workbook[sheet_name]

    name = sheet['A2'].value
    category = 'Фланцы ГОСТ 33259-2015, ст. 09г2с или Фланцы ГОСТ 12820 и Фланцы ГОСТ 12821, ст. 09г2с'
    for row in sheet.iter_rows(min_row=5, max_row=23, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=8788 CPU:5.5% RAM:0.8%  130MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:4]):

            time.sleep(module.PAUSE)
            # STATUS: PID=8834 CPU:5.5% RAM:0.8%  125MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)

    name = sheet['G2'].value
    for row in sheet.iter_rows(min_row=5, max_row=23, min_col=7, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=8900 CPU:5.1% RAM:0.8%  124MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:3]):

            time.sleep(module.PAUSE)
            # STATUS: PID=8930 CPU:5.8% RAM:0.8%  127MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)

    workbook.close()
    return products
