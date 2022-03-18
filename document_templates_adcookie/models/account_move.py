from odoo import api, fields, models, _

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_ref_from_ref(self):
        self.correction_ref = ''
        for invoice in self:
            if invoice.ref:
                invoice.correction_ref = invoice.ref.split(', ')[0]

    def _get_reason_from_ref(self):
        self.correction_reason = ''
        for invoice in self:
            if invoice.ref:
                reason = invoice.ref.split(', ')[1:]
                invoice.correction_reason = ''.join([s+', ' for s in reason])[:-2]

    invoice_payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms',
                                              check_company=True,
                                              readonly=True, states={'draft': [('readonly', False)]})

    invoice_sale_date = fields.Date(string='Old Sale Date', default=fields.Date.today(), help='Sale date for this invoice.')
    date = fields.Date(
        string='Sale Date',
        required=True,
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
        default=fields.Date.context_today
    )
    correction_ref = fields.Char(compute='_get_ref_from_ref')
    correction_reason = fields.Char(compute='_get_reason_from_ref')
    duplicate_date = fields.Datetime(string='Duplicate Date', default=fields.Datetime.now())

    tax_dict = dict()
    correction_tax_dict = dict()

    def get_duplicate_invoice_date(self):
        self.duplicate_date = datetime.now()
        return self.duplicate_date

    def correction_line_tax_summing(self):
        self.correction_tax_dict.clear()

        for line in self.correction_invoice_line_ids:
            if line.invoice_line_tax_ids:
                tax_name = line.invoice_line_tax_ids[0].name
                net_price = line.price_subtotal
                tax_value = line.invoice_line_tax
                taxed_value = line.price_total
                values = [net_price, tax_value, taxed_value]

                if tax_name in self.correction_tax_dict.keys():
                    self.correction_tax_dict[tax_name][0] += values[0]
                    self.correction_tax_dict[tax_name][1] += values[1]
                    self.correction_tax_dict[tax_name][2] += values[2]
                else:
                    self.correction_tax_dict.update({tax_name: values})

        tax_dict = self.env['account.move'].search([('id', '=', self.reversed_entry_id.id)]).line_tax_summing()
        for tax_name in self.correction_tax_dict.keys():
            if tax_dict[tax_name]:
                self.correction_tax_dict[tax_name][0] -= tax_dict[tax_name][0]
                self.correction_tax_dict[tax_name][1] -= tax_dict[tax_name][1]
                self.correction_tax_dict[tax_name][2] -= tax_dict[tax_name][2]

        return self.correction_tax_dict

    def line_tax_summing(self):
        self.tax_dict.clear()

        for line in self.invoice_line_ids:
            if line.tax_ids:
                tax_name = line.tax_ids[0].name
                net_price = line.price_subtotal
                tax_value = line.invoice_line_tax
                taxed_value = line.price_total
                values = [net_price, tax_value, taxed_value]

                if tax_name in self.tax_dict.keys():
                    self.tax_dict[tax_name][0] += values[0]
                    self.tax_dict[tax_name][1] += values[1]
                    self.tax_dict[tax_name][2] += values[2]
                else:
                    self.tax_dict.update({tax_name: values})

        return self.tax_dict

    @staticmethod
    def get_dict_key(dictionary, i):
        """Staticmethod for getting key from a dictionary.

        :param dictionary: Python dictionary get from view.
        :param i: Which element of dictionary should be acquired.
        :return: Dictionary key.
        """
        help_list = list()

        for key in dictionary.keys():
            help_list.append(key)

        return help_list[i]

    @staticmethod
    def get_dict_value_price(dictionary, i):
        """Staticmethod for getting price value from a dictionary.

        :param dictionary: Python dictionary get from view.
        :param i: Which element of dictionary should be acquired.
        :return: Dictionary price value.
        """
        help_list = list()

        for value in dictionary.values():
            help_list.append(value)

        return help_list[i][0]

    @staticmethod
    def get_dict_value_weight(dictionary, i, j=1):
        """Staticmethod for getting weight value from a dictionary.

        :param dictionary: Python dictionary get from view.
        :param i: Which element of dictionary should be acquired.
        :param j: Which element of dictionary list value should be acquired.
        :return: Dictionary weight value.
        """
        help_list = list()

        for value in dictionary.values():
            help_list.append(value)
            
        return help_list[i][j]
