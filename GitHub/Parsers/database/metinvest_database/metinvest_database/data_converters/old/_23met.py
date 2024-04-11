from metinvest_database.shared_models import *
from metinvest_database.uploader_mock import *

PARSER_CODE = '23met'

SUPPLIER_FIELD = 'Поставщик'
CITY_FIELD = 'Город'
PHONE_FIELD = 'Телефон'

CATEGORY_FIELD = 'Категория'
SECTION_FIELD = 'Раздел'
CHARACTERISTIC_FIELD = 'Характеристика'

NAME_FIELD = 'Наименование'

PRICE_FIELDS = ['Цена за 1кг, руб. с НДС_1', 'Цена2 за 1пог.м, руб. с НДС', 'Цена2 за 1т, руб. с НДС', 'Цена за 1шт., руб. с НДС_1',
                'Цена2 за 1м2, руб. с НДС', 'Цена за 1м2, руб. с НДС', 'Цена2 за 1шт., руб. с НДС', 'Цена за 1кг, руб. с НДС',
                'Цена за 1пог.м, руб. с НДС_1', 'Цена за 1пог.м, руб. с НДС', 'Цена за 1шт., руб. с НДС', 'Цена за 1т, руб. с НДС_1',
                'Цена за 1т, руб. с НДС']

EXCLUDE_KEYS = [SUPPLIER_FIELD, CITY_FIELD, PHONE_FIELD, CATEGORY_FIELD, SECTION_FIELD, CHARACTERISTIC_FIELD, NAME_FIELD]
for field in PRICE_FIELDS:
  EXCLUDE_KEYS.append(field)


parser = Parser.objects.get(code=PARSER_CODE)

def create_all():

  cities = {}
  suppliers = {}
  suppliers_cities = {}

  categories = {}

  i = 0
  pre_products = TemporaryPreProduct.objects.filter(parser=PARSER_CODE, maked=False)
  total = pre_products.count()
  for pre_product in pre_products.all():
    i += 1
    if i % 100 == 0:
      print('{} / {}'.format(i, total))

    data = eval(pre_product.data)

    city_name = data[CITY_FIELD]

    if city_name not in cities.keys():
      if not City.objects.filter(code=city_name).all():
        city_entity = City(name=city_name, code=city_name)
        city_entity.save()

      cities[city_name] = City.objects.get(code=city_name)
    city = cities[city_name]

    supplier_name = data[SUPPLIER_FIELD]
    supplier_phone = data[PHONE_FIELD]

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
    section_name = data[SECTION_FIELD]
    characteristic_name = data.get(CHARACTERISTIC_FIELD, '')

    united_category = '{}, {}, {}'.format(category_name, section_name, characteristic_name)
    if united_category not in categories.keys():
      if not Category.objects.filter(parser=parser, name=united_category).all():
        category_entity = Category(parser=parser, name=united_category)
        category_entity.save()
      categories[united_category] = Category.objects.get(parser=parser, name=united_category)
    category = categories[united_category]

    product_name = data.get(NAME_FIELD, '')
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
