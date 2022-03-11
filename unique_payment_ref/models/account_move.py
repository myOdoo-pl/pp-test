from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        """Check if payment_reference exist for partner and raise UserError if it does."""
        for move in self:
            if not vals.get('payment_reference') and not move.payment_reference:
                continue
            query = [('partner_id', '=', vals.get('partner_id', move.partner_id.id)),
                ('payment_reference', '=', vals.get('payment_reference', move.payment_reference)),
                ('id', '!=', move.id)]
                
            # _logger.info(f"TEST(wrie): partner_id={vals.get('partner_id', move.partner_id.id)}")
            payment_references = move.env['account.move'].search(query)
            # _logger.info(f"TEST(wrie): query={query}, payment_references={payment_references}")

            if len(payment_references) > 0:
                raise UserError(_("Payment reference already exist!"))
        
        return super(AccountMove, self).write(vals)
