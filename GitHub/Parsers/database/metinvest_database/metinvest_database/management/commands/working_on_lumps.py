import csv

from django.core.management.base import BaseCommand

from metinvest_database.csv_views import get_raw
from metinvest_database.settings import STATICFILES_DIRS
from metinvest_database.shared_models import *
from metinvest_database.uploader_mock import TemporaryProduct, get_all_fields


CSV_FILES_DIR = '{}/csv/'.format(STATICFILES_DIRS[0])

def delete_old_lumps(parser_code):
    prev_created_at = None
    for pallet in TemporaryProduct.objects.filter(parser=parser_code).order_by('-created_at'):
      if not prev_created_at:
        prev_created_at = pallet.created_at
        continue

      if (prev_created_at - pallet.created_at).seconds > 3600 * 3:
        break
      else:
        prev_created_at = pallet.created_at

    TemporaryProduct.objects.filter(parser=parser_code, created_at__lt=prev_created_at).delete()

def get_big_csv(parser_code):
  fields = Field.objects.filter(parser=Parser.objects.get(code=parser_code)).order_by('name')

  f = open('{}{}.csv'.format(CSV_FILES_DIR, parser_code), 'w')
  writer = csv.writer(f, delimiter=';')

  writer.writerow([field.name for field in fields])

  null = None
  for temporary_product in TemporaryProduct.objects.filter(parser=parser_code):
    data = eval(temporary_product.data)

    for pre in data:
      writer.writerow(get_raw(fields, pre))

  f.close()

def encode_big_csv(parser_code):

  f1 = open('{}{}.csv'.format(CSV_FILES_DIR, parser_code), 'r')
  f2 = open('{}{}_windows.csv'.format(CSV_FILES_DIR, parser_code), 'w', encoding='windows-1251')

  mapping = {}
  for line in f1:

    writed_ok = False
    while not writed_ok:
      if mapping:
        for key, value in mapping.items():
          line = line.replace(key, value)

      try:
        f2.write(line)
        writed_ok = True
      except UnicodeEncodeError as error:
        unknown_symbol = str(error).split("codec can't encode character '")[-1].split("'")[0]

        if not ErrorEncodingSymbol.objects.filter(utf_value=unknown_symbol, replace_with_value='?'):
          print(unknown_symbol)
          ErrorEncodingSymbol(utf_value=unknown_symbol, replace_with_value='?').save()
        decoded_symbol = bytes(unknown_symbol, 'utf-8').decode('unicode_escape')
        mapping[decoded_symbol] = '?'

  f1.close()
  f2.close()


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
      if not TemporaryProduct.objects.filter(maked=False):
        return

      for distinct_parser_data in TemporaryProduct.objects.all().values('Parsers1').distinct().order_by('Parsers1'):
        parser_code = distinct_parser_data['Parsers1']

        delete_old_lumps(parser_code)

        if not Parser.objects.filter(code=parser_code):
          Parser(name=parser_code, code=parser_code).save()
          get_all_fields(parser_code)

        get_big_csv(parser_code)
        encode_big_csv(parser_code)


