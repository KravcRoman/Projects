import csv, datetime
from itertools import chain
from functools import reduce

from django.http import StreamingHttpResponse

from metinvest_database.shared_models import *
from metinvest_database.uploader_mock import *

def get_raw(fields, temporary_pre_product):
  result = []
  for field in fields:
    result.append(temporary_pre_product.get(field.name, ''))
  return result

def get_raw_product(fields, temporary_product):
  null = None
  data = eval(temporary_product.data)

  result = []
  for pre in data:
    result.append(get_raw(fields, pre))

  return result

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def get_csv(request):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    parser_code = request.GET['parser_code']
    type = request.GET['type']

    fields = Field.objects.filter(parser=Parser.objects.get(code=parser_code)).order_by('name')

    rows = (temporary_product for temporary_product in reduce(lambda a, b: a + b, [
      get_raw_product(fields, temporary_product) for temporary_product in TemporaryProduct.objects.filter(parser=parser_code)
    ]))

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')
    return StreamingHttpResponse(
        (writer.writerow(row) for row in chain([[field.name for field in fields]], rows)),
        content_type='text/csv; charset=windows-1251',
        headers={"Content-Disposition": 'attachment; filename="{}_{}_{}.csv"'.format(parser_code, type, datetime.date.today())},
    )