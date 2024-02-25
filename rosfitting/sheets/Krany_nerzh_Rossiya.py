import time

import rosfitting_parser_control_module as module
from model.product import Product


def parser(workbook):
    sheet_name = "Краны нерж. Россия"

    products = []

    sheet = workbook[sheet_name]

    category = 'Краны нержавеющие'
    last_diameter = None
    for row in sheet.iter_rows(min_row=3, max_row=50, max_col=6, values_only=True):

        time.sleep(module.PAUSE)
        # STATUS: PID=11587 CPU:5.4% RAM:0.8%  124MB

        for index, element in enumerate([3, 4, 5, 6]):

            time.sleep(module.PAUSE)
            # STATUS: PID=11647 CPU:5.2% RAM:0.8%  127MB

            name = sheet.cell(row=2, column=element).value
            price = row[index+2]
            diameter = row[0]
            type_size = row[1]

            if diameter is not None:
                last_diameter = diameter
            product = Product(name=name, diameter=last_diameter, type_size=type_size, price=price, category=category)
            products.append(product)

    workbook.close()
    return products