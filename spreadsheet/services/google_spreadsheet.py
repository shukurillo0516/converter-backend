from locale import currency
import os
import datetime
from decimal import Decimal

import gspread
import requests

from django.conf import settings
from spreadsheet.models import Row, Order, CurrencyTracker
from django.utils import timezone


BASE_DIR = settings.BASE_DIR


def get_current_date():
    now = timezone.now()
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
        update_end_row = self.row.update_end_row
        end_row = self.row.end_row
        if update_end_row > end_row:
            self.row.update_end_row = end_row
            self.row.save()
            update_end_row = end_row

        for row_number in range(update_end_row):
            row_values = self.values[row_number]
            row_number += 1

            if row_values != ['№', 'заказ №', 'стоимость,$', 'срок поставки']:
                try:
                    order = Order.objects.get(row_number=row_number)
                    changed = False
                    delivery_time = russian_date_to_english(row_values[3])
                    price_ruble = self.dollar_rate * \
                        Decimal(
                            row_values[2]) if row_values[2] and self.dollar_rate else 0

                    if order.number != row_values[0]:
                        order.number = row_values[0]
                        changed = True
                    if order.order_number != row_values[1]:
                        order.order_number = row_values[1]
                        changed = True
                    if order.price_dollar != row_values[2]:
                        order.price_dollar = row_values[2]
                        changed = True
                    if order.price_ruble != price_ruble:
                        order.price_ruble = price_ruble
                        changed = True
                    if order.delivery_time != delivery_time:
                        order.delivery_time = delivery_time
                        changed = True

                    if changed:
                        order.save()
                except Exception as e:
                    print(e.args, "check_and_update_rows")
        if end_row != update_end_row:
            self.row.update_end_row = end_row
            self.row.save()

    def main_handler(self):
        try:
            usd = CurrencyTracker.objects.get(currency_code="usd")
            if usd.updated_at + datetime.timedelta(hours=12) < timezone.now():
                usd.currency_val_in_ruble = get_dollar_rate()
                usd.save()
            self.dollar_rate = usd.currency_val_in_ruble

        except CurrencyTracker.DoesNotExist:
            dollar_rate = get_dollar_rate()
            usd = CurrencyTracker(
                currency_code="usd",
                currency_val_in_ruble=dollar_rate
            )
            usd.save()
            self.dollar_rate = dollar_rate

        self.values = self.get_values()
        self.rows_length = len(self.values)
        self.delete_or_add_rows()
        self.check_and_update_rows()
