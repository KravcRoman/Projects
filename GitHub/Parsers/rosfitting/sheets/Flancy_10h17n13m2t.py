import time

import rosfitting_parser_control_module as module
from model.product import Product


def parser(workbook):
    sheet_name = "Фланцы10х17н13м2т"

    products = []
    count_list = [6, 10, 16, 25, 40, 63, 160]

    sheet = workbook[sheet_name]

    category = 'Фланцы ГОСТ 12820 и Фланцы ГОСТ 12821, ст. 10х17н13м2т'
    name = sheet['A2'].value
    for row in sheet.iter_rows(min_row=5, max_row=23, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=10039 CPU:4.3% RAM:0.8%  127MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:4]):

            time.sleep(module.PAUSE)
            # STATUS: PID=10083 CPU:4.6% RAM:0.8%  127MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)

    workbook.close()
    return products
