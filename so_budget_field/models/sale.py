from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _is_budget_set(self):
        for rec in self:
            analytic_accs = self.env['crossovered.budget.lines'].search([('analytic_account_id', '=', rec.analytic_account_id.id)])
            if len(analytic_accs) > 0:
                rec.budget_set = True
            else:
                rec.budget_set = False
    
    budget_set = fields.Boolean('Budget Set', compute='_is_budget_set')
