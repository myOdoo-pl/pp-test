from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gus_code = fields.Char(related='company_id.gus_code', string="GUS code", readonly=False)
    use_gus_code = fields.Boolean(
        string='GUS code',
        config_parameter='res_partner.use_gus_code')
