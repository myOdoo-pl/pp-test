from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    company_bank_id = fields.Many2one('res.partner.bank', string='Your Bank Account', help='Your bank account number.')
    date_order = fields.Datetime(string='Order Date', readonly=False, index=True, default=fields.Datetime.now,
                                 states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
