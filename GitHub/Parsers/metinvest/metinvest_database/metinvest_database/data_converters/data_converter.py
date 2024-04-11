import hashlib

from metinvest_database.uploader_mock import TemporaryPreProduct
from metinvest_database.shared_models import *

class BaseConverter():
  def get_exclude_keys(self):
    raise NotImplementedError("Please Implement this method")

  def get_parser_code(self):
    raise NotImplementedError("Please Implement this method")

  def get_city(self, data):
    raise NotImplementedError("Please Implement this method")

  def get_supplier(self, data):
    raise NotImplementedError("Please Implement this method")

  def get_phone(self, data):
    raise NotImplementedError("Please Implement this method")

  def get_category_name(self, data):
    raise NotImplementedError("Please Implement this method")

  def get_product_name(self, data):
    raise NotImplementedError("Please Implement this method")

  def get_price(self, data):
    raise NotImplementedError("Please Implement this method")

  def get_time(self, data):
    raise NotImplementedError("Please Implement this method")

  def get_product_data(self, data):
    return {k: v for k, v in sorted(data.items()) if k not in self.get_exclude_keys()}

  def get_pre_hashes(self, data):

    without_price = '{} {} {} {} {} {}'.format(self.get_category_name(data),
                                               self.get_supplier(data),
                                               self.get_city(data),
                                               self.get_product_name(data),
                                               str(sorted(self.get_product_data(data))),
                                               self.get_parser_code())

    with_price = '{} {}'.format(without_price, self.get_price(data))

    hash_without_price = hashlib.sha256(without_price.encode()).hexdigest()
    hash_with_price = hashlib.sha256(with_price.encode()).hexdigest()

    return hash_without_price, hash_with_price

  def create_product(self, data, parser, cities, suppliers, suppliers_cities, categories):
    city_name = self.get_city(data)

    if city_name not in cities.keys():
      if not City.objects.filter(name=city_name).all():
        city_entity = City(name=city_name)
        city_entity.save()

      print(city_name)
      cities[city_name] = City.objects.get(name=city_name)
    city = cities[city_name]

    supplier_name = self.get_supplier(data)
    supplier_phone = self.get_phone(data)

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

    united_category = self.get_category_name(data)
    if united_category not in categories.keys():
      if not Category.objects.filter(parser=parser, name=united_category).all():
        category_entity = Category(parser=parser, name=united_category)
        category_entity.save()
      categories[united_category] = Category.objects.get(parser=parser, name=united_category)
    category = categories[united_category]

    product_name = self.get_product_name(data)
    price = self.get_price(data)

    product_data = self.get_product_data(data)

    if not Product.objects.filter(parser=parser, category=category, supplier_city=supplier_city, name=product_name,
                                  code=product_name, data=product_data, price=price).all():
      product_entity = Product(parser=parser, category=category, supplier_city=supplier_city, name=product_name,
                               code=product_name, data=product_data, price=price)
      product_entity.make_full_text()
      product_entity.parsed = self.get_time(data)
      product_entity.json_view = product_entity.to_json()
      product_entity.make_hash()
      product_entity.save()

    return cities, suppliers, suppliers_cities, categories



  #DEPRECATED
  def create_all(self):
    parser = Parser.objects.get(code=self.get_parser_code())

    cities = {}
    suppliers = {}
    suppliers_cities = {}
    categories = {}

    i = 0
    pre_products = TemporaryPreProduct.objects.filter(parser=self.get_parser_code())
    total = pre_products.count()

    for pre_product in pre_products.all():
      i += 1
      if i % 100 == 0:
        print('{} / {}'.format(i, total))

      data = eval(pre_product.data)

      cities, suppliers, suppliers_cities, categories = self.create_product(data, parser, cities, suppliers, suppliers_cities, categories)

      pre_product.maked = True
      pre_product.save()
