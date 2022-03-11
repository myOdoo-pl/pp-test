# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _, registry, SUPERUSER_ID
from datetime import datetime
from openerp.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

class ResCurrency(models.Model):
    _inherit='res.currency'

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        parameters_obj = self.env['ir.config_parameter']
        currencies = [from_currency, to_currency]
        now = datetime.today()
        field_date_today = str(fields.Date.today())
        today = datetime.strptime(field_date_today, '%Y-%m-%d')

        for currency in currencies:
            check_services = self.env['currency.rate.update.service'].sudo().search([('currency_to_update', 'in', currency.id)])
            if check_services and currency.date:
                currency_date_string = str(currency.date)
                currency_date = datetime.strptime(currency_date_string, '%Y-%m-%d')
                delta = (today - currency_date).days
                max_delta = min(check_services.sudo().mapped('max_delta_days'))
                if delta >= max_delta:
                    last_warning_parameter = parameters_obj.sudo().search([('key', '=', 'currency_rate.warning')])
                    if not last_warning_parameter:
                        last_warning_parameter = parameters_obj.sudo().create({'key': 'currency_rate.warning', 'value': now.strftime('%Y-%m-%d %H:%M:%S')})
                    last_warning_parm = str(last_warning_parameter.sudo().value)
                    warning_date = datetime.strptime(last_warning_parm, '%Y-%m-%d %H:%M:%S')
                    time_difference = (now - warning_date).total_seconds() / 60
                    if time_difference > 15:
                        # CREATE NEW ENVIRONMENT IN ORDER TO WRITE DATE NEXT TO EXCEPTION
                        with api.Environment.manage():
                            with registry(self.env.cr.dbname).cursor() as new_cr:
                                new_env = api.Environment(new_cr, SUPERUSER_ID, self.env.context)
                                last_warning_parameter.with_env(new_env).write({'value': now.strftime('%Y-%m-%d %H:%M:%S')})
                                new_env.cr.commit()
                        _logger.warn("CURRENCY RATE UPDATE ERROR:")
                        _logger.warn("DATYS WITHOUT RATE UPDATE: %s" %str(delta))
                        _logger.warn("UPDATE SERVICE MAX DELTA: %s" %str(max_delta))
                        raise ValidationError(_('Currency %s is out of date. Last rate update was on %s.\nPlease contact your system administrator or run history update from Currency Rate Update menu.') %(currency.name, currency_date.strftime('%Y-%m-%d')))
        return super(ResCurrency, self)._get_conversion_rate(from_currency, to_currency, company, date)
