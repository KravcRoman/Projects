from django.contrib import admin
from .models import Exchange_Rate

@admin.register(Exchange_Rate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['charcode', 'date', 'rate']

