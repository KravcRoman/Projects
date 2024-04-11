# grandline
#
# Price, OldPrice
#
# CategoryId
#
# Name, Description
#
# Params

from metinvest_database.shared_models import *
from metinvest_database.uploader_mock import *

PARSER_CODE = 'inrost_group'
CITY_FIELD = 'Город'


CATEGORY_FIELD = 'Основной раздел'
SECTION_FIELD = 'Подраздел'
CHARACTERISTIC_FIELD = 'Подраздел 2'

PRICE_FIELDS = ['Цена за 1м с НДС', 'Цена за 1тс НДС']

NAME_FIELD = 'Наименование'

EXCLUDE_KEYS = [CATEGORY_FIELD, SECTION_FIELD, NAME_FIELD]
for field in PRICE_FIELDS:
  EXCLUDE_KEYS.append(field)

parser = Parser.objects.get(code=PARSER_CODE)

def create_all():

  cities = {}
  suppliers = {}
  suppliers_cities = {}

  categories = {}

  i = 0
  pre_products = TemporaryPreProduct.objects.filter(parser=PARSER_CODE)
  total = pre_products.count()
  for pre_product in pre_products.all():
    i += 1
    if i % 100 == 0:
      print('{} / {}'.format(i, total))

    data = eval(pre_product.data)

    city_name = data.get(CITY_FIELD, 'Не определен')

    if city_name not in cities.keys():
      if not City.objects.filter(code=city_name).all():
        city_entity = City(name=city_name, code=city_name)
        city_entity.save()

      cities[city_name] = City.objects.get(code=city_name)
    city = cities[city_name]

    supplier_name = 'Инрост'
    supplier_phone = '8 (800) 500 86 23'

    if supplier_name not in suppliers.keys():
      if not Supplier.objects.filter(code=supplier_name):
        supplier_entity = Supplier(parser=parser, name=supplier_name, code=supplier_name, phone=supplier_phone)
        supplier_entity.save()

      suppliers[supplier_name] = Supplier.objects.get(code=supplier_name)
    supplier = suppliers[supplier_name]

    supplier_city_key = '{} {}'.format(supplier_name, city_name)
    if supplier_city_key not in suppliers_cities.keys():
      if not SupplierCity.objects.filter(supplier=supplier, city=city).all():
        supplier_city_entity = SupplierCity(supplier=supplier, city=city)
        supplier_city_entity.save()

      suppliers_cities[supplier_city_key] = SupplierCity.objects.get(supplier=supplier, city=city)
    supplier_city = suppliers_cities[supplier_city_key]

    category_name = data[CATEGORY_FIELD]
    #section_name = data[SECTION_FIELD]
    #characteristic_name = data[CHARACTERISTIC_FIELD]

    united_category = category_name #'{}, {}, {}'.format(category_name, section_name, characteristic_name)
    if united_category not in categories.keys():
      if not Category.objects.filter(parser=parser, name=united_category).all():
        category_entity = Category(parser=parser, name=united_category)
        category_entity.save()
      categories[united_category] = Category.objects.get(parser=parser, name=united_category)
    category = categories[united_category]

    product_name = data[NAME_FIELD]
    product_data = {k: v for k, v in sorted(data.items()) if k not in EXCLUDE_KEYS}
    prices = [data.get(price, '') for price in PRICE_FIELDS]
    price = ';'.join([price for price in prices if price])
    if not Product.objects.filter(parser=parser, category=category, supplier_city=supplier_city, name=product_name, code=product_name, data=product_data,
                                  price=price).all():
      product_entity = Product(parser=parser, category=category, supplier_city=supplier_city, name=product_name, code=product_name, data=product_data,
                               price=price)
      product_entity.save()

    pre_product.maked = True
    pre_product.save()

    #FIXME update
