from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    company_group_id = fields.Many2one('res.partner', string='Company Group', readonly=True)

    @api.model
    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", move.company_group_id as company_group_id"
