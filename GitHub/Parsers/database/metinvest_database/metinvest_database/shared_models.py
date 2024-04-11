import hashlib

from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.auth.models import User
from django.db.models import DO_NOTHING, CASCADE

from metinvest_database.constants import *



class Parser(models.Model):
  class Meta:
    verbose_name = 'Парсер'
    verbose_name_plural = 'Парсеры'


  name = models.CharField(max_length=255, verbose_name="Название", unique=True)
  code = models.CharField(max_length=255, verbose_name="Внутренний код", unique=True, null=True, blank=True)
  url = models.CharField(max_length=255, verbose_name="URL", null=True)

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  def __str__(self):
    return self.name



class Region(models.Model):
  class Meta:
    verbose_name = 'Регион'
    verbose_name_plural = 'Регионы'

  name = models.CharField(max_length=255, verbose_name="Название", unique=True)

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  def __str__(self):
    return self.name



class UniqueCity(models.Model):
  class Meta:
    verbose_name = 'Город'
    verbose_name_plural = 'Города'

  name = models.CharField(max_length=255, verbose_name="Название")
  region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, verbose_name="Регион", null=True)

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  def __str__(self):
    return self.name



class City(models.Model):
  class Meta:
    verbose_name = 'Город (парсера)'
    verbose_name_plural = 'Города (парсеров)'

  parser = models.ForeignKey(Parser, on_delete=models.DO_NOTHING, verbose_name="Парсер", null=True)
  unique_city = models.ForeignKey(UniqueCity, on_delete=models.DO_NOTHING, verbose_name="Город", null=True)

  name = models.CharField(max_length=255, verbose_name="Название")
  code = models.CharField(max_length=255, verbose_name="Внутренний код", null=True, blank=True)

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  def __str__(self):
    return self.name

  # full_text = models.TextField(null=True)
  #
  # def make_full_text(self):
  #   self.full_text = '{}'.format(prepare_for_search(self.name))



class Supplier(models.Model):
  class Meta:
    verbose_name = 'Поставщик (парсера)'
    verbose_name_plural = 'Поставщики (парсеров)'

  parser = models.ForeignKey(Parser, on_delete=models.DO_NOTHING, verbose_name="Парсер", null=True)

  name = models.CharField(max_length=255, verbose_name="Название")
  code = models.CharField(max_length=255, verbose_name="Внутренний код", null=True, blank=True)
  phone = models.CharField(max_length=255, verbose_name="Телефон", null=True)
  email = models.CharField(max_length=255, verbose_name="Email", null=True)

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  def __str__(self):
    return self.name

  # full_text = models.TextField(null=True)
  #
  # def make_full_text(self):
  #   self.full_text = '{}'.format(prepare_for_search(self.name))



class SupplierCity(models.Model):
  class Meta:
    verbose_name = 'Филиал поставщика'
    verbose_name_plural = 'Филиалы поставщиков'

  supplier = models.ForeignKey(Supplier, on_delete=models.DO_NOTHING, verbose_name="Поставщик")
  city = models.ForeignKey(City, on_delete=models.DO_NOTHING, verbose_name="Город")

  def __str__(self):
    return '{} ({})'.format(self.supplier.name, self.city.name)












class Category(models.Model):
  class Meta:
    verbose_name = 'Категория'
    verbose_name_plural = 'Категории'

  parser = models.ForeignKey(Parser, on_delete=models.DO_NOTHING, verbose_name="Парсер", null=True)
  parent_category_id = models.IntegerField(null=True, verbose_name="Идентификатор надкатегории")

  name = models.CharField(max_length=255, verbose_name="Название")
  json_view = models.JSONField(null=True, blank=True)

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  def to_json(self):
    return {
      PARSER: self.parser.name,
      NAME: self.name
    }

  # full_text = models.TextField(null=True)
  #
  # def make_full_text(self):
  #   self.full_text = '{}'.format(prepare_for_search(self.name))


  def __str__(self):
    return self.name


class Field(models.Model):
  class Meta:
    verbose_name = 'Поле'
    verbose_name_plural = 'Поля'
    unique_together = (['Parsers1', 'code'])

  parser = models.ForeignKey(Parser, on_delete=models.DO_NOTHING, verbose_name="Парсер", null=True)
  category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, verbose_name="Категория", null=True)

  name = models.CharField(max_length=255, verbose_name="Название")
  code = models.CharField(max_length=255, verbose_name="Внутренний код", null=True, blank=True)

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  # full_text = models.TextField(null=True)
  #
  # def make_full_text(self):
  #   self.full_text = '{}'.format(prepare_for_search(self.name))

  def __str__(self):
    return self.name



from metinvest_database.utils.utils import prepare_for_search

class Product(models.Model):
  class Meta:
    verbose_name = 'Товар'
    verbose_name_plural = 'Товары'

    indexes = [GinIndex(fields=['search_vector']), GinIndex(fields=['product_full_text'])]


  parser = models.ForeignKey(Parser, on_delete=models.DO_NOTHING, verbose_name="Парсер", null=True)
  category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, verbose_name="Категория", null=True)
  supplier_city = models.ForeignKey(SupplierCity, on_delete=models.DO_NOTHING, verbose_name="Филиал поставщика", null=True)

  name = models.CharField(max_length=255, verbose_name="Название")
  code = models.CharField(max_length=255, verbose_name="Внутренний код", null=True, blank=True)
  data = models.JSONField(verbose_name="Данные")
  price = models.CharField(max_length=255, verbose_name="Цена")

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")
  parsed = models.DateTimeField(null=True, verbose_name="Последний парсинг")

  product_full_text = models.TextField(null=True, db_index=True)
  changed = models.BooleanField(default=False, null=True)
  json_view = models.JSONField(null=True, blank=True)

  search_vector = SearchVectorField(null=True)

  hash_without_price = models.CharField(max_length=65, verbose_name="Хэш без цены", null=True, db_index=True)
  hash_with_price = models.CharField(max_length=65, verbose_name="Хэш с ценой", null=True, db_index=True)

  def __str__(self):
    return self.name

  def to_json(self):
    return {
      NAME: self.name,
      "html": self.name,
      PARSER: self.parser.name,
      CATEGORY: {"id": self.category.id, NAME: self.category.name, "Parsers1": self.category.parser.name},
      CITY: self.supplier_city.city.code,
      SUPPLIER: {"id": self.supplier_city.supplier.id, NAME: self.supplier_city.supplier.name, "Parsers1": self.supplier_city.supplier.parser.name},
      DATA: self.data,
      PRICE: self.price,
      #FIXME
      #"updated": self.parsed.strftime("%Y-%m-%d %H:%M:%S")
      "updated": self.parsed
    }

  def make_full_text(self):
    self.product_full_text = '{} {} {} {} {} {}'.format(prepare_for_search(self.category.name),
                                               prepare_for_search(self.supplier_city.supplier.name),
                                               prepare_for_search(self.supplier_city.city.code),
                                               prepare_for_search(self.name),
                                               prepare_for_search(' '.join([value for value in self.data.values() if value])),
                                               prepare_for_search(self.category.parser.name))

  def make_hash(self):
    without_price = '{} {} {} {} {} {}'.format(self.category.name, self.supplier_city.supplier.name, self.supplier_city.city.name,
                                               self.name, str(sorted(self.data.items())), self.category.parser.name)
    with_price = '{} {}'.format(without_price, self.price)
    self.hash_without_price = hashlib.sha256(without_price.encode()).hexdigest()
    self.hash_with_price = hashlib.sha256(with_price.encode()).hexdigest()



class ErrorEncodingSymbol(models.Model):
  class Meta:
    verbose_name = 'Непереводимый символ'
    verbose_name_plural = 'Непереводимые символы'

  utf_value = models.CharField(max_length=255, verbose_name="Оригинал")
  replace_with_value = models.CharField(max_length=255, verbose_name="Замена")

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")




class MetinvestManager(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь системы")
  name = models.CharField(max_length=255, null=True, blank=True, verbose_name="ФИО")
  phone = models.CharField(max_length=255, null=True, blank=True, verbose_name="Телефон")
  email = models.CharField(max_length=255, null=True, blank=True, verbose_name="Email")



class RatingScoreRecord(models.Model):
  class Meta:
    verbose_name = 'Оценка рейтинга'
    verbose_name_plural = 'Оценки рейтингов'

  user = models.ForeignKey(MetinvestManager, on_delete=DO_NOTHING, verbose_name="Оценивший менеджер")


class UniqueSupplier(models.Model):
  class Meta:
    verbose_name = 'Поставщик'
    verbose_name_plural = 'Поставщики'

  name = models.CharField(max_length=255, verbose_name="Название")
  code = models.CharField(max_length=255, verbose_name="Код")

  comment = models.TextField(null=True, blank=True)
  rating = models.IntegerField(null=True, blank=True)

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  def __str__(self):
    return self.name

class Manager(models.Model):
  class Meta:
    verbose_name = 'Поставщик'
    verbose_name_plural = 'Поставщики'

  unique_supplier = models.ForeignKey(UniqueSupplier, on_delete=CASCADE, verbose_name="Поставщик")
  name = models.CharField(max_length=255, null=True, blank=True, verbose_name="ФИО")
  phone = models.CharField(max_length=255, null=True, blank=True, verbose_name="Телефон")
  email = models.CharField(max_length=255, null=True, blank=True, verbose_name="Email")
  schedule = models.CharField(max_length=255, null=True, blank=True, verbose_name="График работы")
  comment = models.TextField(null=True, blank=True, verbose_name="Комментарий")


class Office(models.Model):
  class Meta:
    verbose_name = 'Офис'
    verbose_name_plural = 'Офисы'

  supplier = models.ForeignKey(UniqueSupplier, on_delete=models.DO_NOTHING, verbose_name="Поставщик", null=True)
  city = models.CharField(max_length=255, verbose_name="Город", blank=True, null=True)

  name = models.CharField(max_length=255, verbose_name="Название", blank=True, null=True)
  address = models.CharField(max_length=255, verbose_name="Адрес", blank=True, null=True)
  phone = models.CharField(max_length=255, verbose_name="Телефон", blank=True, null=True)
  email = models.CharField(max_length=255, verbose_name="Email", blank=True, null=True)
  schedule = models.TextField()
  comment = models.TextField()

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  def __str__(self):
    return self.name



class Warehouse(models.Model):
  class Meta:
    verbose_name = 'Склад'
    verbose_name_plural = 'Склады'

  supplier = models.ForeignKey(UniqueSupplier, on_delete=models.DO_NOTHING, verbose_name="Поставщик", null=True)
  city = models.CharField(max_length=255, verbose_name="Город", blank=True, null=True)

  name = models.CharField(max_length=255, verbose_name="Название", blank=True, null=True)
  address = models.CharField(max_length=255, verbose_name="Адрес", blank=True, null=True)
  phone = models.CharField(max_length=255, verbose_name="Телефон", blank=True, null=True)
  email = models.CharField(max_length=255, verbose_name="Email", blank=True, null=True)
  schedule = models.TextField()
  comment = models.TextField()

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  def __str__(self):
    return self.name


# class MergedCategory(models.Model):
#   class Meta:
#     verbose_name = 'МультиКатегория'
#     verbose_name_plural = 'МультиКатегории'
#
#   name = models.CharField(max_length=255, verbose_name="Название")
#
#   created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
#   updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")
#
#   def __str__(self):
#     return self.name
#
#
# class MergedProduct(models.Model):
#   class Meta:
#     verbose_name = 'МультиТовар'
#     verbose_name_plural = 'МультиТовары'
#
#   name = models.CharField(max_length=255, verbose_name="Название")
#
#   created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
#   updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")
#
#   def __str__(self):
#     return self.name
#
#
# class MappingCity(models.Model):
#   class Meta:
#     verbose_name = 'Маппинг города'
#     verbose_name_plural = 'Маппинги городов'
#
#   city_name = models.CharField(max_length=255, verbose_name="Название города")
#   code = models.CharField(max_length=255, verbose_name="Обозначение")
#
#   created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
#   updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")
