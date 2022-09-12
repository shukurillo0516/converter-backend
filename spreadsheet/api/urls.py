from django.urls import path, include


app_name = 'spreadsheet'

urlpatterns = [
    path('v1/', include('spreadsheet.api.v1.urls')),
]
