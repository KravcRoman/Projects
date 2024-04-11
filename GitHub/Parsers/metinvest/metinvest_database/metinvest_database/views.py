import json
import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django import forms
from django.core import serializers

from metinvest_database.models import *
from metinvest_database.settings import MEDIA_ROOT

from metinvest_database.crud_views.main import *
from metinvest_database.utils.objects import Null
from metinvest_database.utils.utils import *



@csrf_exempt
def upload_raw(request):
  data = json.loads(get_body_or_error(request))

  parser = data['Parsers1']
  data = data[DATA]

  product = TemporaryProduct(parser=parser, data=data)
  product.save()

  return JsonResponse({'result': 'ok'})



@csrf_exempt
@login_required
def doc(request):
  products_count = Product.objects.all().count()
  categories_count = Category.objects.all().count()
  suppliers_count = Supplier.objects.all().count()
  cities_count = City.objects.all().count()
  parsers_count = Parser.objects.all().count()

  return render(request, 'lk_kp.html', {
    'products_count': get_digits_formatted(products_count),
    'categories_count': get_digits_formatted(categories_count),
    'suppliers_count': get_digits_formatted(suppliers_count),
    'cities_count': get_digits_formatted(cities_count),
    'parsers_count': get_digits_formatted(parsers_count)
  })

@csrf_exempt
@login_required
def index(request):
  main_statistics = Statistics.objects.filter(type=Statistics.Type.MAIN).first()

  unique_cities = UniqueCity.objects.order_by('name').all()

  num_columns = 5
  num_rows = len(unique_cities) // num_columns + 1

  cities = []
  for i in range(num_rows):
    cities.append(unique_cities[i::num_rows])


  return render(request, 'index.html', {
    'products_count': get_digits_formatted(main_statistics.products_count),
    'categories_count': get_digits_formatted(main_statistics.categories_count),
    'suppliers_count': get_digits_formatted(main_statistics.suppliers_count),
    'cities_count': get_digits_formatted(main_statistics.cities_count),
    'parsers_count': get_digits_formatted(main_statistics.parsers_count),
    'cities': cities
  })

@csrf_exempt
@login_required
def upload(request):
  parsers = [parser.name for parser in Parser.objects.all()]
  context = {'parsers': parsers}

  if request.POST:
    if request.POST['Parsers1'] != '1C':
      context['result'] = 'error'
      context['error'] = 'Адаптер для прайслиста не найден. Выберите другой источник данных либо свяжитесь с администратором'
      return context

    file = request.FILES["pricelist"]
    with open("{}/{}".format(MEDIA_ROOT, file.name), "wb+") as destination:
      for chunk in file.chunks():
        destination.write(chunk)



    return render(request, 'upload.html', context)

  return render(request, 'upload.html', context)







def clean_string(input_string):
  # Оставляем только символы русского и английского алфавитов, цифры, дефисы и пробелы
  cleaned_string = re.sub(r'[^a-zA-Zа-яА-Я0-9\- ]', '', input_string)
  return prepare_for_search(cleaned_string.strip())


def replace_with_selected_by_html_word(words, source_string, prepared_string):
  START_REPLACE_EXPRESSION = "<span style='color: red'>"
  END_REPLACE_EXPRESSION = '</span>'

  for word in words:
    if word in prepared_string:
      start_index = prepared_string.index(word)
      end_index = start_index + len(word)

      source_string = source_string[:start_index] + START_REPLACE_EXPRESSION + source_string[start_index:end_index] + \
                      END_REPLACE_EXPRESSION + source_string[end_index:]
      prepared_string = prepared_string[:start_index] + START_REPLACE_EXPRESSION + prepared_string[start_index:end_index] + \
                      END_REPLACE_EXPRESSION + prepared_string[end_index:]

  return source_string

from django.db.models import Q, Max, Min
from metinvest_database.constants import DATA, NAME, CATEGORY, SUPPLIER, CITY

def replace_json_data(words, json_data):

  if not json_data:
    json_data = {}

  result = {}
  for key in json_data.keys():
    if json_data[key]:
      if key == DATA:
        result[key] = {k: replace_with_selected_by_html_word(words, v, prepare_for_search(v)) for k, v in json_data[key].items()}
      elif key == 'html' or key == CITY:
        result[key] = replace_with_selected_by_html_word(words, json_data[key], prepare_for_search(json_data[key]))
      elif key == CATEGORY or key == SUPPLIER:
        result[key] = json_data[key]
        result[key][NAME] = replace_with_selected_by_html_word(words, json_data[key][NAME], prepare_for_search(json_data[key][NAME]))
        result[key]['parser_name'] = replace_with_selected_by_html_word(words, json_data[key]['Parsers1'], prepare_for_search(json_data[key]['Parsers1']))
      else:
        result[key] = json_data[key]
  return result



from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Cast



def main_filter(query, cities):
  query = query.replace(',', ' ')

  words = prepare_for_search(query).split()

  if cities:
    # for city in cities:
    #   words.append(city)

    print('metinvest')
    #print(cities)

    filtered_products = Product.objects.filter(
      supplier_city__city__code__in=cities
    ).filter(
      *[Q(product_full_text__icontains=word) for word in words]
    )

    print('metinvest.metinvest')
    # print(Product.objects.filter(
    #   supplier_city__city__code__in=cities
    # ).filter(
    #   *[Q(product_full_text__icontains=word) for word in words]
    # ).query)

  else:

    print('metinvest')
    filtered_products = Product.objects.filter(*[Q(product_full_text__icontains=word) for word in words])

  #vector = SearchVector('product_full_text')
  #search_query = SearchQuery(prepare_for_search(query))

  print('2')

  #filtered_products = filtered_products.annotate(rank=SearchRank(vector, search_query)).order_by('-rank')

  print('3')

  return words, filtered_products

@csrf_exempt
@login_required
def search(request):
  if request.POST and 'query' in request.POST:
    print('POST: {}'.format(request.POST))

    query = request.POST['query']
    cities = request.POST.getlist('cities[]')

    if query:
      if 'limit' in request.POST:
        limit = int(request.POST['limit'])
      else:
        limit = 30

      words, filtered_products = main_filter(query, cities)

      print('4')

      if 'products_offset' in request.POST:
        offset = int(request.POST['products_offset'])
        products = filtered_products[offset:offset+limit]
      else:
        products = filtered_products[:limit]

      print('5')

      result = JsonResponse({"products": [replace_json_data(words, product.json_view if product.json_view else product.to_json()) for product in products]})

      print('6')

      return result

  return JsonResponse({"products": []})



@csrf_exempt
@login_required
def count(request):
  if request.POST and 'query' in request.POST:
    print('POST: {}'.format(request.POST))

    query = request.POST['query']
    cities = request.POST.getlist('cities[]')

    print('---{}---'.format(cities))
    if query:

      words, filtered_products = main_filter(query, cities)

      products_total = filtered_products.values_list('pk', flat=True).count()

      print('++{}++'.format(products_total))

      result = JsonResponse({"products_total": products_total})


      return result

  return JsonResponse({"products_total": []})




@csrf_exempt
@login_required
def get_categories(request):

  if request.POST and 'query' in request.POST:
    print('POST: {}'.format(request.POST))

    query = request.POST['query']
    if query:
      query = query.replace(',', ' ')

      splitted_query = query.split()

      words = prepare_for_search(query).split()

      filtered_categories = Category.objects.filter(*[Q(name__icontains=t) for t in splitted_query])

      categories_total = filtered_categories.count()
      categories = filtered_categories[:10]

      result = JsonResponse({
        "categories": [replace_json_data(words, category.json_view) for category in categories],
        "categories_total": categories_total
      })

      return result

  return JsonResponse({"categories": [], "categories_total": []})

@csrf_exempt
@login_required
def filter_cities(request):
  if request.POST and 'query' in request.POST:
    return JsonResponse({city.id: city.name for city in UniqueCity.objects.filter(name__startswith=request.POST['query'])[:3]})
  return JsonResponse({})


def update_supplier(request):

    if request.method == 'POST':
      supplier_name = request.POST.get('supplier_name')

      try:
        supplier = Supplier.objects.get(supplier_name=supplier_name)
      except Supplier.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Поставщик не найден'})

      supplier.manager = request.POST.get('manager')
      supplier.manager_schedule = request.POST.get('manager_schedule')
      supplier.mobile_phone = request.POST.get('mobile_phone')
      supplier.work_phone = request.POST.get('work_phone')
      supplier.email = request.POST.get('email')
      supplier.other_contacts = request.POST.get('other_contacts')
      supplier.rating = request.POST.get('rating')
      supplier.rating_notes = request.POST.get('rating_notes')
      supplier.delivery_conditions = request.POST.get('delivery_conditions')
      supplier.save()

      return JsonResponse({'success': True, 'message': 'Поставщик успешно обновлен'})
    else:
      return JsonResponse({'success': False, 'message': 'Метод запроса не поддерживается'})



@csrf_exempt
@login_required
def all_suppliers_query(request):
    query = request.POST.get('query')
    all_suppliers = Supplier.objects.all()

    suppliers_data = serializers.serialize('json', all_suppliers)

    suppliers_list = json.loads(suppliers_data)
    suppliers_list_sorted = []
    for supplier in suppliers_list:
        supplier_name = supplier.get('fields', {}).get('name')
        if query.lower() in supplier_name.lower():
            suppliers_list_sorted.append(supplier)

    return JsonResponse({'suppliers': suppliers_list_sorted})


@csrf_exempt
@login_required
def all_suppliers(request):
    # Получаю все поставщики
    all_suppliers = Supplier.objects.all()
    suppliers_data = serializers.serialize('json', all_suppliers)

    suppliers_list = json.loads(suppliers_data)

    return JsonResponse({'suppliers': suppliers_list})



def create_supplier(request):

    if request.method == 'POST':
      supplier_form = SupplierForm(request.POST)

      if supplier_form.is_valid():
        supplier_form.save()
        return redirect('product-views')

    else:
      supplier_form = SupplierForm()

    return render(request, 'create_supplier.html', {'supplier_form': supplier_form})


def create_supplier_warehouse(request):
  if request.method == 'POST':
    supplier_warehouse_form = WarehouseForm(request.POST)

    if supplier_warehouse_form.is_valid():
      supplier_warehouse_form.save()
      return redirect('product-views')

  else:
    supplier_warehouse_form = WarehouseForm()

  return render(request, 'create_warehouse.html', {'supplier_warehouse_form': supplier_warehouse_form})


def create_supplier_office(request):
  if request.method == 'POST':
    supplier_office_form = OfficeForm(request.POST)

    if supplier_office_form.is_valid():
      supplier_office_form.save()
      return redirect('product-views')

  else:
    supplier_office_form = OfficeForm()

  return render(request, 'create_office.html', {'supplier_office_form': supplier_office_form})

def products(request):
  pass

def sites(request):
  from metinvest_database.uploader_mock import TemporaryProduct
  from metinvest_database.models import ParserStatistics

  context = {}
  context['parsers'] = {}

  parser_names = [parser_code_obj[0] for parser_code_obj in TemporaryProduct.objects.all().order_by('Parsers1').values_list('Parsers1').distinct()]
  for parser in Parser.objects.all():
    if parser.code not in parser_names:
      parser_names.append(parser.code)

  for parser_code in sorted(parser_names):
    parsers = Parser.objects.filter(code=parser_code)

    if parsers:
      parser = parsers[0]
      context['parsers'][parser.code] = Null()
      if ParserStatistics.objects.filter(parser__id=parser.id):
        context['parsers'][parser.code].statistics = ParserStatistics.objects.get(parser__id=parser.id)
        if parser_code in ('1C', '23met', 'infometall', 'poiskmetalla'):
          context['parsers'][parser.code].status = 'Не обновляется'
          context['parsers'][parser.code].status_color = 'darkred'
        elif parser_code in ('mmk', 'metall_service'):
          context['parsers'][parser.code].status = 'Есть полный цикл'
          context['parsers'][parser.code].status_color = 'darkgreen'
        elif parser_code == 'medexe':
          context['parsers'][parser_code].status = 'Нет адаптера'
          context['parsers'][parser_code].status_color = 'darkgrey'
        else:
          context['parsers'][parser.code].status = 'Есть адаптер'
          context['parsers'][parser.code].status_color = '#8B8000'
      else:
        context['parsers'][parser.code].statistics = ParserStatistics()
    else:
      context['parsers'][parser_code] = Null()
      context['parsers'][parser_code].status = 'Нет адаптера'
      context['parsers'][parser_code].status_color = 'darkgrey'

    pre_products = TemporaryProduct.objects.filter(parser=parser_code)
    context['parsers'][parser_code].pre_count = pre_products.count()*500
    min = pre_products.aggregate(Min('created_at'))['created_at__min']
    max = pre_products.aggregate(Max('created_at'))['created_at__max']
    context['parsers'][parser_code].dates = '{} - {}'.format(
      min.strftime("%d.%m.%Y") if min else 'Отсутствует',
      max.strftime("%d.%m.%Y") if max else 'Отсутствует'
    )

  return render(request, 'models/parsers.html', context)

def cities(request):
  context = {}

  if request.GET and 'sort' in request.GET:
    context['cities'] = [city for city in UniqueCity.objects.order_by(request.GET['sort'], 'name').all()]
  else:
    context['cities'] = [city for city in UniqueCity.objects.order_by('name').all()]

  for city in context['cities']:
    statistics = Statistics.objects.get(type=Statistics.Type.CITY, id=city.id)
    city.parsers = statistics.parsers_count
    city.suppliers = statistics.suppliers_count
    city.products = statistics.products_count

  return render(request, 'models/cities.html', context)



import pdfkit

from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings

@csrf_exempt
def generate_pdf(request):
    if request.method == 'POST':
        #try:
            data = json.loads(request.body.decode('utf-8'))

            product_data = data.get('selectedProducts', [])
            amount_data = data.get('productCosts', [])
            companyInfo = data.get('companyInfo', {})
            supplier = data.get('supplier', {})
            title = data.get('title', '')
            buyer = data.get('buyer', '')
            static_url = '%s://%s%s' % (request.scheme, request.get_host(), settings.STATIC_URL)

            print( static_url)
            context = {
                'product_data': product_data,
                'amount_data': amount_data,
                'companyInfo': companyInfo,
                'supplier': supplier,
                'title': title,
                'buyer': buyer,
                'STATIC_URL': static_url
            }

            template = get_template('kp_pdf.html')

            html = template.render(context)

            #try:
            options = {
                       'page-size': 'A4',
                        'encoding': 'UTF-8',
                        'enable-local-file-access': True,
                }
            pdf_content = pdfkit.from_string(html, False, options=options)
            #except Exception as e:
            #    return HttpResponse("An error occurred during PDF generation", status=500)

            if len(pdf_content) > 0:
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="file.pdf"'
                return response
            else:
                return HttpResponse("PDF content is empty", status=500)

        #except Exception as e:
        #    return HttpResponse(str(e), status=500)

    return HttpResponse("Invalid request", status=400)




def categories(request):
  pass

def suppliers(request):
  suppliers = UniqueSupplier.objects.all().order_by('name')

  return render(request, 'models/suppliers.html', {'suppliers': suppliers})


def product(request):
  pass

def site(request, id):
  pass

def category(request, id):
  pass

import random



@login_required()
def supplier(request, id):
  unique_supplier = UniqueSupplier.objects.get(id=id)
  manager = Manager.objects.filter(unique_supplier=unique_supplier).order_by('-id').first()

  if request.POST:
    if 'comment' in request.POST:
      unique_supplier.comment = request.POST['comment']
      unique_supplier.save()

      manager_name = request.POST['manager_name']
      manager_phone = request.POST['manager_phone']
      manager_email = request.POST['manager_email']
      manager_schedule = request.POST['manager_schedule']
      manager_comment = request.POST['manager_comment']
      if manager:
        manager.name = manager_name
        manager.phone = manager_phone
        manager.email = manager_email
        manager.schedule = manager_schedule
        manager.comment = manager_comment
        manager.save()
      else:
        Manager(
          unique_supplier=unique_supplier, name=manager_name, phone=manager_phone, email=manager_email, schedule=manager_schedule, comment=manager_comment
        ).save()
    elif any('office_' in value for value in request.POST.keys()):
      if 'office_-1__city' in request.POST:
        id = '-metinvest'
        office = Office(supplier=unique_supplier)
      else:
        id = sorted(request.POST.keys())[-1].replace('office_', '').split('_')[0]
        office = Office.objects.get(id=int(id))

      if request.POST['office_{}__delete'.format(id)] == 'true':
        office.delete()
      else:
        office_city = request.POST['office_{}__city'.format(id)]
        office_name = request.POST['office_{}__name'.format(id)]
        office_address = request.POST['office_{}__address'.format(id)]
        office_phone = request.POST['office_{}__phone'.format(id)]
        office_email = request.POST['office_{}__email'.format(id)]
        office_schedule = request.POST['office_{}__schedule'.format(id)]
        office_comment = request.POST['office_{}__comment'.format(id)]

        office.city=office_city
        office.name=office_name
        office.address=office_address
        office.phone=office_phone
        office.email=office_email
        office.schedule=office_schedule
        office.comment=office_comment

        office.save()
    elif any('warehouse_' in value for value in request.POST.keys()):
      if 'warehouse_-1__city' in request.POST:
        id = '-metinvest'
        warehouse = Warehouse(supplier=unique_supplier)
      else:
        id = sorted(request.POST.keys())[-1].replace('warehouse_', '').split('_')[0]
        warehouse = Warehouse.objects.get(id=int(id))

      if request.POST['warehouse_{}__delete'.format(id)] == 'true':
        warehouse.delete()
      else:

        warehouse_city = request.POST['warehouse_{}__city'.format(id)]
        warehouse_name = request.POST['warehouse_{}__name'.format(id)]
        warehouse_address = request.POST['warehouse_{}__address'.format(id)]
        warehouse_phone = request.POST['warehouse_{}__phone'.format(id)]
        warehouse_email = request.POST['warehouse_{}__email'.format(id)]
        warehouse_schedule = request.POST['warehouse_{}__schedule'.format(id)]
        warehouse_comment = request.POST['warehouse_{}__comment'.format(id)]

        warehouse.city=warehouse_city
        warehouse.name=warehouse_name
        warehouse.address=warehouse_address
        warehouse.phone=warehouse_phone
        warehouse.email=warehouse_email
        warehouse.schedule=warehouse_schedule
        warehouse.comment=warehouse_comment

        warehouse.save()


  unique_supplier.rating = random.choice(range(101))

  if not manager:
    manager = Manager(unique_supplier=unique_supplier)

  context = {}
  context['supplier'] = unique_supplier
  context['manager'] = manager

  context['new_office'] = Office(id=-1, city='', name='', address='', phone='', email='', schedule='', comment='')
  context['offices'] = Office.objects.filter(supplier=unique_supplier).order_by('id')

  context['new_warehouse'] = Warehouse(id=-1, city='', name='', address='', phone='', email='', schedule='', comment='')
  context['warehouses'] = Warehouse.objects.filter(supplier=unique_supplier).order_by('id')

  return render(request, 'create_supplier.html', context)

def city(request, id):
  pass
