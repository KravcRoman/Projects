import time

import grandline_parser_control_module as module
from pydantic import BaseModel
from typing import List


class Offer(BaseModel):
    id: int
    available: bool
    url: str
    price: str = None
    oldprice: str = None
    currencyId: str = None
    categoryId: int = None
    picture: str = None
    store: bool
    delivery: bool
    pickup: bool
    name: str
    description: str = None
    sales_notes: str = None
    manufacturer_warranty: bool
    vendor: str = None
    params: List[str]

    @classmethod
    def from_xml_element(cls, xml_element):
        params = []
        for param_element in xml_element.findall('param'):

            # time.sleep(module.PAUSE)

            param_name = param_element.attrib.get('name')
            param_value = param_element.text.strip()
            if param_name and param_value:
                params.append(f'{param_name}: {param_value}')

        return cls(
            id=int(xml_element.attrib.get('id')),
            available=bool(xml_element.attrib.get('available')),
            url=xml_element.findtext('url'),
            price=xml_element.findtext('price') or '',
            oldprice=xml_element.findtext('oldprice') or '',
            currencyId=xml_element.findtext('currencyId') or '',
            categoryId=int(xml_element.findtext('categoryId') or 0),
            picture=xml_element.findtext('picture') or '',
            store=bool(xml_element.findtext('store')),
            delivery=bool(xml_element.findtext('delivery')),
            pickup=bool(xml_element.findtext('pickup')),
            name=xml_element.findtext('name'),
            description=xml_element.findtext('description') or '',
            sales_notes=xml_element.findtext('sales_notes') or '',
            manufacturer_warranty=bool(xml_element.findtext('manufacturer_warranty')),
            vendor=xml_element.findtext('vendor') or '',
            params=params
        )
