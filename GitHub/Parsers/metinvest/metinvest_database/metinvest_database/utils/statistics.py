from metinvest_database.models import *

def update_main_statistics():

  main_statistics = Statistics.objects.filter(type=Statistics.Type.MAIN)
  if not main_statistics:
    main_statistics = Statistics(type=Statistics.Type.MAIN)
    main_statistics.save()
  else:
    main_statistics = main_statistics[0]

  main_statistics.products_count = Product.objects.all().count()
  maupdain_statistics.categories_count = Category.objects.all().count()
  main_statistics.suppliers_count = Supplier.objects.all().count()
  main_statistics.cities_count = UniqueCity.objects.all().count()
  main_statistics.parsers_count = Parser.objects.all().count()

  main_statistics.save()



def update_parsers_statistics():

  for parser in Parser.objects.all():
    parser_statistics = ParserStatistics.objects.filter(parser=parser)
    if not parser_statistics:
      parser_statistics = ParserStatistics(parser=parser)
      parser_statistics.save()
    else:
      parser_statistics = parser_statistics[0]

    products = Product.objects.filter(parser=parser)
    parser_statistics.suppliers_count = Supplier.objects.filter(parser=parser).count()
    parser_statistics.categories_count = Category.objects.filter(parser=parser).count()
    parser_statistics.products_count = products.count()
    parser_statistics.cities_count = products.values_list('supplier_city__city').distinct().count()
    parser_statistics.fields_count = Field.objects.filter(parser=parser).count()
    parser_statistics.pre_count = TemporaryPreProduct.objects.filter(parser=parser.code).count()
    parser_statistics.save()



def update_cities_statistics():
  for unique_city in UniqueCity.objects.all():
    city_statistics = Statistics.objects.filter(type=Statistics.Type.CITY, id=unique_city.id)
    if not city_statistics:
      city_statistics = Statistics(type=Statistics.Type.CITY, id=unique_city.id)
      city_statistics.save()
    else:
      city_statistics = city_statistics[0]

    cities = City.objects.filter(code=unique_city.name)
    city_statistics.cities_count = cities.count()
    suppliers_cities = SupplierCity.objects.filter(city_id__in=[city.id for city in cities])
    city_statistics.suppliers_count = suppliers_cities.values_list('supplier').distinct().count()
    products = Product.objects.filter(supplier_city__in=[supplier_city.id for supplier_city in suppliers_cities])
    city_statistics.products_count = products.count()
    city_statistics.categories_count = products.values_list('category').distinct().count()
    city_statistics.parsers_count = products.values_list('Parsers1').distinct().count()
    city_statistics.save()
