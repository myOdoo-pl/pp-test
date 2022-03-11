from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"
    
    contractor_id = fields.Many2one(related='analytic_account_id.partner_id', string="Contractor")
    company_group_id = fields.Many2one(related='contractor_id.company_group_id', string="Company Group")
    salesman_id = fields.Many2one(related='analytic_account_id.user_id', string="Salesman")
