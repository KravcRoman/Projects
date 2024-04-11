from django.http import JsonResponse

from metinvest_database.shared_models import Parser, City, Supplier, SupplierCity, Category, Field, Product

from main import *

def delete_parser(request):
  data = get_body_or_error(request)

  code = data[CODE]
  parser = Parser.objects.get(code=code)

  parser.delete()

  return JsonResponse({'result': 'ok'})


def delete_supplier(request):
  data = get_body_or_error(request)

  supplier_code = data[CODE]
  supplier = Supplier.objects.get(code=supplier_code)

  supplier.delete()



def delete_city(request):
  data = get_body_or_error(request)

  code = data[CODE]
  city = City.objects.get(code)

  city.delete()

  return JsonResponse({'result': 'ok'})


def delete_category(request):
  data = get_body_or_error(request)

  code = data[CODE]
  category = Category.objects.get(code=code)

  category.delete()

  return JsonResponse({'result': 'ok'})


def delete_field(request):
  data = get_body_or_error(request)

  code = data[CODE]
  field = Field.objects.get(code=code)

  field.delete()

  return JsonResponse({'result': 'ok'})


def delete_product(request):
  data = get_body_or_error(request)

  code = data[CODE]
  product = Product.objects.get(code=code)

  product.delete()

  return JsonResponse({'result': 'ok'})