from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    company_group_id = fields.Many2one('res.partner', string='Company Group', readonly=True)

    def _select_sale(self, fields=None):
        return super(SaleReport, self, fields)._select_sale() + ", s.company_group_id as company_group_id"
