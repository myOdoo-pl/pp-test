# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import datetime
from openerp.exceptions import UserError
from openerp.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period, REVERSE_QUARTER_MAP
import re

from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class WizardJpkVat(models.TransientModel):
    _name='wizard.jpk.vat.3'
    _inherit='account.common.report'

    period = fields.Selection([
        ("1", 'Monthly'),
        ("3/1", '1st Quarter'),
        ("3/2", '2nd Quarter'),
        ("3/3", '3rd Quarter'),
        ("3/4", '4th Quarter')], 'Period Type', default="1", required=True)
    date_from = fields.Date(string='Start Date', default=lambda x: datetime.now().strftime('%Y-%m')+'-01')
    company_id = fields.Many2one("res.company", "Company", default=lambda self: self.env.user.company_id)
    vat_file = fields.Binary("Plik JPK ewidencji VAT", readonly=True)
    vat_filename = fields.Char("JPK VAT filename", readonly=True)
    cash_basis_pl = fields.Boolean("Cash basis", help="Select this if you are using chash basis method speciffic for polish accounting.", default=lambda self: self.company_id.cash_basis_pl)
    correction_number = fields.Integer("Nr korekty", default=0, required=True, help="Wartość '0' oznacza generowanie nowego pliku za dany okres. Każda kolejna wartość '1', '2', '3' itd., oznacza numer korekty.")
    pdf_file = fields.Binary("Plik podglądowy PDF", readonly=True)
    pdf_filename = fields.Char("JPK VAT filename", readonly=True)

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
        file_and_dict = self.env['report.jpk.vat.3'].render_xml(self)
        jpk_file = file_and_dict[0]
        self.write({'vat_file': jpk_file, 'vat_filename': 'VAT-JPK-' + self.date_from.strftime('%Y-%m-') + str(self.correction_number) + '-' + datetime.now().strftime('%Y-%m-%d') + ".xml"})
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





    def print_pdf_report(self):
        file_and_dict = self.env['report.jpk.vat.3'].render_xml(self)
        vat_dict = file_and_dict[1]
        # pprint(vat_dict)
        data_dict = {}
        data_dict['wizard_id'] = self.id
        data_dict['wizard_model'] = self._name
        data_dict['date_from'] = self.date_from
        data_dict['date_to'] = self.date_to
        data_dict['vat_dict'] = vat_dict
        return self.env.ref('account_pl_cirrus.account_jpk_vat3_pdf').report_action(self, data=data_dict)
