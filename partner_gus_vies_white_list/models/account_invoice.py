# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        if self.partner_id.vat and not self.partner_id.vat_subjected:
            raise ValidationError(_("Partner VAT is not valid, please double check it!"))
        else:
            return super(AccountMove, self).action_post()
