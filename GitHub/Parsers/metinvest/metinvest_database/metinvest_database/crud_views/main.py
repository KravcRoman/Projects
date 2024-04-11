NAME = 'name'
CODE = 'code'
URL = 'url'
PHONE = 'phone'
EMAIL = 'email'
DATA = 'data'
PRICE = 'price'

PARSER_CODE = 'parser_code'
CATEGORY_CODE = 'category_code'
SUPPLIER_CODE = 'supplier_code'
CITY_CODE = 'city_code'

def get_body_or_error(request):
  if request.body:
    return request.body

  # FIXME
  raise Exception('No request body')

def subtract_cities_codes(subtract_from_codes, subtract_this):
  return [city_code for city_code in subtract_from_codes if city_code not in subtract_this]