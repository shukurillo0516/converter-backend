import os
import datetime
from decimal import Decimal

import gspread
import requests

from django.conf import settings
from spreadsheet.models import Row, Order


BASE_DIR = settings.BASE_DIR


def get_current_date():
    now = datetime.datetime.now()
    return now.strftime("%d/%m/%Y")


def get_dollar_rate(date=None):
    if date is None:
        date = get_current_date()
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date}"
    req = requests.get(url=url)
    data = req.text

    usd_index = data.find("USD")
    data = data[usd_index:]
    val_tag = data.find(r"<Value>") + len("<Value>")
    val_tag_end = data.find(r"</Value>")
    usd_course = data[val_tag:val_tag_end]
    if usd_course:
        usd_course = usd_course.replace(".", "").replace(",", ".")

    return Decimal(usd_course)


def russian_date_to_english(date):
    date = date.split(".")
    day = date[0] if len(date[0]) > 1 else f"0{date[0]}"
    month = date[1] if len(date[1]) > 1 else f"0{date[1]}"
    return f"{date[2]}-{month}-{day}"


class SpreadsheetDataRetrieverMixin:
    @staticmethod
    def get_values(filenname="/key.json", sheet_name="test_data", worksheet_index=0):
        filenname = f"{BASE_DIR}/spreadsheet/services/{filenname}"
        gc = gspread.service_account(filename=filenname)
        sh = gc.open(sheet_name)
        worksheet = sh.get_worksheet(worksheet_index)
        list_of_values = worksheet.get_all_values()
        return list_of_values


class GoogleSpreadsheet(SpreadsheetDataRetrieverMixin):
    def __init__(self):
        self.row, _ = Row.objects.get_or_create(row_id=1)
        self.values = None
        self.rows_length = None
        self.dollar_rate = None

    def delete_or_add_rows(self):
        end_row = self.row.end_row
        if end_row == self.rows_length:
            return None
        elif end_row > self.rows_length:
            for row_no in range(self.rows_length, end_row):
                row_no += 1
                order = Order.objects.get(row_number=row_no)
                order.delete()

            self.row.end_row = self.rows_length
            self.row.save()
        elif end_row < self.rows_length:
            # if new rows added, save them to db
            for row_no in range(end_row, self.rows_length):
                row_values = self.values[row_no]
                if row_values != ['№', 'заказ №', 'стоимость,$', 'срок поставки']:
                    delivery_time = russian_date_to_english(row_values[3])
                    price_ruble = self.dollar_rate * \
                        Decimal(
                            row_values[2]) if row_values[2] and self.dollar_rate else 0

                    order = Order(row_number=row_no+1,
                                  number=row_values[0],
                                  order_number=row_values[1],
                                  price_dollar=row_values[2],
                                  price_ruble=price_ruble,
                                  delivery_time=delivery_time
                                  )
                    order.save()

            self.row.end_row = self.rows_length
            self.row.save()

    def check_and_update_rows(self):
        for row_number, row in enumerate(self.rows):
            row_number += 2
            try:
                order = Order.objects.get(row_number=row_number)
            except Order.DoesNotExist:
                try:
                    delivery_time = russian_date_to_english(row[3])
                    order = Order(
                        row_number=row_number,
                        number=row[0],
                        order_number=row[1],
                        price_dollar=row[2],
                        delivery_time=delivery_time
                    )
                    order.save()
                except Exception as err:
                    print(err)

    def main_handler(self):
        self.dollar_rate = get_dollar_rate()
        self.values = self.get_values()
        self.rows_length = len(self.values)
        print(self.rows_length, "self.rows_length")
        self.delete_or_add_rows()
        pass
