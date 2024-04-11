from metinvest_database.shared_models import *
from metinvest_database.uploader_mock import *

from django.db import models

class ParserStatistics(models.Model):
  class Meta:
    verbose_name = 'Статистика сайта'
    verbose_name_plural = 'Статистики сайтов'

  parser = models.ForeignKey(Parser, on_delete=models.DO_NOTHING, verbose_name="Парсер", null=True)

  suppliers_count = models.IntegerField(null=True, verbose_name="Количество поставщиков")
  categories_count = models.IntegerField(null=True, verbose_name="Количество категорий")
  products_count = models.IntegerField(null=True, verbose_name="Количество продуктов")
  cities_count = models.IntegerField(null=True, verbose_name="Количество городов")
  fields_count = models.IntegerField(null=True, verbose_name="Количество полей")
  pre_count = models.IntegerField(null=True, verbose_name="Количество сырых товаров")

  created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Создан")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

  def __str__(self):
    return self.name

class Statistics(models.Model):
  class Meta:
    verbose_name = 'Статистика'
    verbose_name_plural = 'Статистики'

  class Type(models.TextChoices):
    MAIN = 'MAIN', "Главная"
    CITY = 'CITY', "Город"

  type = models.CharField(
        max_length=16,
        choices=Type.choices,
        default=Type.MAIN,
        verbose_name="Тип"
  )

  foreign_id = models.IntegerField(null=True)
  products_count = models.IntegerField(null=True, verbose_name="Количество продуктов")
  categories_count = models.IntegerField(null=True, verbose_name="Количество категорий")
  suppliers_count = models.IntegerField(null=True, verbose_name="Количество поставщиков")
  cities_count = models.IntegerField(null=True, verbose_name="Количество городов")
  parsers_count = models.IntegerField(null=True, verbose_name="Количество сайтов")
