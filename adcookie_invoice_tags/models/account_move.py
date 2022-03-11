from odoo import api, fields, models, _

from random import randint


class AccountMove(models.Model):
    _inherit = 'account.move'

    category_id = fields.Many2many('account.move.category', string='Tags')


class AccountMoveCategory(models.Model):
    _description = 'Invoice Tags'
    _name = 'account.move.category'
    _order = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index', default=_get_default_color)
    invoice_ids = fields.Many2many('account.move', string='Invoices')
