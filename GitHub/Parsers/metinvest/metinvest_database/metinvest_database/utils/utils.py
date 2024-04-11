SEARCH_SYMBOLS_MAP = {
  'e': 'е',
  't': 'т',
  'y': 'у',
  'o': 'о',
  'p': 'р',
  'a': 'а',
  'd': 'д',
  'h': 'н',
  'k': 'к',
  'x': 'х',
  'c': 'с',
  'b': 'в',
  'm': 'м',
  '0': 'о',
  ',': ' '
}

def replace_from_map(string, symbols_map):
  for symbol in symbols_map.keys():
    string = string.replace(symbol, symbols_map[symbol])
  return string

def prepare_for_search(string):
  if string:
    string = string.lower()
    string = replace_from_map(string, SEARCH_SYMBOLS_MAP)

  return string

def get_digits_formatted(value):
  return "{:,.0f}".format(value).replace(",", " ")

def remake_texts(isnull, offset, limit):
  from metinvest_database.shared_models import Product
  products = Product.objects.filter(product_full_text__isnull=isnull).order_by('id')
  total = products.count()

  i = 0
  for product in products[offset:limit]:
    i += 1
    if not i % 100:
      print('{} / {}'.format(i, total))

    product.make_full_text()
    product.save()


def create_cities():
  from metinvest_database.shared_models import City, UniqueCity
  for city in City.objects.order_by('name').all():
    if not UniqueCity.objects.filter(name=city.name):
      yn = input('{} - это город?'.format(city.name))
      if yn:
        unique_city = UniqueCity(name=city.name)
        unique_city.save()

#Оскол, Новгород, Воды, Челны
def fix_2_words_city_supplier(city_name):
  from metinvest_database.shared_models import City, SupplierCity, UniqueCity
  city = City.objects.get(name=city_name)

  suppliers_cities = SupplierCity.objects.filter(city=city)
  yn = input('{} вместо {}?'.format('{} {}'.format(suppliers_cities[0].supplier.name.split()[-1], city.name), city.name))
  new_city_chunk = suppliers_cities[0].supplier.name.split()[-1]

  old_city_name = city.name
  city.name = '{} {}'.format(new_city_chunk, city.name)
  print('{} исправлено на {}'.format(old_city_name, city.name))
  city.save()

  if not UniqueCity.objects.filter(name=city.name):
    UniqueCity(name=city.name).save()

  for supplier_city in suppliers_cities:
    old_supplier_name = supplier_city.supplier.name
    supplier_city.supplier.name = ' '.join(supplier_city.supplier.name.split(' ')[:-1])
    print('{} исправлено на {}'.format(old_supplier_name, supplier_city.supplier.name))
    supplier_city.supplier.save()



def make_jsons(limit):
  from metinvest_database.shared_models import Product

  i = 0
  products = Product.objects.filter(json_view__isnull=True)
  total = products.count()
  for product in products[:limit]:
    i += 1
    if not i % 100:
      print('{} / {}'.format(i, total))
    product.json_view = product.to_json()
    product.save()


def make_city_mappings():
  from metinvest_database.shared_models import City, UniqueCity, MappingCity

  for city in City.objects.filter(not_a_city__isnull=True).order_by('name').all():
    is_city = input('==={}=== это город?'.format(city.name))
    if is_city:
      unique_city = UniqueCity(name=city.name)
      unique_city.save()

      city.not_a_city = False
      city.code=city.name
      city.save()

def make_city_mappings_with_bracket():
  from metinvest_database.shared_models import City, UniqueCity, MappingCity

  for city in City.objects.filter(not_a_city__isnull=True).order_by('name').all():
    if '(' in city.name:
      name = city.name.split('(')[0].strip()
      if not UniqueCity.objects.filter(name=name):
        unique_city = UniqueCity(name=name)
        unique_city.save()

      city.not_a_city = True
      city.code=name
      city.save()

def try_to_mapping_shorted_names():
  from metinvest_database.shared_models import City, UniqueCity, MappingCity

  for city in City.objects.filter(not_a_city__isnull=True).order_by('name').all():
    unique_cities = UniqueCity.objects.filter(name__startswith=city.name[0])
    ok_cities = []

    for unique_city in unique_cities:

      ok = True
      last_index = 0
      for i in range(1, len(city.name[1:])):
        if city.name[i] in unique_city.name and unique_city.name.index(city.name[i]) > last_index:
          last_index = unique_city.name.index(city.name[i])
        else:
          ok = False
          break
      if ok:
        ok_cities.append(unique_city.name)

    if len(ok_cities) == 1:
      input('{} -> {}'.format(city.name, ok_cities[0]))
      city.code = ok_cities[0]
      city.not_a_city = True
      city.save()

CITIES_MAPPING = {
  'Балак': 'Балаково',
  'Березовск': 'Березовский',
  'Благ': 'Благовещенск',
  'ВВол': 'Вышний Волочек',
  'Воды': 'Минеральные Воды',
  'Минводы': 'Минеральные Воды',
  'Мск': 'Москва',
  'Ннов': 'Нижний Новгород',
  'ННов': 'Нижний Новгород',
  'Н. Новгород': 'Нижний Новгород',
  'Н.Таг': 'Нижний Тагил',
  'НЧел': 'Набережные Челны',
  'Орен': 'Оренбург',
  'Оскол': 'Старый Оскол',
  'П-Камч': 'Петропавловск-Камчатский',
  'Под': 'Подольск',
  'Сарат': 'Саратов',
  'Спб': 'Санкт-Петербург',
  'Тагил': 'Нижний Тагил',
  'Усс': 'Уссурийск',
  'УУдэ': 'Улан-Удэ',
  'У-Удэ': 'Улан-Удэ',

  'Алекс': 'Александров',
  'Брк': 'Брянск',
  'Бтк': 'Батайск',
  'Ввк': 'Владивосток',
  'Вга': 'Вологда',
  'Вгд': 'Волгоград',
  'Волж': 'Волжский',
  'Жук': 'Жуковский',
  'И': 'Большой Исток',
  'Иван': 'Иваново',
  'Ивка': 'Ивантеевка',
  'Иж': 'Ижевск',
  'Кдр': 'Краснодар',
  'Кир': 'Киров',
  'Кмр': 'Кемерово',
  'Крк': 'Курск',
  'Крсн': 'Красноярск',
  'Кург': 'Курган',
  'Нвм': 'Невинномысск',
  'Нмск': 'Новомосковск',
  'Нчб': 'Новочебоксарск',
  'Нчк' : 'Новочебоксарск',
  'Одв' : 'Одинцово',
  'Окт' : 'Люберцы',
  'Орл' : 'Орел',
  'Перв' : 'Первоуральск',
  'Прм' : 'Пермь',
  'Птк' : 'Пятигорск',
  'Пшк' : 'Пушкин',
  'Скр' : 'Сыктывкар',
  'Смр' : 'Самара',
  'Срк' : 'Саранск',
  'Стл' : 'Ставрополь',
  'Нкрс': 'Некрасовский'
}

def map_cities_by_dict():
  from metinvest_database.shared_models import City

  for key in CITIES_MAPPING.keys():
    for city in City.objects.filter(name=key):
      city.code = CITIES_MAPPING[key]
      city.not_a_city = True
      city.save()

def map_by_product():
  from metinvest_database.shared_models import City, Product

  for city in City.objects.filter(not_a_city__isnull=True).order_by('name').all():
    print('city is =={}=='.format(city.name))
    print('Parsers1 is {}'.format(city.parser.name))
    product = Product.objects.filter(supplier_city__city=city)[0]
    print('product is {}'.format('{} {} {}'.format(product.id, product.category, product.name)))
    input()

def time_to_parsed(parser):
  from metinvest_database.shared_models import Product

  products = Product.objects.filter(parser__code=parser)
  i = 0
  total = products.count()

  for product in products:
    i += 1
    if not i % 100:
      print('{}/{}'.format(i, total))
    #FIXME это только mmk
    product.parsed = product.data['Время']
    del product.data['Время']
    product.make_full_text()
    product.make_hash()
    product.json_view = product.to_json()
    product.save()

