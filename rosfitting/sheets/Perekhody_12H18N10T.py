import time

import rosfitting_parser_control_module as module
from model.product import Product


def parser(workbook):
    sheet_name = "Переходы 12Х18Н10Т"

    products = []

    sheet = workbook[sheet_name]

    category = 'Переходы'
    name = sheet['A2'].value
    for index in [1, 3, 5]:

        time.sleep(module.PAUSE)
        # STATUS: PID=12215 CPU:11.7% RAM:0.8%  126MB

        for row in sheet.iter_rows(min_row=6, max_row=41, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=12232 CPU:5.5% RAM:0.8%  125MB

            type_size = row[0]
            price = row[1]

            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)

    name = sheet['A43'].value
    for index in [1, 3, 5]:

        time.sleep(module.PAUSE)
        # STATUS: PID=12305 CPU:12.6% RAM:0.8%  129MB

        for row in sheet.iter_rows(min_row=47, max_row=51, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=12321 CPU:6.4% RAM:0.8%  126MB

            type_size = row[0]
            if type_size is None:
                continue

            price = row[1]

            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)
    return products
