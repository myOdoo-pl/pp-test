from odoo import api, fields, models, _


class CrmLeadFields(models.Model):
    _inherit = "crm.lead"

    scoring = fields.Integer(
        string='Scoring'
    )

    pipedrive_id = fields.Integer(
        string='PipeDrive ID'
    )

    pipedrive_url = fields.Char(
        string='PipeDrive URL',
        compute='_compute_pipedrive_url'
    )

    @api.depends('pipedrive_id')
    def _compute_pipedrive_url(self):
        """Create link from pipedrive_id"""
        self.pipedrive_url = f'https://adcookie.pipedrive.com/deal/{self.pipedrive_id}'
