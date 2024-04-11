from metinvest_database.shared_models import *

def create_unique_suppliers():
  prev = []
  for supplier in Supplier.objects.all().order_by('name'):
    if not prev:
      prev = supplier.name

    intersection = [w for w in supplier.name.lower().split() if w in prev.lower().split()]
    if intersection:
      supplier_name = ' '.join(sorted([w for w in supplier.name.split() if w in prev.split()]))
      if not UniqueSupplier.objects.filter(name=supplier_name):
        UniqueSupplier(name=supplier_name, code=supplier.name).save()
    else:
      prev = supplier.name
