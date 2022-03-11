# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_date = fields.Date('Tax Period', help="Period for tax accounting (when different than period for financial accounting)")
    date_issue = fields.Date('Issue Date', readonly=True, index=True,
                             states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]},
                             help="Date of issue of the invoice, current date by default."
                                  "(It differs from the Invoice Date which is the date of sale).")
    custom_partner_id = fields.Many2one('res.partner', string='Partner')


    @api.onchange('date_issue')
    def _onchange_vat_tax_date(self):
        if self.move_type in ['out_refund', 'in_refund']:
            self.tax_date = self.date_issue



    def _check_balanced(self):
        credit = 0.0
        debit = 0.0
        prec = self.company_id.currency_id.decimal_places
        if self.line_ids:
            for line in self.line_ids:
                credit += line.credit
                debit += line.debit
            _logger.warning('credit:          '+str(credit))
            _logger.warning('debit:          '+str(debit))
            if credit != debit:
                difference_full = round(abs(credit - debit),prec)
                if difference_full > 0.0 and difference_full <= 0.02:
                    _logger.warning('Added currecny rate difference in PLN:    '+str(difference_full))
                    difference = [0.01] if difference_full == 0.01 else [0.01, 0.01]
                    loops = len(difference)
                    lines = [line for line in self.line_ids if line.account_id.code[0] not in ['4','5','6']]
                    lines_debit = [line for line in lines if line.debit != 0.0]
                    lines_credit = [line for line in lines if line.credit != 0.0]
                    if credit > debit:#dodac do debitu
                        if lines_debit:
                            if len(lines_debit) >= len(difference):
                                for line_debit in lines_debit:
                                    line_debit.debit += difference[0]
                                    loops -= 1
                                    if loops != 0:
                                        continue
                                    else:
                                        break
                            else:
                                lines_debit[0].debit += difference_full
                        else:
                            if len(lines_credit) >= len(difference):
                                for line_credit in lines_credit:
                                    line_credit.credit -= difference[0]
                                    loops -= 1
                                    if loops != 0:
                                        continue
                                    else:
                                        break
                            else:
                                lines_credit[0].credit -= difference_full

                    else:
                        if lines_credit:
                            if len(lines_credit) >= len(difference):
                                for line_credit in lines_credit:
                                    line_credit.credit += difference[0]
                                    loops -= 1
                                    if loops != 0:
                                        continue
                                    else:
                                        break
                            else:
                                lines_credit[0].credit += difference_full
                        else:
                            if len(lines_debit) >= len(difference):
                                for line_debit in lines_debit:
                                    line_debit.debit -= difference[0]
                                    loops -= 1
                                    if loops != 0:
                                        continue
                                    else:
                                        break
                            else:
                                lines_debit[0].debit -= difference_full
        for move in self:
            _logger.warning('Account Move: %s'% move.name)
            for line in move.line_ids:
                _logger.warning('Debit: %s Credit: %s Currency: %s)' %(line.debit,line.credit,line.amount_currency))
        res = super(AccountMove, self)._check_balanced()
        return res




class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tax_date = fields.Date(related='move_id.tax_date', string='Tax Period', help="Period for tax accounting (when different than period for financial accounting)")
    tax_value = fields.Monetary(currency_field="company_currency_id")
    date_manual = fields.Date(string='Custom Date')
    tax_basic_custom = fields.Float(string='Custom Nett Value')
