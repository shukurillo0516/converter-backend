from django.urls import path
from rest_framework import routers

from .views import SpreadsheetDataViewSet


router = routers.DefaultRouter()
router.register(r"spreadsheet-data", SpreadsheetDataViewSet)

urlpatterns = []

urlpatterns += router.urls
