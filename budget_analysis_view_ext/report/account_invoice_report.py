from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    @api.model
    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", move.partner_id.company_group_id as company_group_id"
