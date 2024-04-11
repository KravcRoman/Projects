import json

from django.db import models

from metinvest_database.shared_models import *




class TemporaryProduct(models.Model):
  parser = models.CharField(max_length=255, verbose_name="Парсер")
  data = models.TextField(max_length=255, verbose_name="Данные")
  maked = models.BooleanField(verbose_name="Обработано", default=False, null=True)

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")





#DEPRECATED
class TemporaryPreProduct(models.Model):
  parser = models.CharField(max_length=255, verbose_name="Парсер")
  data = models.TextField(max_length=255, verbose_name="Название")
  maked = models.BooleanField(verbose_name="Обработано", default=False)

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

#FIXME all
def makePre(parser):
  if parser:
    products = TemporaryProduct.objects.filter(parser=parser, maked=False).all()
  else:
    products = TemporaryProduct.objects.filter(maked=False).all()

  i = 0
  total = products.count()
  for product in products:
    i += 1

    if i % 10 == 0:
      print('{}/{}'.format(i, total))

    data = eval(product.data)

    for pre in data:
      pre_product = TemporaryPreProduct(parser=product.parser, data=json.dumps(pre))
      pre_product.save()

    product.maked = True
    product.save()


def create_parsers():
  for parser_name in TemporaryProduct.objects.values('Parsers1').distinct():
    if not Parser.objects.filter(name=parser_name, code=parser_name).all():
      parser = Parser(name=parser_name, code=parser_name)
      parser.save()

def get_all_fields(parser_name):
  all_fields = {}

  i = 0
  pres = TemporaryProduct.objects.filter(parser=parser_name).all()
  total = pres.count()

  parser = Parser.objects.get(code=parser_name)
  null = None

  for pre in pres:
   for product in eval(pre.data):
    i += 1
    if i % 100 == 0:
      print('{} {}/{}'.format(parser_name, i, total))



    if parser not in all_fields.keys():
      all_fields[parser] = []

    if product:
     try:
      for field in product.keys():
       if field not in all_fields[parser]:
        all_fields[parser].append(field)
     except:
       print('ERROR {}'.format(product))


  for parser_name in all_fields.keys():
    parser = Parser.objects.get(code=parser_name)

    for field_name in all_fields[parser_name]:
      if not Field.objects.filter(parser=parser, name=field_name, code=field_name).all():
        field = Field(parser=parser, name=field_name, code=field_name)
        field.save()



def show_field_values(parser, field_name):
  pre_products = TemporaryPreProduct.objects.filter(parser=parser)[:10]

  result = []
  for product in pre_products:
    result.append(eval(product.data)[field_name])

  print(result)





def rotate_parser_pallets(parser_code):
  parser = Parser.objects.get(code=parser_code)
  products = TemporaryProduct.objects.filter(parser=parser, maked=False).all()

  if parser_code == 'mmk':
    from metinvest_database.data_converters.mmk import MmkConverter
    data_converter = MmkConverter()
  elif parser_code == 'metall_service':
    from metinvest_database.data_converters.metall_service import MetallServiceConverter
    data_converter = MetallServiceConverter()
  else:
    print('Unknown converter for Parsers1 {}'.format(parser_code))
    return

  i = 0
  total = products.count()

  cities = {}
  suppliers = {}
  suppliers_cities = {}
  categories = {}

  no_changes_count = 0
  price_changed_count = 0
  new_products_count = 0

  for product in products:
    i += 1

    data = eval(product.data)

    g = 0
    total_g = len(data)
    for pre_data in data:
      g += 1

      if not g % 100:
        print('{}/{} {}/{}'.format(i, total, g, total_g))

      hash_without_price, hash_with_price = data_converter.get_pre_hashes(pre_data)

      with_price = Product.objects.filter(hash_with_price=hash_with_price)
      if with_price:
        with_price[0].parsed = data_converter.get_time(pre_data)
        with_price[0].json_view = with_price[0].to_json()
        with_price[0].save()
        no_changes_count += 1
      else:
        without_price = Product.objects.filter(hash_without_price=hash_without_price)
        if without_price:
          without_price[0].parsed = data_converter.get_time(pre_data)
          without_price[0].price = data_converter.get_price(pre_data)
          without_price[0].json_view = without_price[0].to_json()
          without_price[0].save()
          price_changed_count += 1
        else:
          cities, suppliers, suppliers_cities, categories = data_converter.create_product(pre_data, parser, cities, suppliers, suppliers_cities, categories)
          new_products_count += 1
    print('{}. {}/{}/{}'.format(i, no_changes_count, price_changed_count, new_products_count))
    product.delete()

  print('{}/{}/{}/{}'.format(no_changes_count, price_changed_count, new_products_count,
                             Product.objects.filter(parser=parser).count()-no_changes_count-price_changed_count-new_products_count))