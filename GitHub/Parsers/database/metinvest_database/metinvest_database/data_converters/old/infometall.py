#
# '' ['Мечел (Чср)', 'Мечел (Нсб)', 'Мечел (Крсн)', 'Мечел (Орен)', 'Мечел (Екб)', 'Мечел (Кмр)', 'Мечел (СПб)', 'УТК (Кург)', 'УТК (Кург)', 'Новосаратовка (СПб)']
#

from metinvest_database.shared_models import *
from metinvest_database.uploader_mock import *

PARSER_CODE = 'infometall'


SUPPLIER_FIELD = 'Металлобаза'

PHONE_FIELD = 'Телефон'

CATEGORY_FIELD = 'Категория'
SECTION_FIELD = 'Раздел'
CHARACTERISTIC_FIELD = 'Материал'

PRICE_FIELD = 'Цена'

EXCLUDE_KEYS = [SUPPLIER_FIELD, PHONE_FIELD, CATEGORY_FIELD, SECTION_FIELD, CHARACTERISTIC_FIELD, PRICE_FIELD]


parser = Parser.objects.get(code=PARSER_CODE)

def create_all():

  cities = {}
  suppliers = {}
  suppliers_cities = {}

  categories = {}

  duplicate_products = {}

  i = 0
  pre_products = TemporaryPreProduct.objects.filter(parser=PARSER_CODE)
  total = pre_products.count()
  for pre_product in pre_products.all():
    i += 1
    if i % 100 == 0:
      print('{} / {}'.format(i, total))

    data = eval(pre_product.data)

    supplier_field = data[SUPPLIER_FIELD]

    if '(' in supplier_field:
      city_name = supplier_field.split('(')[-1].strip().split(')')[-2]
      supplier_name = data[SUPPLIER_FIELD].split('(')[-2].strip()
    else:
      city_name = 'Не определен'
      supplier_name = supplier_field

    if city_name not in cities.keys():
      if not City.objects.filter(code=city_name).all():
        city_entity = City(name=city_name, code=city_name)
        city_entity.save()

      cities[city_name] = City.objects.get(code=city_name)
    city = cities[city_name]

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
    characteristic_name = data[CHARACTERISTIC_FIELD]

    united_category = '{}, {}, {}'.format(category_name, section_name, characteristic_name)
    if united_category not in categories.keys():
      if not Category.objects.filter(parser=parser, name=united_category).all():
        category_entity = Category(parser=parser, name=united_category)
        category_entity.save()
      categories[united_category] = Category.objects.get(parser=parser, name=united_category)
    category = categories[united_category]

    product_name = "cм. категорию + характеристики"
    product_data = {k: v for k, v in sorted(data.items()) if k not in EXCLUDE_KEYS}
    price = data.get(PRICE_FIELD, '')

    products = Product.objects.filter(parser=parser, category=category, supplier_city=supplier_city, name=product_name, code=product_name, data=product_data,
                           price=price).all()
    if not products:
      product_entity = Product(parser=parser, category=category, supplier_city=supplier_city, name=product_name, code=product_name, data=product_data,
                               price=price)
      product_entity.save()
    else:
      if products[0].id not in duplicate_products.keys():
        duplicate_products[products[0].id] = pre_product.id
      else:
        print('{}: {}, {}'.format(products[0].id, duplicate_products[products[0].id], pre_product.id))


    pre_product.maked = True
    pre_product.save()

    #FIXME update
