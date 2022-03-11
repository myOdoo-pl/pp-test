# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    Module hr_billing_freelance is copyrighted by
#    Mikołaj Dziurzyński and Grzegorz Grzelak of OpenGLOBE (www.openglobe.pl)
#    with the same rules as OpenObject and OpenERP platform
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError, ValidationError

from urllib.request import urlopen
import datetime
import time
import logging

from pprint import pprint

logger=logging.getLogger('OPENERP_cur_hist_update')
_logger = logging.getLogger(__name__)

class currency_history_update(models.TransientModel):
    _name = 'currency.history.update'
    _description = 'Updating currency rates for choosen days'

    currency_table = {
        'A': [ 'THB', 'USD', 'AUD',	'HKD', 'CAD', 'NZD', 'SGD', 'EUR', 'HUF', 'CHF', 'GBP', 'UAH', 'JPY', 'CZK', 'DKK',
               'ISK', 'NOK', 'SEK', 'HRK', 'RON', 'BGN', 'TRY',	'ILS', 'CLP', 'PHP', 'MXN', 'ZAR', 'BRL', 'MYR', 'RUB',
               'IDR', 'INR', 'KRW', 'CNY', 'XDR'],
       'B': [ 'AFN', 'MGA', 'PAB',	'ETB', 'VES', 'BOB', 'CRC', 'SVC', 'NIO', 'GMD', 'MKD', 'DZD', 'BHD', 'IQD', 'JOD',
               'KWD', 'LYD', 'RSD', 'TND', 'MAD', 'AED', 'STN',	'BSD', 'BBD', 'BZD', 'BND',	'FJD', 'GYD', 'JMD', 'LRD',
               'NAD', 'SRD', 'TTD',	'XCD', 'SBD', 'VND', 'AMD',	'CVE', 'AWG', 'BIF', 'XOF', 'XAF', 'XPF', 'DJF', 'GNF',
               'KMF', 'CDF', 'RWF', 'EGP', 'GIP', 'LBP', 'SSP', 'SDG', 'SYP', 'GHS', 'HTG', 'PYG', 'ANG', 'PGK', 'LAK',
               'MWK', 'ZMW', 'AOA', 'MMK', 'GEL', 'MDL', 'ALL', 'HNL', 'SLL', 'SZL', 'LSL', 'AZN', 'MZN', 'NGN', 'ERN',
               'TWD', 'TMT', 'MRU', 'TOP', 'MOP', 'ARS', 'DOP', 'COP', 'CUP', 'UYU', 'BWP', 'GTQ', 'IRR', 'YER', 'QAR',
               'OMR', 'SAR', 'KHR', 'BYN', 'LKR', 'MVR', 'MUR', 'NPR', 'PKR', 'SCR', 'PEN', 'KGS', 'TJS', 'UZS', 'KES',
               'SOS', 'TZS', 'UGX', 'BDT', 'WST', 'KZT','MNT','VUV', 'BAM']
    }

    def _two_weeks_back(self):
        """marker for calendar, defines default position """
        two_weeks_back_date = (datetime.datetime.now() - datetime.timedelta(days=14)).strftime('%Y-%m-%d')
        return two_weeks_back_date

    date = fields.Date('Date', help = "Date from which the rates will be updated. If there is no rating for choosen date, the rates will be updated from the last available date.", default=_two_weeks_back)
    force_update = fields.Boolean('Force Update', help = "Running the wizard with this field checked updates currency rates with overwriting already existing records for any of the given dates.")


    def get_currency_rate(self,url):
        """gets url with information about currency, table and date
        and returns rate and effectiveDate.
        If there is no response from server or url doesnt exist return False  """

        import requests
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'][0]['mid']
            rate_date = data['rates'][0]['effectiveDate']
            return rate, rate_date
        else:
            return False

    def get_currency_ids(self):
        """get list of currencies which user want to look closer"""
        # service_nr is the number assigned to NBP service
        # to obtain currency code --> curr_id.name
        currency_update_obj = self.env['currency.rate.update.service']
        service_id = self._context.get('active_id',False)
        if service_id:
            service = currency_update_obj.browse(service_id)
        currency_ids = service.currency_to_update
        # to obtain currency code --> curr_id.name
        return currency_ids

    def which_table(self, currency, reference_table):
        """ Checks both table for existance selected currencies if not found return UserError """
        if currency  in reference_table['A']:
            return 'A'
        elif currency in reference_table['B']:
            return 'B'
        else:
            raise UserError(_("One of selected currency cannot be found in table A or B"))




    def list_of_days(self, first_date, second_date, delta):
        """ Based on range created be current date and other return a list of dates
        that will be used to create url, delta is fo advanced users that want to
        increase time delta for rates """

        list_of_days = []
        first_date = datetime.datetime.strptime(first_date,"%Y%m%d")
        second_date = datetime.datetime.strptime(second_date,"%Y%m%d")
        if first_date > second_date:
            smaller = second_date
            diff = first_date - second_date
        elif second_date > first_date:
            diff = second_date - first_date
            smaller = first_date
        for i in range(diff.days + delta):
            day = smaller + datetime.timedelta(days=i)
            list_of_days.append(day)
        return list_of_days

    def delete_weekenddays(self, list_of_days):
        """ delete from list of days saturday and sunday because npb is closed """
        # insert in datetime.datetime isoformat
        week_days = []
        for date in list_of_days:
            if datetime.datetime.weekday(date) < 5:
                week_days.append(date)
        return week_days

    
    def currency_history_update(self, *args):

        currency_rate_obj = self.env['res.currency.rate']
        wizard = self
        start_date = wizard.date.strftime("%Y%m%d")
        logger.warn("Downloading currency rate since {0}...".format(wizard.date))
        start_time = time.time()
        currency_update_obj = self.env['currency.rate.update.service']
        service_id = self._context.get('active_id',False)

        if service_id:
            service = currency_update_obj.browse(service_id)
            if service.service != 'PL_NBP_getter':
                raise UserError(_("Updating currency history works only for National Bank of Poland webservice."))

        company_id = service.company_id and service.company_id.id or False
        my_date_now = datetime.datetime.now().strftime('%Y%m%d')
        list_of_days = self.list_of_days(my_date_now, start_date, delta = 1)
        list_of_weekdays = self.delete_weekenddays(list_of_days)
        currency_ids = self.get_currency_ids()

        #iterating through list of week days
        for date_for_update in list_of_weekdays:

            #iterating through currencies
            for curr_id in currency_ids:

                # just in case that user wanted to get history of PLN
                if curr_id.name == "PLN":
                    continue

                # Give me number of table or error
                table = self.which_table(curr_id.name, self.currency_table)

                # Force update == break connection with existing rates
                if wizard.force_update:
                    
                    if date_for_update.weekday() == 4:
                        ids_to_del =currency_rate_obj.search([('name','=',(date_for_update + datetime.timedelta(days=1)).strftime('%Y-%m-%d')),('currency_id', '=', curr_id.id)])
                        if ids_to_del:
                            ids_to_del.unlink()
                        ids_to_del = currency_rate_obj.search([('name','=',(date_for_update + datetime.timedelta(days=3)).strftime('%Y-%m-%d')),('currency_id', '=', curr_id.id)])
                        if ids_to_del:
                            ids_to_del.unlink()
                    else:
                        ids_to_del = currency_rate_obj.search([('name','=',(date_for_update + datetime.timedelta(days=1)).strftime('%Y-%m-%d')),('currency_id', '=', curr_id.id)])
                        if ids_to_del:
                            ids_to_del.unlink()

                # If selected currency and date cannot be found in database download from NBP
                if not currency_rate_obj.search([('name','=',(date_for_update + datetime.timedelta(days=1)).strftime('%Y-%m-%d')),('currency_id','=',curr_id.id),('company_id', '=', company_id)]):
                    url = 'http://api.nbp.pl/api/exchangerates/rates/%s/%s/%s/' % (table, curr_id.name, datetime.datetime.strftime(date_for_update,"%Y-%m-%d"))

                    #If there is no response from server go to next currency else retrieve rate and date
                    if self.get_currency_rate(url) == False:
                        continue
                    else:
                        rate,rate_date = self.get_currency_rate(url)

                        # This checking if date is friday is for putting rates from this day to saturday and monday
                        if datetime.datetime.strptime(rate_date,"%Y-%m-%d").weekday() == 4:

                            # MONDAY
                            rate_date_datetime = (datetime.datetime.strptime(rate_date, '%Y-%m-%d') + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
                            log = currency_rate_obj.create({
                                                    'currency_id': curr_id.id,
                                                    'rate': 1/rate,
                                                    'name': rate_date_datetime,
                                                    'company_id' : service_id and service.company_id.id or False
                                                })
                            # SATURDAY
                            rate_date_datetime = (datetime.datetime.strptime(rate_date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                            log = currency_rate_obj.create({
                                                    'currency_id': curr_id.id,
                                                    'rate': 1/rate,
                                                    'name': rate_date_datetime,
                                                    'company_id' : service_id and service.company_id.id or False
                                                })
                        else:
                            rate_date_datetime = (datetime.datetime.strptime(rate_date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                            log = currency_rate_obj.create({
                                                    'currency_id': curr_id.id,
                                                    'rate': 1/rate,
                                                    'name': rate_date_datetime,
                                                    'company_id' : service_id and service.company_id.id or False
                                                })
            date_for_update = (date_for_update + datetime.timedelta(days=1)).strftime('%Y%m%d')
        logger.warn("Currency rates updated. Finished in {0} seconds".format(time.time()-start_time))
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
