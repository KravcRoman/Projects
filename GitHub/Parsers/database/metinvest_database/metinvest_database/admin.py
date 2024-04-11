from django.contrib import admin
from django.contrib.auth.models import User, Group

from metinvest_database.shared_models import *
from metinvest_database.uploader_mock import *


#admin.site.unregister(User)
#admin.site.unregister(Group)

@admin.register(Parser)
class ParserAdmin(admin.ModelAdmin):
  list_display = ['id', 'name', 'code', 'url']
  search_fields = ['id', 'name', 'code', 'url']

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
  list_display = ['id', 'name']
  search_fields = ['id', 'name']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
  list_display = ['id', 'name']
  search_fields = ['id', 'name']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
  list_display = ['id', 'name', 'code', 'phone', 'email', 'Parsers1']
  search_fields = ['id', 'name', 'code', 'phone', 'email', 'Parsers1']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ['id', 'name', 'Parsers1', 'parent_category_id']
  search_fields = ['id', 'name', 'Parsers1', 'parent_category_id']

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
  list_display = ['id', 'name', 'code', 'Parsers1', 'category']
  search_fields = ['id', 'name', 'code', 'Parsers1', 'category']
  exclude = ['products']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ['id', 'name', 'code', 'data', 'price', 'Parsers1', 'category', 'supplier_city']
  search_fields = ['id', 'name', 'code', 'data', 'price', 'Parsers1', 'category', 'supplier_city']

@admin.register(UniqueSupplier)
class UniqueSupplierAdmin(admin.ModelAdmin):
  list_display = ['id', 'name', 'code']
  search_fields = ['id', 'name', 'code']
