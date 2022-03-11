# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import datetime
from openerp.exceptions import UserError
from openerp.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period, REVERSE_QUARTER_MAP

from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class WizardJpkFa1(models.TransientModel):
    _name='wizard.jpk.fa.1'
    _inherit='account.common.report'

    period = fields.Selection([
        ("1", 'Monthly'),
        ("3/1", '1st Quarter'),
        ("3/2", '2nd Quarter'),
        ("3/3", '3rd Quarter'),
        ("3/4", '4th Quarter')], 'Period Type', default="1", required=True)
    date_from = fields.Date(string='Start Date', default=lambda x: datetime.now().strftime('%Y-%m')+'-01')
    company_id = fields.Many2one("res.company", "Company", default=lambda self: self.env.user.company_id)
    jpk_fa_file = fields.Binary("Plik JPK-FA", readonly=True)
    jpk_fa_filename = fields.Char("JPK-FA filename", readonly=True)
    cash_basis_pl = fields.Boolean("Cash basis", help="Select this if you are using chash basis method speciffic for polish accounting.", default=lambda self: self.company_id.cash_basis_pl)


    @api.onchange('date_from', 'period')
    def _set_date_to(self):
        if self.period:
            months, quarter = self.period.partition("/")[::2]
            data_to_period.set_date_to(self, months, quarter)
        else:
            data_to_period.set_date_to(self)

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.cash_basis_pl = self.company_id.cash_basis_pl


    def _print_report(self, data):
        data['company_id'] = self.company_id
        data_to_period.check_dates(self)
        jpk_file = self.env['report.jpk.fa.1'].render_xml(self)
        self.write({'jpk_fa_file': jpk_file, 'jpk_fa_filename':'JPK-FA-' + datetime.now().strftime('%Y-%m-%d') + ".xml"})
        return {'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': self.id,
                    'res_model': self._name,
                    'target': 'new',
                    'context': {
                        'default_model': self._name,
                    },
                }
