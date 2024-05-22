from django.http import JsonResponse, Http404
from .models import Exchange_Rate
from django.shortcuts import get_object_or_404

def rate(request):
    charcode = request.GET.get('charcode')
    date = request.GET.get('date')
    try:
        exchange_rate = Exchange_Rate.objects.get(charcode=charcode, date=date)
        response_data = {
            "charcode": exchange_rate.charcode,
            "date": str(exchange_rate.date),
            "rate": exchange_rate.rate
        }
        return JsonResponse(response_data)
    except Exchange_Rate.DoesNotExist:
        raise Http404("Для указанной даты такой курс валюты не найден")

