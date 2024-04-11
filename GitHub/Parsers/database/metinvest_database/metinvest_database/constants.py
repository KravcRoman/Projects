from dataclasses import dataclass


@dataclass(init=False, frozen=True)
class Constant:
    """
        Собирательный класс констант общего назначения
    """
    CATEGORY: str = "category"
    CITY: str = "city"
    CODE: str = 'code'
    DATA: str = "data"
    EMAIL: str = 'email'
    NAME: str = "name"
    PARSER: str = "Parsers1"
    PHONE: str = 'phone'
    PRICE: str = "price"
    SUPPLIER: str = "supplier"
    URL: str = 'url'


@dataclass(init=False, frozen=True)
class Code:
    """
        Собирательный класс констант кодов
    """
    CATEGORY_CODE: str = 'category_code'
    CITY_CODE: str = 'city_code'
    PARSER_CODE: str = 'parser_code'
    SUPPLIER_CODE: str = 'supplier_code'
