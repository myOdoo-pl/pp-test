from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _prepare_invoice_values(self, order, name, amount, so_line):
        """Extended method for generating values for the invoice that's about to be created.

        :param order: Origin sale order.
        :param name: Downpayment name.
        :param amount: Downpayment value.
        :param so_line: Record from origin sale order line that represents downpayment.
        :return: Values for create method of invoice model.
        """
        invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)

        # If this is downpayment invoice, add new value.
        if self.advance_payment_method != 'delivered':
            invoice_vals['is_downpayment'] = True
            invoice_vals['journal_id'] = self.env.ref('downpayment_modification.downpayment_journal').id

        return invoice_vals
