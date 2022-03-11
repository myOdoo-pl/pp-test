# -*- coding: utf-8 -*-

import logging
from pprint import pprint
from odoo import models, fields, api, _

from odoo.addons import decimal_precision as dp

from odoo.exceptions import UserError, RedirectWarning, ValidationError #

_logger = logging.getLogger(__name__)


class CorrectionAccountInvoiceLine(models.Model):
    _name = "correction.account.invoice.line"
    _description = "Correction Invoice Line"

    name = fields.Text(string='Description')
    account_id = fields.Many2one('account.account', string='Account')
    original_quantity = fields.Float(string='Original Quantity', digits=dp.get_precision('Product Unit of Measure'))
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    original_price_unit = fields.Float(string='Original Unit Price',)
    price_unit = fields.Float(string='Unit Price', default=0)
    discount = fields.Float(string='Discount (%)')
    # price_subtotal = fields.Monetary(string='Amount')#, compute='_compute_price')
    price_subtotal = fields.Monetary(string='Amount', readonly=True)
    price_total = fields.Monetary(string='Gross', readonly=True)
    invoice_line_tax = fields.Monetary(string ="Tax", readonly=True)
    currency_id = fields.Many2one('res.currency')
    sequence = fields.Integer(default=10)
    invoice_id = fields.Many2one('account.move', string='Invoice Reference', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    invoice_line_tax_ids = fields.Many2many('account.tax','account_correction_invoice_line_tax_rel', 'correction_account_invoice_line_id', 'tax_id', string='Taxes')#, domain=[('type_tax_use','!=','none'), '|', ('active', '=', False), ('active', '=', True)], oldname='invoice_line_tax_id')
    invoice_line_ids = fields.One2many('account.move.line', 'correction_invoice_line_id')
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], default=False, help="Technical field for UX purpose.")

    @api.onchange('quantity', 'price_unit', 'invoice_line_tax_ids')
    def _recompute_correction_lines(self):
        if len(self.invoice_line_ids) == 2:
            self.invoice_line_ids[1].unlink()

        price_include = False
        price_unit = self.price_unit
        if self.invoice_line_tax_ids:
            price_include = self.invoice_line_tax_ids.mapped('price_include')[0]
        if self.discount:
            price_unit = price_unit - (price_unit*(self.discount/100))
            
        taxes_res = self.invoice_line_tax_ids._origin.compute_all(price_unit, currency=self.currency_id, quantity=self.quantity, handle_price_include=price_include)

        self.price_subtotal = taxes_res['total_excluded']
        self.invoice_line_tax = taxes_res['total_included'] - taxes_res['total_excluded']
        self.price_total =  taxes_res['total_included']


#     def recompute_lines_from_correction(self):
#         if self.price_unit != self.original_price_unit and self.quantity != self.original_quantity:
#             if len(self.invoice_line_ids) == 1:
#                 original_line = self.invoice_line_ids
#                 new_line = self.invoice_line_ids.copy()
#             else:
#                 original_line = self.invoice_line_ids[0]
#                 new_line = self.invoice_line_ids[1]
#
#             original_line.update({
#                 'price_unit' : self.original_price_unit - self.price_unit, #price_unit,
#                 'quantity' : self.quantity,#self.original_quantity - self.quantity,
#                 })
#             new_line.update({
#                 'price_unit' : self.original_price_unit,
#                 'quantity' : self.original_quantity - self.quantity,
#                 })
#         else:
#             if len(self.invoice_line_ids) == 2:
#                 self.invoice_line_ids[1].unlink()
#             if self.price_unit != self.original_price_unit:
#                 self.invoice_line_ids.update({
#                     'price_unit' : self.original_price_unit - self.price_unit,
#                     'quantity' : self.quantity,#self.original_quantity - self.quantity,
#                     })
#             elif self.quantity != self.original_quantity:
# #                _logger.warning("------------IN onchange correction QUANTITY")
#                 self.invoice_line_ids.update({
#                     'price_unit' : self.price_unit,
#                     'quantity' : self.original_quantity - self.quantity, #quantity
#                     })
# #                _logger.warning("------------IN onchange correction QUANTITY %s",self.invoice_line_ids.quantity)
#                 self.invoice_line_ids.quantity = self.original_quantity - self.quantity
#             else:
#                 self.invoice_line_ids.update({
#                     'price_unit' : 0,
#                     'quantity' : self.original_quantity #quantity
#                     })
#
#     @api.onchange('price_unit', 'quantity')
#     def _onchange_correction_line(self):
#         self.recompute_lines_from_correction()

    # def write(self, vals):
    #     super(CorrectionAccountInvoiceLine, self).write(vals)
    #     price_subtotal = self.quantity * self.price_unit
    #     if self.price_unit != self.original_price_unit and self.quantity != self.original_quantity:
    #         if len(self.invoice_line_ids) == 1:
    #             original_line = self.invoice_line_ids
    #             new_line = self.invoice_line_ids.copy()
    #         else:
    #             original_line = self.invoice_line_ids[0]
    #             new_line = self.invoice_line_ids[1]
    #
    #         original_line.update({
    #             'price_unit' : self.original_price_unit - self.price_unit, #price_unit,
    #             'quantity' : self.quantity,#self.original_quantity - self.quantity,
    #             })
    #         new_line.update({
    #             'price_unit' : self.original_price_unit,
    #             'quantity' : self.original_quantity - self.quantity,
    #             })
    #     else:
    #         if len(self.invoice_line_ids) == 2:
    #             self.invoice_line_ids[1].unlink()
    #         if self.price_unit != self.original_price_unit:
    #             self.invoice_line_ids.update({
    #                 'price_unit' : self.original_price_unit - self.price_unit,
    #                 'quantity' : self.quantity,#self.original_quantity - self.quantity,
    #                 })
    #         elif self.quantity != self.original_quantity:
    #             self.invoice_line_ids.update({
    #                 'price_unit' : self.price_unit,
    #                 'quantity' : self.original_quantity - self.quantity, #quantity
    #                 })
    #         else:
    #             self.invoice_line_ids.update({
    #                 'price_unit' : 0,
    #                 'quantity' : self.original_quantity #quantity
    #                 })
    #     self.invoice_id._calc_net_gross()
    #     self.invoice_id._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)

        # self.invoice_id.compute_taxes()


    def unlink(self):
        if self.invoice_line_ids:
            self.write({'price_unit': 0, 'quantity': self.original_quantity})
        return super(CorrectionAccountInvoiceLine, self).unlink()
