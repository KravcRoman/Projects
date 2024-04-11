from django.http import JsonResponse

from metinvest_database.shared_models import Parser, City, Supplier, SupplierCity, Category, Field, Product

from main import *



def update_parser(request):
  data = get_body_or_error(request)

  code = data[CODE]
  parser = Parser.objects.get(code=code)

  name = data.get(NAME, '')
  if name:
    parser.name = name

  url = data.get(URL, '')
  if url:
    parser.url = url

  parser.save()

  return JsonResponse({'result': 'ok'})


def update_supplier(request):
  data = get_body_or_error(request)

  supplier_code = data[CODE]
  supplier = Supplier.objects.get(code=supplier_code)

  name = data.get(NAME, '')
  if name:
    supplier.name = name

  phone = data.get(PHONE, '')
  if phone:
    supplier.phone = phone

  email = data.get(EMAIL, '')
  if email:
    supplier.email = email

  supplier.save()


  cities_codes = data.get('cities_codes', [])
  if cities_codes:
    incoming_cities = City.objects.filter(code__in=cities_codes).all()

    supplier_city_codes = [supplier_city.city.code for supplier_city in SupplierCity.objects.filter(supplier=supplier)]

    cities_codes_to_add = subtract_cities_codes(incoming_cities, supplier_city_codes)
    cities_codes_to_remove = subtract_cities_codes(supplier_city_codes, incoming_cities)

    for city_code in cities_codes_to_add:
      supplier_city = SupplierCity(supplier=supplier, city=City.objects.get(city_code))
      supplier_city.save()

    for city_code in cities_codes_to_remove:
      supplier_city = SupplierCity(supplier=supplier, city=City.objects.get(city_code))
      supplier_city.remove()

  return JsonResponse({'result': 'ok'})


def update_city(request):
  data = get_body_or_error(request)

  code = data[CODE]
  city = City.objects.get(code)

  name = data.get(NAME, '')
  if name:
    city.name = name

  city.save()

  return JsonResponse({'result': 'ok'})


def update_category(request):
  data = get_body_or_error(request)

  code = data[CODE]
  category = Category.objects.get(code=code)

  name = data.get(NAME, '')
  if name:
    category.name = name

  category.save()

  return JsonResponse({'result': 'ok'})


def update_field(request):
  data = get_body_or_error(request)

  code = data[CODE]
  field = Field.objects.get(code=code)

  name = data(NAME, '')
  if name:
    field.name = name

  field.save()

  return JsonResponse({'result': 'ok'})


def update_product(request):
  data = get_body_or_error(request)

  code = data[CODE]
  product = Product.objects.get(code=code)

  name = data.get(NAME, '')
  if name:
    product.name = name

  product_data = data.get(DATA, '')
  if product_data:
    product.data = product_data

  price = data.get(PRICE, '')
  if  price:
    product.price = price

  product.save()

  return JsonResponse({'result': 'ok'})