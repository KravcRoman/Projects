from metinvest_database.shared_models import City, SupplierCity

def fix_city_parser():
  for city in City.objects.all():
    supplier_city = SupplierCity.objects.filter(city=city)
    if supplier_city:
      city.parser = supplier_city[0].supplier.parser
      city.save()