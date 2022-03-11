# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    invoice_id = fields.Many2one(string="Invoice", related="move_id.move_id")