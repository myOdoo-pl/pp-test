# -*- coding: utf-8 -*-
from pprint import pprint
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import float_is_zero, float_compare, pycompat

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['communication'] = invoice['invoice_payment_ref'] or invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            if invoice['type'] in ('out_invoice', 'in_refund'):
                if invoice['amount_total'] >= 0.0:
                    rec['payment_type'] = 'inbound'
                else:
                    rec['payment_type'] = 'outbound'
            else:
                if invoice['amount_total'] >= 0.0:
                    rec['payment_type'] = 'outbound'
                else:
                    rec['payment_type'] = 'inbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = abs(invoice['amount_residual'])
        return rec
