from odoo import api, fields, models


class Contract(models.Model):
    _inherit = 'hr.contract'

    overhead = fields.Monetary(string='Overhead', help='Overhead for this employee per month.')
