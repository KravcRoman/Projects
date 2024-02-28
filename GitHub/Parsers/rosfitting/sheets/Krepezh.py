import time

import rosfitting_parser_control_module as module
from model.product import Product


def parser(workbook):
    sheet_name = "Крепеж"

    products = []

    sheet = workbook[sheet_name]

    category = 'Нержавеющий крепеж'
    name = sheet['A1'].value
    for index in [1, 3, 5]:

        time.sleep(module.PAUSE)
        # STATUS: PID=11790 CPU:14.4% RAM:0.8%  124MB

        for row in sheet.iter_rows(min_row=3, max_row=12, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=11806 CPU:5.2% RAM:0.8%  126MB

            type_size = row[0]
            if type_size is None:
                continue

            price = row[1]
            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)

    name = sheet['A13'].value
    for index in [1, 3, 5]:

        time.sleep(module.PAUSE)
        # STATUS: PID=11846 CPU:11.7% RAM:0.8%  130MB

        for row in sheet.iter_rows(min_row=15, max_row=21, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=11871 CPU:4.5% RAM:0.8%  128MB

            type_size = row[0]
            if type_size is None or type_size == "-":
                continue

            price = row[1]
            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)

    name = sheet['A22'].value
    for index in [1, 3, 5]:

        time.sleep(module.PAUSE)
        # STATUS: PID=11919 CPU:13.3% RAM:0.8%  128MB

        for row in sheet.iter_rows(min_row=24, max_row=26, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=11935 CPU:5.2% RAM:0.8%  127MB

            type_size = row[0]
            if type_size is None:
                continue

            price = row[1]
            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)

    name = sheet['A27'].value
    for index in [1, 3, 5]:

        time.sleep(module.PAUSE)
        # STATUS: PID=11958 CPU:13.6% RAM:0.7%  122MB

        for row in sheet.iter_rows(min_row=29, max_row=31, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=11970 CPU:5.2% RAM:0.8%  127MB

            type_size = row[0]
            if type_size is None:
                continue

            price = row[1]
            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)

    name = sheet['A32'].value
    for index in [1, 3, 5]:

        time.sleep(module.PAUSE)
        # STATUS: PID=11989 CPU:11.4% RAM:0.8%  131MB

        for row in sheet.iter_rows(min_row=34, max_row=37, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=12003 CPU:4.2% RAM:0.8%  127MB

            type_size = row[0]
            if type_size is None:
                continue

            price = row[1]
            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)

    workbook.close()
    return products
