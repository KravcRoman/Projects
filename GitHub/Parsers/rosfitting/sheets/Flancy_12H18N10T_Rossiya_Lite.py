import time

import rosfitting_parser_control_module as module
from model.product import Product


def parser(workbook):
    sheet_name = "Фланцы12Х18Н10Т Россия Литье"

    products = []
    count_list = [6, 10, 16, 25, 40, 63, 160]

    sheet = workbook[sheet_name]

    category = 'Фланцы ГОСТ 33259-2015, ст. 12х18н10т или Фланцы ГОСТ 12820 и Фланцы ГОСТ 12821, ст. 12х18н10т'
    name = f"{sheet['A1'].value } {sheet['A2'].value}"
    for row in sheet.iter_rows(min_row=5, max_row=22, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=11058 CPU:3.9% RAM:0.8%  125MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:4]):

            time.sleep(module.PAUSE)
            # STATUS: PID=11089 CPU:3.3% RAM:0.7%  123MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)

    workbook.close()
    return products
