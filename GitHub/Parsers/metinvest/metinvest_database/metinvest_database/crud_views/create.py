from django.http import JsonResponse

from metinvest_database.shared_models import Parser, City, Supplier, SupplierCity, Category, Field, Product

from main import *



def create_parser(request):
  data = get_body_or_error(request)

  name = data[NAME]
  code = data[CODE]
  url = data[URL]

  if Parser.objects.filter(code=code).all():
    raise Exception('Parser with code {} already exists'.format(code))

  parser = Parser(name=name, code=code, url=url)
  parser.save()

  return JsonResponse({'result': 'ok'})


def create_supplier(request):
  data = get_body_or_error(request)

  parser_code = data[PARSER_CODE]
  parser = Parser.objects.get(code=parser_code)  # орать будет

  name = data[NAME]
  code = data[CODE]
  phone = data.get(PHONE, '')
  email = data.get(EMAIL, '')

  if Supplier.objects.filter(code=code).all():
    raise Exception('Supplier with code {} already exists'.format(code))

  cities_codes = data.get('cities_codes', [])
  cities = City.objects.filter(code__in=cities_codes).all()
  if len(cities) != len(cities_codes):
    raise Exception('Cities with codes {} not found'.format(subtract_cities_codes(cities_codes, [city.code for city in cities])))

  supplier = Supplier(parser=parser, name=name, code=code, phone=phone, email=email)
  supplier.save()

  for city in cities:
    supplier_city = SupplierCity(supplier=supplier, city=city)
    supplier_city.save()

  return JsonResponse({'result': 'ok'})


def create_city(request):
  data = get_body_or_error(request)

  name = data[NAME]
  code = data[CODE]

  if City.objects.filter(code=code).all():
    raise Exception('City with code {} already exists'.format(code))

  city = City(name=name, code=code)
  city.save()

  return JsonResponse({'result': 'ok'})


def create_category(request):
  data = get_body_or_error(request)

  name = data[NAME]
  code = data[CODE]

  if Category.objects.filter(code=code).all():
    raise Exception('Category with code {} already exists'.format(code))

  category = Category(name=name, code=code)
  category.save()

  return JsonResponse({'result': 'ok'})


def create_field(request):
  data = get_body_or_error(request)

  parser_code = data[PARSER_CODE]
  parser = Parser.objects.get(code=parser_code)  # орать будет

  category_code = data[CATEGORY_CODE]
  category = Parser.objects.get(code=category_code)  # орать будет

  name = data[NAME]
  code = data[CODE]

  field = Field(parser=parser, category=category, name=name, code=code)
  field.save()

  return JsonResponse({'result': 'ok'})


def create_product(request):
  data = get_body_or_error(request)

  parser_code = data[PARSER_CODE]
  parser = Parser.objects.get(code=parser_code)  # орать будет

  category_code = data[CATEGORY_CODE]
  category = Parser.objects.get(code=category_code)  # орать будет

  supplier_code = data[SUPPLIER_CODE]
  supplier = Supplier.objects.get(code=supplier_code)  # орать будет

  city_code = data[CITY_CODE]
  city = City.objects.get(city_code)  # орать будет

  # supplier_code, city_code
  supplier_city = SupplierCity.objects.get(supplier=supplier, city=city)  # орать будет

  name = data[NAME]
  code = data[CODE]
  product_data = data[DATA]
  price = data[PRICE]

  product = Product(name=name, code=code, data=product_data, price=price, parser=parser, category=category, supplier_city=supplier_city)
  product.save()

  return JsonResponse({'result': 'ok'})