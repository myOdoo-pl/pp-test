# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError
from datetime import datetime

from openerp.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period
from pprint import pprint

import logging
_logger = logging.getLogger(__name__)

#TODO TEST DOCUMENT LAYOUT
class AccountReportInvoiceRegister(models.TransientModel):
    _name = "account.report.invoice_register"
    _description = "Invoice Register Report"
    # _inherit = "account.common.report"

    # journal_id = fields.Many2one("account.journal", "Journal", default=lambda self: self.env['account.journal'].search([['type', '=', 'sale']], limit=1))
    register_journal_ids = fields.Many2many("account.journal", string="Journals")
    journal_type = fields.Selection([
            ('sale', 'Sale'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('general', 'Miscellaneous'),], 'Journal Type', default='sale')
    date_from = fields.Date(string='Start Date', default=lambda x: datetime.now().strftime('%Y-%m')+'-01')
    date_to = fields.Date(string='End Date')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    cash_basis_pl = fields.Boolean("Cash basis", help="Select this if you are using chash basis method speciffic for polish accounting.", default=lambda self: self.company_id.cash_basis_pl)
    different_period_items = fields.Boolean("Different Tax Dates", help='Zaznacz, aby wygenerować raport składający się z elementów z inną datą do podatku niż data zapisu księgowego w podnym miesiącu.')


    @api.onchange('journal_type')
    def onchange_journal_type(self):
        register_journal_ids = self.env['account.journal'].search([('type', '=', self.journal_type)])
        self.register_journal_ids = [(4, journal,0) for journal in register_journal_ids.ids]

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        data_to_period.check_dates(self)

    @api.onchange('date_from')
    def _set_date_to(self):
        data_to_period.set_date_to(self)

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.cash_basis_pl = self.company_id.cash_basis_pl

    # BUG in ODOO or wrong many2many write method
    # changed options in creation of this record for m2m:
    # FROM 1 (create new record with values) TO 4 (link to existing records)
    # in former versions this was not needed
    # @api.model
    # def create(self, vals):
    #     journal_type = vals['journal_type']
    #     register_journal_ids = self.env['account.journal'].search([('type', '=', journal_type)])
    #     journal_update = [(4, journal_id, 0) for journal_id in register_journal_ids.ids]
    #     vals['register_journal_ids'] = journal_update
    #     res = super(AccountReportInvoiceRegister, self).create(vals)
    #     return res


    def generate_report(self):
        data = {}
        VatUtils = self.env['wizard.vat.utils']
        VatUtils.check_company_data(self)
        vat_dict =VatUtils.get_vat_details(self, filter_journals=self.register_journal_ids, cash_basis=self.cash_basis_pl, different_period_items=self.different_period_items)

        if not self.journal_type:
            raise UserError(_("Choose journal type"))
        data['wizard_id'] = self.id
        data['wizard_model'] = self._name
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['register_journal_ids'] = self.register_journal_ids.ids
        data['journal_type'] = self.journal_type
        data['vat_dict'] = vat_dict
        return self.env.ref('account_pl_cirrus.account_invoice_register').report_action(self, data=data)
