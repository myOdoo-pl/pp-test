from odoo import models, fields, api, _
from datetime import datetime as dt

from odoo.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period

import logging

_logger = logging.getLogger(__name__)


class WizardJpkWb(models.TransientModel):
    _name = "wizard.jpk.wb"
    _inherit='account.common.report'


    period = fields.Selection([
        ("1", 'Monthly'),
        ("3/1", '1st Quarter'),
        ("3/2", '2nd Quarter'),
        ("3/3", '3rd Quarter'),
        ("3/4", '4th Quarter')], 'Period Type', default="1", required=True)
    date_from = fields.Date(string='Start Date', default=lambda x: dt.now().strftime('%Y-%m')+'-01')
    journal_id = fields.Many2one('account.journal', 'Bank Statement Journal', required=True, domain=[('type','=','bank')])
    jpk_wb_file = fields.Binary('JPK-WB file', readonly=True)
    jpk_wb_filename = fields.Char('JPK-WB filename', readonly=True)

    @api.onchange('date_from', 'period')
    def _set_date_to(self):
        if self.period:
            months, quarter = self.period.partition("/")[::2]
            data_to_period.set_date_to(self, months, quarter)
        else:
            data_to_period.set_date_to(self)


    def _print_report(self, data):
        data['company_id'] = self.company_id
        data_to_period.check_dates(self)
        jpk_file = self.env['report.jpk.wb'].render_xml(self)
        self.write({'jpk_wb_file': jpk_file, 'jpk_wb_filename':'JPK-WB-' + dt.now().strftime('%Y-%m-%d') + ".xml"})
        return {'type': 'ir.actions.act_window',
                    'name': 'JPK-WB',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': self.id,
                    'res_model': self._name,
                    'target': 'new',
                    'context': {
                        'default_model': self._name,
                    },
                }
