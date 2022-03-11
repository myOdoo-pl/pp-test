# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2009 CamptoCamp. All rights reserved.
#    @author Nicolas Bessi
#
#    Abstract class to fetch rates from National Bank of Poland
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from .currency_getter_interface import Currency_getter_interface

from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)


class PL_NBP_getter(Currency_getter_interface):
    """Implementation of Currency_getter_factory interface
    for PL NBP service

    """

    def rate_retrive(self, data, curr):
        """recive rate from completed dict that contains rates and dates from table A,B """
        # Information about dates from rating can be usefull for future modification
        # However dict is so small it doesnt affect calculation process
        for currence in data:
            if curr in currence.values():
                res = currence['mid']
        return res

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days):
        """implementation of abstract method of Curreny_getter_interface"""
        """it takes currency array as list of avaiable currencies, currency that
        user want to check, and ma_delta_days to validate currency rate date """

        if main_currency in currency_array:
            currency_array.remove(main_currency)

        _logger.debug("NBP.pl currency rate service : connecting...")

        # Url and dictionary for rates
        url = 'http://api.nbp.pl/api/exchangerates/tables/'
        raw_dictionary = self.get_url(url)

        _logger.debug("NBP.pl sent a valid JSON file")

        # Data check
        rate_date = raw_dictionary['dates'][0]
        rate_date_datetime = datetime.strptime(rate_date, DEFAULT_SERVER_DATE_FORMAT)
        self.check_rate_date(rate_date_datetime, max_delta_days)

        self.supported_currency_array = [x['code'] for x in raw_dictionary['rates']]
        self.supported_currency_array.append('PLN')

        _logger.debug("Supported currencies = %s" % self.supported_currency_array)

        self.validate_cur(main_currency)

        if main_currency != 'PLN':
            main_rate = self.rate_retrive(raw_dictionary['rates'], main_currency)

        for curr in currency_array:
            self.validate_cur(curr)
            if curr == 'PLN':
                rate = main_rate
            else:
                curr_data = self.rate_retrive(raw_dictionary['rates'], curr)
                if main_currency == 'PLN':
                    rate =  1 / curr_data
                else:
                    rate = main_rate * curr_data

            self.updated_currency[curr] = rate
            _logger.debug("Rate retrieved : %s = %s %s" % (main_currency, rate, curr))
        return self.updated_currency, self.log_info
