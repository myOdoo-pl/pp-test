from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('analytic_account_id', 'user_id')
    def _onchange_analytic_account_id(self):
        if self.user_id and self.analytic_account_id:
            self.analytic_account_id.user_id = self.user_id.id
