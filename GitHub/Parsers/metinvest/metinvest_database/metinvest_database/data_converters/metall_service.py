from metinvest_database.data_converters.data_converter import BaseConverter

class MetallServiceConverter(BaseConverter):

  # , 'Наим.,Диаметр', 'Марка,ширина', 'Гост,Диаметр', 'длина', 'Тех.хар', 'полка', 'Марка, диаметр', 'Марка,Ширина', 'Марка, Размер',
  # 'Ширина', 'Марка,Длина', 'Размер, марка', 'ширина', 'Наименование', 'Полка', 'Цена, т', 'Цена, шт', 'Марка, Ширина', 'Диаметр',
  # 'стенка', 'Размер', 'диаметр', '', 'Хар-ка', 'Размеры', 'размер', 'URL прайс-листа', 'Время парсинга', 'Телефон', 'Раздел', 'Цена',
  # 'Ед.изм', 'толщина', 'Марка']

  PARSER_CODE = 'metall_service'

  NAME_FIELD = 'Наименование'
  PHONE_FIELD = 'Телефон'
  SECTION = 'Раздел'
  TIME_FIELD = 'Время парсинга'

  PRICE_FIELDS = ['Цена', 'Цена, т', 'Цена, шт']

  def get_parser_code(self):
    return self.PARSER_CODE

  def get_product_name(self, data):
    return data.get(self.NAME_FIELD, '')

  def get_price(self, data):
    return '; '.join([data.get(price, '') for price in self.PRICE_FIELDS])

  def get_exclude_keys(self):
    exclude_fields = [self.NAME_FIELD, self.PHONE_FIELD, self.SECTION]
    for price_field in self.PRICE_FIELDS:
      exclude_fields.append(price_field)
    return exclude_fields

  def get_city(self, data):
    return 'Не определено'

  def get_supplier(self, data):
    return 'Металлсервис'

  def get_phone(self, data):
    return data[self.PHONE_FIELD]

  def get_category_name(self, data):
    return data[self.SECTION]

  def get_time(self, data):
    return data[self.TIME_FIELD]