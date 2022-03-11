# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from openerp import fields, models, _, api
from openerp.exceptions import UserError
from openerp.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period, REVERSE_QUARTER_MAP

from pprint import pprint
_logger = logging.getLogger(__name__)


class AccountReportVat7_19(models.TransientModel):
    _name = "account.report.vat.7.19"
    _description = "VAT-7 Report"
    _inherit = "account.common.report"

    period = fields.Selection([
        ("1", 'Monthly'),
        ("3/1", '1st Quarter'),
        ("3/2", '2nd Quarter'),
        ("3/3", '3rd Quarter'),
        ("3/4", '4th Quarter')], 'Period Type', default="1", required=True)
    date_from = fields.Date(
        string='Start Date', default=lambda x: datetime.now().strftime('%Y-%m')+'-01')
    vat7_file = fields.Binary("VAT-7 File", readonly=True)
    vat7_filename = fields.Char("VAT-7 Filename", size=64, readonly=True)
    vat7k_file = fields.Binary("VAT-7K File", readonly=True)
    vat7k_filename = fields.Char("VAT-7K Filename", size=64, readonly=True)
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.user.company_id)
    person_type = fields.Selection([
        ('T', 'Osoba fizyczna'),
        ('F', 'Osoba niefizyczna'),
    ], 'Person Type', default="F")
    # xml = fields.Text("XML")
    cash_basis_pl = fields.Boolean("Cash basis", help="Select this if you are using chash basis method speciffic for polish accounting.", default=lambda self: self.company_id.cash_basis_pl)


    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        data_to_period.check_dates(self)

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

    def _extend_data(self, data):
        VatUtils = self.env['wizard.vat.utils']

        data['xml_version'] = self.env.context.get('xml_version')
        data['wizard_id'] = self.id
        if self.date_from.month != self.date_to.month:
            if self.date_from.month not in REVERSE_QUARTER_MAP:
                raise UserError(
                    _("Please choose correct starting date for given quarter (use period field)!"))
            data['quarter'] = REVERSE_QUARTER_MAP[self.date_from.month]
        else:
            data['month'] = str(self.date_from.month)
        data['year'] = str(self.date_from.year)

        data['vat_dict'] = VatUtils.get_vat_details(self, cash_basis=self.cash_basis_pl)
        data['wizard_model'] = self._name
        return data

    def _print_report(self, data):
        # self._check_company_data()
        VatUtils = self.env['wizard.vat.utils']
        VatUtils.check_company_data(self)

        data = self._extend_data(data)
        pprint(self.env.context)
        if self.env.context.get('vat-7'):
            return self._print_vat7(data)
        else:
            return self._print_vat7k(data)

    def _print_vat7(self, data):
        _logger.warning('data                     '+str(data))
        if self.env.context.get('xml_version'):
            vat7_file = self.env[
                'report.account_pl_cirrus.report_vat_7_19'].render_xml(data)
            self.write({'vat7_file': vat7_file, 'vat7_filename':
                        'VAT7-'+data['year']+'-'+data['month']+'.xml'})
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
        else:
            return self.env.ref('account_pl_cirrus.account_vat_7_19').report_action(self, data=data)

    def _print_vat7k(self, data):
        if self.env.context.get('xml_version'):
            vat7k_file = self.env['report.account_pl_cirrus.report_vat_7k_13'].render_xml(data)
            self.write({'vat7k_file': vat7k_file, 'vat7k_filename':
                        'VAT7K-'+data['year']+'-'+data['quarter']+'.xml'})
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
        else:
            pprint(self.env.context)
            return self.env.ref('account_pl_cirrus.account_vat_7k_13').report_action(self, data=data)
