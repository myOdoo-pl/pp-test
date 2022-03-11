from odoo import api, fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    sensitive_data = fields.Boolean(string='Sensitive data', default=False)
    user_id = fields.Many2one('res.users', string='Responsible', ondelete='restrict')
