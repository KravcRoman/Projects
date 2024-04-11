import xlrd

from metinvest_database.uploader_mock import TemporaryPreProduct

def get_caption_row(sheet):
  i = 0
  captions_finded = False
  while not captions_finded:
    for col in sheet.row(i):
      if col.value == 'Цена':
        captions_finded = True
        break
    if not captions_finded:
      i += 1
  return i

def parse_file(filename, parser):
  excel = xlrd.open_workbook(filename)

  sheet_names = excel.sheet_names()
  for name in sheet_names:
    sheet = excel.sheet_by_name(name)

    captions_row = get_caption_row(sheet)
    captions = [col.value for col in sheet.row(7)]

    for row_n in range(captions_row + 1, sheet.nrows):
      if not row_n % 100:
        print('{} / {}'.format(row_n, sheet.nrows))
      data = {}
      for caption in captions:
        if caption != 42:
          data[caption] = sheet.row(row_n)[captions.index(caption)].value
      TemporaryPreProduct(parser=parser.name, data=data).save()