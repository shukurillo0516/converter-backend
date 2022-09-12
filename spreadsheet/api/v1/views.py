from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from spreadsheet.services.google_spreadsheet import GoogleSpreadsheet
from spreadsheet.models import Row, Order


class SpreadsheetDataViewSet(viewsets.ViewSet):
    queryset = Order.objects.all()

    @action(detail=False)
    def test(self, request, *args, **kwargs):
        google_sheet = GoogleSpreadsheet()
        google_sheet.main_handler()

        return Response({200: 200})

    def list(self, request, *args, **kwargs):
        data = Order.objects.all().order_by("row_number").values_list("number", "order_number",
                                                                      "price_dollar", "price_ruble", "delivery_time")
        return Response({"payload": data})
