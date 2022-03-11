from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = "res.company"

    gus_code = fields.Char(string='GUS code')
