from statistics import mode
from tabnanny import verbose
from django.db import models
from core.models import TimestampedModel


class Row(TimestampedModel):
    row_id = models.PositiveIntegerField(default=1)
    update_end_row = models.PositiveIntegerField(default=0)
    end_row = models.PositiveIntegerField(default=0)


class Order(TimestampedModel):
    row_number = models.PositiveIntegerField(blank=True, null=True)
    number = models.IntegerField(verbose_name="№", blank=True, null=True)
    order_number = models.CharField(
        verbose_name="заказ №", max_length=255, blank=True, null=True)
    price_dollar = models.DecimalField(
        verbose_name="стоимость,$", max_digits=20, decimal_places=2, blank=True, null=True)
    price_ruble = models.DecimalField(
        verbose_name="стоимость,₽", max_digits=20, decimal_places=2, blank=True, null=True)
    delivery_time = models.DateField(
        verbose_name="срок поставки", blank=True, null=True)

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"
