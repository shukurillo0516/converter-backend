from ast import Or
from re import A
from django.contrib import admin
from .models import Order, Row, CurrencyTracker


class OrderAdmin(admin.ModelAdmin):
    list_display = ('row_number', 'number', 'delivery_time', 'order_number')
    list_display_links = ('row_number', 'number',
                          'delivery_time', "order_number")


admin.site.register(Order, OrderAdmin)
admin.site.register(Row)
admin.site.register(CurrencyTracker)
