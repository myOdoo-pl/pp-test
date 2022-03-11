# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from openerp import fields, models, _, api
from openerp.exceptions import UserError

from openerp.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period, REVERSE_QUARTER_MAP

_logger = logging.getLogger(__name__)


class AccountReportVatUE4(models.TransientModel):
    _name = "account.report.vat.ue4"
    _description = "VAT-UE Report"
    _inherit = "account.common.report"

    date_from = fields.Date(
        string='Start Date', default=lambda x: datetime.now().strftime('%Y-%m')+'-01')
    vatue_file = fields.Binary("VAT-UE File", readonly=True)
    vatue_filename = fields.Char("VAT-UE Filename", size=64, readonly=True)
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.user.company_id.id)
    person_type = fields.Selection([
        ('T', 'Osoba fizyczna'),
        ('F', 'Osoba niefizyczna'),
    ], 'Person Type', default="F")
    xml = fields.Text("XML")

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if self.date_from.month != self.date_to.month:
            raise UserError(_("Version 4 of VAT-UE accepts only monthly declarations. Choose range of one month only."))
        data_to_period.check_dates(self)

    @api.onchange('date_from')
    def _set_date_to(self):
        data_to_period.set_date_to(self)

    def _print_report(self, data):
        VatUtils = self.env['wizard.vat.utils']
        VatUtils.check_company_data(self)

        data['xml_version'] = self.env.context.get('xml_version')
        data['wizard_id'] = self.id
        data['wizard_model'] = self._name
        data['month'] = str(self.date_from.month)
        data['year'] = str(self.date_from.year)
        data['vat_dict'] = VatUtils.get_vat_details(self)

        if self.env.context.get('xml_version') and not self._context.get('correction'):
            vatue_file = self.env['report.account_pl_cirrus.report_vat_ue_4'].render_xml(data)

            period = data.get('month') and data['month'] or data['quarter']
            self.write({'vatue_file': vatue_file, 'vatue_filename':
                        'VAT-UE-'+data['year']+'-' + period + '.xml'})
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
        elif not self.env.context.get('xml_version') and not self._context.get('generate'):
            return self.env.ref('account_pl_cirrus.account_vat_ue_4').report_action(self, data=data)
