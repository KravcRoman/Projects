import time

import rosfitting_parser_control_module as module
from model.product import Product


def parser(workbook):
    sheet_name = "Заглушки 12Х18Н10Т"

    products = []
    count_list = [6, 10, 16, 25, 40, 63, 160]

    sheet = workbook[sheet_name]

    category = 'Заглушки'
    name = f"{sheet['A1'].value}, {sheet['A2'].value}"
    for index in [1, 3]:

        time.sleep(module.PAUSE)
        # STATUS: PID=12627 CPU:5.4% RAM:0.8%  127MB

        for row in sheet.iter_rows(min_row=6, max_row=20, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=12642 CPU:5.7% RAM:0.8%  128MB

            type_size = row[0]
            price = row[1]

            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)

    name = sheet['F2'].value
    for row in sheet.iter_rows(min_row=6, max_row=24, min_col=6, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=12685 CPU:5.4% RAM:0.8%  128MB

        diameter = row[0]
        prices = row[1:]
        for index, price in enumerate(prices[:5]):

            time.sleep(module.PAUSE)
            # STATUS: PID=12713 CPU:5.3% RAM:0.8%  126MB

            price = price if price != "-" else None
            product = Product(name=name, diameter=diameter, count=count_list[index], price=price, category=category)
            products.append(product)

    return products
