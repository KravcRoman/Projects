import time

import rosfitting_parser_control_module as module
from model.product import Product


def parser(workbook):
    sheet_name = "Отводы 12Х18Н10Т"

    products = []

    sheet = workbook[sheet_name]

    category = 'Отводы'
    name = sheet['A2'].value
    for index in [1, 3, 5, 8, 10, 12]:

        time.sleep(module.PAUSE)
        # STATUS: PID=12072 CPU:7.0% RAM:0.8%  127MB

        name = name if index < 8 else sheet['H2'].value
        for row in sheet.iter_rows(min_row=6, max_row=39, min_col=index, values_only=True):

            time.sleep(module.PAUSE)
            # STATUS: PID=12087 CPU:5.4% RAM:0.8%  126MB

            type_size = row[0]
            price = row[1]

            price = price if price != "-" else None
            product = Product(name=name, price=price, type_size=type_size, category=category)
            products.append(product)
    return products
