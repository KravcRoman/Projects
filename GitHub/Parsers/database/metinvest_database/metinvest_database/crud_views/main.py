def get_body_or_error(request):
  if request.body:
    return request.body

  # FIXME
  raise Exception('No request body')

def subtract_cities_codes(subtract_from_codes, subtract_this):
  return [city_code for city_code in subtract_from_codes if city_code not in subtract_this]