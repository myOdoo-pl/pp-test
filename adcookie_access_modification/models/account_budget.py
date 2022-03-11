from odoo import api, fields, models, _


class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"

    sensitive_data = fields.Boolean(string='Sensitive data', default=True)
