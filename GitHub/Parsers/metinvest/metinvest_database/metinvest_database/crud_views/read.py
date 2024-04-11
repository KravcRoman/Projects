from django.http import JsonResponse

from metinvest_database.shared_models import Parser, City, Supplier, SupplierCity, Category, Field, Product

from main import *

WITH_CITIES = 'with_cities'
CITIES = 'cities'


def get_parser(request):
  data = get_body_or_error(request)

  code = data[CODE]
  parser = Parser.objects.get(code=code)

  return JsonResponse({'result': 'ok', 'data': parser.to_json()})


def get_parsers(request):
  data = get_body_or_error(request)

  parsers = Parser.objects.all()

  return JsonResponse({'result': 'ok', 'data': [parser.to_json() for parser in parsers]})


def get_supplier(request):
  data = get_body_or_error(request)

  supplier_code = data[CODE]
  supplier = Supplier.objects.get(code=supplier_code)
  result_data = supplier.to_json()

  with_cities = data.get(WITH_CITIES, '')
  if with_cities:
    cities = [supplier_city.city.to_json() for supplier_city in SupplierCity.objects.filter(supplier=supplier)]
    result_data[CITIES] = cities

  return JsonResponse({'result': 'ok', 'data': 'result_data'})



def get_suppliers(request):
  data = get_body_or_error(request)

  suppliers = Supplier.objects.all()

  with_cities = data.get(WITH_CITIES, '')
  if with_cities:
    result_data = []
    for supplier in suppliers:
      supplier_result_data = supplier.to_json()
      cities = [supplier_city.city.to_json() for supplier_city in SupplierCity.objects.filter(supplier=supplier)]
      supplier_result_data[CITIES] = cities
  else:
    result_data = [supplier.to_json() for supplier in suppliers]

  return JsonResponse({'result': 'ok', 'data': result_data})



def get_city(request):
  data = get_body_or_error(request)

  code = data[CODE]
  city = City.objects.get(code)

  return JsonResponse({'result': 'ok', 'data': city.to_json()})

def get_cities(request):
  data = get_body_or_error(request)

  cities = City.objects.all()

  return JsonResponse({'result': 'ok', 'data': [city.to_json() for city in cities]})



def get_category(request):
  data = get_body_or_error(request)

  code = data[CODE]
  category = Category.objects.get(code=code)

  return JsonResponse({'result': 'ok', 'data': category.to_json()})

def get_categories(request):
  data = get_body_or_error(request)

  categories = Category.objects.all()

  return JsonResponse({'result': 'ok', 'data': [category.to_json() for category in categories]})



def get_field(request):
  data = get_body_or_error(request)

  code = data[CODE]
  field = Field.objects.get(code=code)

  return JsonResponse({'result': 'ok', 'data': field.to_json()})

def get_fields(request):
  data = get_body_or_error(request)

  fields = Field.objects.all()

  return JsonResponse({'result': 'ok', 'data': [field.to_json() for field in fields]})



def get_product(request):
  data = get_body_or_error(request)

  code = data[CODE]
  product = Product.objects.get(code=code)

  return JsonResponse({'result': 'ok', 'data': product.to_json()})

def get_products(request):
  data = get_body_or_error(request)

  products = Product.objects.all()

  return JsonResponse({'result': 'ok', 'data': [product.to_json() for product in products]})
