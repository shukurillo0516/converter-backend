from django.urls import path
from rest_framework import routers

from .views import SpreadsheetDataViewset


router = routers.DefaultRouter()
router.register(r"spreadsheet-data", SpreadsheetDataViewset)

urlpatterns = []

urlpatterns += router.urls
