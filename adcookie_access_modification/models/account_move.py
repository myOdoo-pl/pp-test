from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import format_date, get_lang
from odoo.tools import float_compare

from collections import defaultdict

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    sensitive_data = fields.Boolean(string='Sensitive data', default=False)
    selected_in_wizard = fields.Boolean(string='Selected', default=False)

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
            raise UserError(
                _('You cannot create a move already in the posted state. Please create a draft move and post it after.'))

        vals_list = self._move_autocomplete_invoice_lines_create(vals_list)

        # _logger.info(f"VALS LIST: {vals_list}")
        # _logger.info(f"VALS LIST TYPE: {type(vals_list)}")
        # for vals in vals_list:
        #     _logger.info(f"VALS: {vals}")
        #     _logger.info(f"VALS TYPE: {type(vals)}")

        new_vals_list = []

        for vals in vals_list:

            if vals.get('move_type') == 'in_invoice' or vals.get('move_type') == 'in_refund':
                vals['sensitive_data'] = True

            new_vals_list.append(vals)

        vals_list = new_vals_list

        rslt = super(AccountMove, self).create(vals_list)
        for i, vals in enumerate(vals_list):
            if 'line_ids' in vals:
                rslt[i].update_lines_tax_exigibility()
        return rslt
