from metinvest_database.shared_models import *
from metinvest_database.uploader_mock import *

PARSER_CODE = 'sds_center'

PRICE_FIELD = 'price'

NAME_FIELD = 'name'

CATEGORY_FIELD = 'categories'

EXCLUDE_KEYS = [NAME_FIELD, PRICE_FIELD, CATEGORY_FIELD]


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

    null = None
    data = eval(pre_product.data)

    city_name = 'Москва' #data[SUPPLIER_FIELD].split('(')[-metinvest].strip().split(')')[-2]

    if city_name not in cities.keys():
      if not City.objects.filter(code=city_name).all():
        city_entity = City(name=city_name, code=city_name)
        city_entity.save()

      cities[city_name] = City.objects.get(code=city_name)
    city = cities[city_name]

    supplier_name = 'Современные Дренажные Системы' #data[SUPPLIER_FIELD].split('(')[-2].strip()
    supplier_phone = ''#data[PHONE_FIELD]

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

    united_category = category_name #'{}, {}, {}'.format(category_name, section_name, subsection_name)
    if united_category not in categories.keys():
      if not Category.objects.filter(parser=parser, name=united_category).all():
        category_entity = Category(parser=parser, name=united_category)
        category_entity.save()
      categories[united_category] = Category.objects.get(parser=parser, name=united_category)
    category = categories[united_category]

    product_name = data[NAME_FIELD]
    product_data = {k: v for k, v in sorted(data.items()) if k not in EXCLUDE_KEYS}
    price = data.get(PRICE_FIELD, '')
    if not Product.objects.filter(parser=parser, category=category, supplier_city=supplier_city, name=product_name, code=product_name, data=product_data,
                                  price=price).all():
      product_entity = Product(parser=parser, category=category, supplier_city=supplier_city, name=product_name, code=product_name, data=product_data,
                               price=price)
      product_entity.save()

    pre_product.maked = True
    pre_product.save()

    #FIXME update
