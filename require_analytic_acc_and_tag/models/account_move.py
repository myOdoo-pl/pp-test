# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"
    
    def action_post(self):
        for line in self.invoice_line_ids:
            if line.display_type:
                continue
            if line.analytic_account_id.id == False or len(line.analytic_tag_ids) == 0:
                raise ValidationError(_("No analytical account or analytical tags for %s" % (line.product_id.name)))
        return super(AccountMove, self).action_post()