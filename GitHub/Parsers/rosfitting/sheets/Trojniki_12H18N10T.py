import time

import rosfitting_parser_control_module as module
from model.product import Product


def parser(workbook):
    sheet_name = "Тройники 12Х18Н10Т"

    products = []

    sheet = workbook[sheet_name]

    category = 'Тройники'
    name = sheet['A2'].value
    for index in [1, 3, 5]:

        time.sleep(module.PAUSE)
        # STATUS: PID=12403 CPU:1.9% RAM:0.8%  131MB

        for row in sheet.iter_rows(min_row=6, max_row=28, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=12419 CPU:1.0% RAM:0.8%  127MB

            type_size = row[0]
            price = row[1]

            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)

    name = sheet['A32'].value
    for index in [1, 3, 5]:

        time.sleep(module.PAUSE)
        # STATUS: PID=12485 CPU:6.8% RAM:0.8%  127MB

        for row in sheet.iter_rows(min_row=36, max_row=48, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=12500 CPU:6.4% RAM:0.8%  124MB

            type_size = row[0]
            if type_size is None:
                continue

            price = row[1]

            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)

    name = sheet['A51'].value
    for index in [1, 3]:

        time.sleep(module.PAUSE)
        # STATUS: PID=12553 CPU:4.3% RAM:0.8%  128MB

        for row in sheet.iter_rows(min_row=54, max_row=59, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=12566 CPU:5.2% RAM:0.8%  129MB

            type_size = row[0]
            if type_size is None:
                continue

            price = row[1]

            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)
    return products
