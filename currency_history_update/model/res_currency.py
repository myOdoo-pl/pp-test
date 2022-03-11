# -*- encoding: utf-8 -*-
##############################################################################
#
#    (C) 2015 OpenGlobe
#    Author: Mikołaj Dziurzyński, Mariusz Osak, Grzegorz Grzelak (OpenGlobe)
#
#    All Rights reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

class res_currency(models.Model):
    _inherit = 'res.currency'

    def _get_reverse_rate(self):
        for record in self:
            record.reverse_rate = 1/record.rate

    reverse_rate = fields.Float(
        compute="_get_reverse_rate", digits=(12,15), string="Reverse Rate")


class res_currency_rate(models.Model):
    _inherit = 'res.currency.rate'

    def _get_reverse_rate(self):
        for record in self:
            record.reverse_rate = 1/record.rate


    reverse_rate = fields.Float(
        compute="_get_reverse_rate", digits=(12,15), string="Reverse Rate")
