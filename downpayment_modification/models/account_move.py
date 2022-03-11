from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('invoice_origin')
    def _set_main_so(self):
        """Compute method for obtaining sale document from which invoice originated."""
        for invoice in self:
            invoice.main_so_id = None

            if invoice.invoice_origin:
                # Check invoice type, to avoid searching wrong source document.
                if invoice.move_type in ['out_invoice', 'out_refund']:
                    # Search for sale document and assign it to new field as clickable record.
                    origin_sp = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)])
                    invoice.main_so_id = origin_sp.id

    main_so_id = fields.Many2one('sale.order', string='Origin Sale Document', compute='_set_main_so',
                                 help='Field for storing origin document for this invoice.')
    is_downpayment = fields.Boolean(string='Downpayment', readonly=True,
                                    help='Set this to True, if this invoice is a downpayment.')
