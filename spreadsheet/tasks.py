import os

from celery import shared_task
from celery.utils.log import get_task_logger
from .services.google_spreadsheet import GoogleSpreadsheet
import datetime


logger = get_task_logger(__name__)


@shared_task
def get_orders_data():
    """
    This function is peridiocally  called by celery beat
    """
    google_sheet = GoogleSpreadsheet()
    google_sheet.main_handler()
