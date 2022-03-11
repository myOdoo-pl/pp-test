# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import _
from openerp.exceptions import UserError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

QUARTER_MAP = {'1': 1, '2': 4, '3': 7, '4': 10}
REVERSE_QUARTER_MAP = {10: '4', 4: '2', 7: '3', 1: '1'}

import logging
l = logging.getLogger(__name__)


class data_to_period:

    @staticmethod
    def check_dates(records):
        if records.date_from.day != 1:
            raise UserError(
                _("In 'Date Start' field you must choose a first day of a month: 02/01/2016, 12/01/2016..."))
        elif records.date_from.year != records.date_to.year:
            raise UserError(
                _("The chosen dates must be within the same year!"))
        # date_from_dt = datetime.strptime(
        #     records.date_from, DEFAULT_SERVER_DATE_FORMAT)
        date_from_dt = records.date_from
        months = records.date_from.month == records.date_to.month and 1 or 3
        month_end = date_from_dt + relativedelta(months=+months) + relativedelta(days=-1)
        if records.date_to != month_end:
            raise UserError(
                _("The chosen date range must start at first day of a month and end at \
                last day of a month (either the same month or quarter!"))

    @staticmethod
    def set_date_to(records, months=1, quarter=None):
        for record in records:
            # TODO: CORRECT QUARTER GENERATION
            if quarter:
                record.date_from = datetime(year=record.date_from.year, month=QUARTER_MAP[quarter], day=1).date()
            if record.date_from:
                date_from_dt = records.date_from
                month_end = date_from_dt + relativedelta(months=+int(months)) + relativedelta(days=-1)
                record.date_to = month_end
