from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from spreadsheet.services.google_spreadsheet import GoogleSpreadsheet
from spreadsheet.models import Row


class SpreadsheetDataViewset(viewsets.ViewSet):
    queryset = Row.objects.all()

    @action(detail=False)
    def test(self, request, *args, **kwargs):
        google_sheet = GoogleSpreadsheet()
        google_sheet.main_handler()

        return Response({200: 200})
