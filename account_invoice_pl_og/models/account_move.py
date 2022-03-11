# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#    Module is copyrighted by OpenGLOBE (www.openglobe.pl) and Cirrus (www.cirrus.pl)
#    with the same rules as OpenObject and Odoo.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import json
import logging
from pprint import pprint
from collections import defaultdict
from functools import partial
from datetime import datetime

from odoo.exceptions import UserError
from odoo import models, fields, api, _
# from odoo.tools import amount_to_text_en
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang, format_date, get_lang

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'


    @api.depends('amount_residual')
    def _compute_word_amount(self):

        def num2word(n,l="en_US"):
        #    wordtable = ["zer","jed","dwa","trz","czt","pie","sze","sie","osi","dzi"]
            sym={
                "en_US": {
                    "0": u'zero',
                    "x": [u'one',u'two',u'three',u'four',u'five' ,u'six',u'seven',u'eight',u'nine'],
                    "1x": [u'ten',u'eleven',u'twelve',u'thirteen',u'fourteen',u'fifteen',u'sixteen',u'seventeen',u'eighteen',u'nineteen'],
                    "x0": [u'twenty',u'thirty',u'fourty',u'fifty',u'sixty',u'seventy',u'eighty',u'ninety'],
                    "100": u'hundred',
                    "1K": u'thousand',
                    "1M": u'million',
                },
                "pl_PL": {
                    "0": u'zero',
                    "x": [u'jeden',u'dwa',u'trzy',u'cztery',u'pięć' ,u'sześć',u'siedem',u'osiem',u'dziewięć'],
                    "1x": [u'dziesięć',u'jedenaście',u'dwanaście',u'trzynaście',u'czternaście',u'piętnaście',u'szesnaście',u'siedemnaście',u'osiemnaście',u'dziewiętnaście'],
                    "x0":  [u'dwadzieścia',u'trzydzieści',u'czterdzieści',u'pięćdziesiąt',u'sześćdziesiąt',u'siedemdziesiąt',u'osiemdziesiąt',u'dziewięćdziesiąt'],
                    "1xx": [u'sto',u'dwieście',u'trzysta',u'czterysta',u'pięćset',u'sześćset',u'siedemset',u'osiemset',u'dziewięćset'],
                    "1000" : u'tysiąc',
                    "1K": [u'tysięcy',u'tysięcy',u'tysiące',u'tysiące',u'tysiące',u'tysięcy',u'tysięcy',u'tysięcy',u'tysięcy',u'tysięcy', 'tysięcy'],
                    "1M" : u'milion',
                    "1Ms": [u'milionów',u'milionów',u'miliony',u'miliony',u'miliony',u'milionów',u'milionów',u'milionów',u'milionów',u'milionów'],
               }
            }

            if n==0:
                word = sym[l]["0"]
            elif n<10:
                word = sym[l]["x"][int(n-1)]
            elif n<100:
                if n<20:
                    word = sym[l]["1x"][int(n-10)]
                else:
                    word = sym[l]["x0"][int(n/10-2)] + (n%10 and " " + num2word(n%10,l) or "")
            elif n<1000:
                if l=="en_US":
                    word = sym[l]["x"][int(n/100-1)]+" " + sym[l]["100"]+(n%100 and " "+num2word(n%100,l) or "")
                elif l=="pl_PL":
                    word = sym[l]["1xx"][int(n/100-1)] + (n%100 and " "+num2word(n%100,l) or "")
            elif n<1000000:
                if l=="en_US":
                    word = num2word(n/1000,l)+" "+sym[l]["1K"]+(n%1000 and " "+num2word(n%1000,l) or "")
                elif l=="pl_PL":
                    if n <2000:
                        tys = sym[l]["1000"]
                    elif n%100000>10000 and n%100000<20000:
                        tys = sym[l]["1K"][0]
                    else:
                        tys = sym[l]["1K"][int(n/1000%10)]
                    word = num2word(n/1000,l) +" "+ tys + (n%1000  and " " + num2word(n%1000,l) or "")
            elif n<1000000000:
                if l=="en_US":
                    word = num2word(n/1000000,l)+" "+sym[l]["1M"] + (n%1000000  and " " + num2word(n%1000000,l) or "")
                if l=="pl_PL":
                    if n <2000000:
                        mil = sym[l]["1M"]
                    elif n%100000000>10000000 and n%100000000<20000000:
                        mil = sym[l]["1Ms"][0]
                    else:
                        mil = sym[l]["1Ms"][n/1000000%10]
                    word = num2word(n/1000000,l) +" "+ mil + (n%1000000  and " " + num2word(n%1000000,l) or "")
            else:
                return  "N/A"
            return word

        if self.partner_id.lang=='pl_PL':
            cents = str(self.amount_residual)[-2:]
            if '.' in cents:
                cents = (str(self.amount_residual)[-1:] + '0')
            self.word_amount = (num2word(self.amount_residual, 'pl_PL') + ' ' + str(cents) + '/100')
        else:
            iso_code = self.env['res.lang'].search([('code','=',self.partner_id.lang)])[0].iso_code
            self.word_amount = amount_to_text_en.amount_to_text(self.amount_residual, lang=iso_code, currency=self.currency_id.name)

    # STANDARD FIELD: refund_invoice_id
    # original_inv_id = fields.Many2one('account.invoice', 'Refunded Invoice',
    #     readonly = True, states={'draft':[('readonly',False)]},
    #     help="Invoice number of which this refund is based on.")
    # date_issue = fields.Date('Issue Date', readonly=True, index=True,
    #     states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]},
    #     help="Date of issue of the invoice, current date by default."
    #          "(It differs from the Invoice Date which is the date of sale).")
    date_recived = fields.Date('Recieved Date', readonly=True,
        states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}, index=True,
        help="Invoice recieved date, current date by default.")
    vat = fields.Char(related='partner_id.vat', string='NIP')
    display_original_refund = fields.Boolean(default=False)

    correction_invoice_line_ids = fields.One2many('correction.account.invoice.line', 'invoice_id')
    correction_untaxed = fields.Monetary(string='Untaxed Amount',
        store=True, readonly=True, compute='_compute_amount_correction', track_visibility='always')
    correction_tax = fields.Monetary(string='Tax',
        store=True, readonly=True, compute='_compute_amount_correction')
    correction_total = fields.Monetary(string='Total',
        store=True, readonly=True, compute='_compute_amount_correction')
    correction_residual = fields.Monetary(string='To refund',
            related="amount_residual")
    current_country_code = fields.Char(string='Country code', related='company_id.partner_id.country_id.code', store = True)
    correction_due = fields.Boolean()

    wew = fields.Boolean(default=False, string='w przypadku dokumentu wewnętrznego;przykład:przekazanie nieodpłatnie przez podatnika towarów należących do jego przedsiębiorstwa.')
    split_payment_method = fields.Boolean(default=False, string="Transakcja  objęta obowiązkiemstosowania     mechanizmu podzielonej płatności.  Oznaczenie  MPP  należy  stosować  do  faktur  o  kwocie  brutto wyższej niż 15 000,00 zł, które dokumentują dostawętowarów lub świadczenie usług wymienionych w załączniku nr 15 do ustawy.")
    imp = fields.Boolean(default=False, string="Oznaczenie  dotyczące  podatku  naliczonego  z  tytułu  importu towarów, w tym importu towarów rozliczanego zgodnie z art. 33a ustawy")
    sw = fields.Boolean(default=False, string="Dostawa  w  ramach  sprzedaży  wysyłkowej  z  terytorium  kraju, októrej mowa w art. 23 ustawy. ")
    ee = fields.Boolean(default=False, string="Świadczenie   usług telekomunikacyjnych, nadawczych i elektronicznych, o których mowa w art. 28k ustawy.")
    tp = fields.Boolean(default=False, string="Istniejące powiązania między nabywcą a dokonującym dostawy towarów lub usługodawcą, o których mowa w art. 32 ust. 2 pkt 1 ustawy.")
    tt_wnt = fields.Boolean(default=False, string="Wewnątrzwspólnotowe nabycie  towarów  dokonane  przez drugiego  w  kolejności  podatnika  VAT  w  ramach  transakcji trójstronnej w procedurze uproszczonej, o której mowa w dziale XII rozdział8 ustawy.")
    tt_d = fields.Boolean(default=False, string="Dostawa towarów poza terytorium kraju dokonana przez drugiego w  kolejności podatnika  VAT  w  ramach  transakcji  trójstronnej wprocedurze uproszczonej, o której mowa w dziale XII rozdział8 ustawy.")
    mr_t = fields.Boolean(default=False, string="Świadczenie usług turystyki opodatkowane na zasadach marży zgodnie z art. 119 ustawy. ")
    mr_uz = fields.Boolean(default=False, string="Dostawa  towarów  używanych,  dzieł sztuki,  przedmiotów kolekcjonerskich i antyków, opodatkowana na zasadach marży zgodnie z art. 120 ustawy.")
    i_42 = fields.Boolean(default=False, string="Wewnątrzwspólnotowa dostawa towarów następująca po imporcie tych towarów w ramach procedury celnej 42 (import). ")
    i_63 = fields.Boolean(default=False, string="Wewnątrzwspólnotowa dostawa towarów następująca po imporcie tych towarów w ramach procedury celnej 63 (import). ")
    b_spv = fields.Boolean(default=False, string="Transfer  bonu  jednego  przeznaczenia  dokonany  przez  podatnika działającego we własnym imieniu, opodatkowany zgodnie z art. 8a ust. 1 ustawy. ")
    b_spv_dostawa = fields.Boolean(default=False, string="Dostawa towarów oraz świadczenie usług, których dotyczy bon jednego przeznaczenia na rzecz podatnika, który wyemitował bon zgodnie z art. 8a ust. 4 ustawy.")
    b_mpv_prowizja = fields.Boolean(default=False, string="Świadczenie usług pośrednictwa oraz innych usług dotyczących transferu  bonu  różnego  przeznaczenia,  opodatkowane  zgodnie zart. 8b ust. 2 ustawy. ")
    doc_type_vdek = fields.Selection([('RO','RO'),('WEW','WEW'),('FP','FP')],'Typ dokumentu')
    purchase_doc_vdek = fields.Selection([('MK','MK'),('VAT_RR','VAT_RR'),('WEW','WEW')],'Dokument zakupu')



    @api.onchange('correction_invoice_line_ids')
    def _recompute_dynamic_lines_correction(self):
        for line in self.correction_invoice_line_ids:
            after_price_unit = line.original_price_unit - line.price_unit
            if line.quantity != line.original_quantity:
                after_qty = line.original_quantity - line.quantity
                if after_qty > line.original_quantity:
                    after_price_unit = abs(after_qty * line.original_price_unit)
                else:
                    after_price_unit = line.original_price_unit
            else:
                after_qty = line.original_quantity
            line.invoice_line_ids.update({
                'price_unit': after_price_unit,
                'quantity': after_qty,
                })
            line.invoice_line_ids._onchange_price_subtotal()
        self._calc_net_gross()
        self._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)

    def write(self, values):
        res = super(AccountMove, self).write(values)
        for rec in self:
            if rec.currency_id and rec.currency_id.name == 'PLN' and rec.amount_total > 15000:
                for line in rec.invoice_line_ids:
                    marker = line.product_id.product_tmpl_id.get_tax_marker()
                    if marker:
                        if marker.name in ['GTU_05', 'GTU_06', 'GTU_08'] or line.product_id.product_tmpl_id.split_payment_method:
                            if not rec.split_payment_method:
                                rec.split_payment_method = True
        return res


    @api.depends('correction_invoice_line_ids.price_unit', 'correction_invoice_line_ids.quantity')
    def _compute_amount_correction(self):
        for invoice in self:
            round_curr = invoice.currency_id.round
            invoice.correction_untaxed = sum(line.price_subtotal for line in invoice.correction_invoice_line_ids)
            invoice.correction_tax = sum(round_curr(line.invoice_line_tax) for line in invoice.correction_invoice_line_ids)
            invoice.correction_total = invoice.correction_untaxed + invoice.correction_tax
            if invoice.amount_total < 0.0:
                invoice.correction_due = True
            else:
                invoice.correction_due = False


    def get_refund_sum(self, original_tax_lines, refund_tax_lines):
        lines = []
        for tax_line in refund_tax_lines:
            original_line = filter(lambda x: x['name'] == tax_line['name'], original_tax_lines)
            if original_line:
                original_line = next(original_line)
                lines.append({
                    'name': tax_line['name'],
                    'tax': abs(original_line['tax'] - tax_line['tax']),
                    'amount_base': round(original_line['amount_base'] - tax_line['amount_base'],2),
                    'gross_amount': round(original_line['gross_amount'] - tax_line['gross_amount'],2),
                    'foreign_cur': tax_line['foreign_cur'],
                    'country_tax': round(original_line['country_tax'] - tax_line['country_tax'],2)
                })
        return lines

    def funct_tax_lines(self):
        foreign_cur = False
        if self.currency_id.id != self.company_id.currency_id.id:
            if not self.fiscal_position_id or (self.fiscal_position_id.name == "Kraj"):
                foreign_cur = True
        result = []
        tax_lines = [tax_line for tax_line in self.line_ids if tax_line.tax_tag_ids and not tax_line.tax_ids]
        for tax_line in tax_lines:
            if tax_line.credit != 0.0:
                tax = tax_line.credit
            else:
                tax = tax_line.debit
            country_tax = False
            if self:
                move_line = self.env['account.move.line'].search(
                    [('move_id', '=', self.id), ('name', '=', tax_line.name)])
                tax = move_line.credit or move_line.debit
                if foreign_cur:
                    tax = abs(move_line.amount_currency)
                    country_tax = move_line.credit or move_line.debit
            else:
                if foreign_cur:
                    country_tax = self.currency_id._compute(
                        self.currency_id, self.company_id.currency_id, tax)

            amount_base = 0
            gross_amount = 0
            if self.invoice_line_ids:
                for line in self.invoice_line_ids:
                    if line.tax_ids and line.tax_ids[0].name == tax_line.name:
                        amount_base += line.price_subtotal
#                        gross_amount += line.invoice_line_gross
                        gross_amount += line.price_total


            res = {
                'name': tax_line.name,
                'tax': tax,
                'amount_base': amount_base,
                'gross_amount': gross_amount,
                'foreign_cur': foreign_cur,
                'country_tax': country_tax
            }
            result.append(res)
        return result

    # def _amount_by_group(self):
    #     res = super(AccountInvoice, self)._amount_by_group()
    #     for invoice in self:
    #         if invoice.refund_invoice_id:
    #             currency = invoice.currency_id or invoice.company_id.currency_id
    #             fmt = partial(formatLang, invoice.with_context(lang=invoice.partner_id.lang).env, currency_obj=currency)
    #             res2 = {}
    #             for line in invoice.tax_line_ids:
    #                 res2.setdefault(line.tax_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
    #                 res2[line.tax_id.tax_group_id]['amount'] += line.amount
    #                 res2[line.tax_id.tax_group_id]['base'] += line.base
    #             res2 = sorted(res2.items(), key=lambda l: l[0].sequence)
    #             invoice.amount_by_group = [(
    #                 r[0].name, abs(r[1]['amount']), abs(r[1]['base']),
    #                 fmt(abs(r[1]['amount'])), fmt(abs(r[1]['base'])),
    #             ) for r in res2]
    #         else:
    #             return res


    # payments_widget
    # DONE: need further investigation
    # needed different domain for two cases of refunds
    def _get_outstanding_info_JSON(self):
        self.outstanding_credits_debits_widget = json.dumps(False)
        if self.state == 'open':
            domain = [('account_id', '=', self.account_id.id),
                      ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id),
                      ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                      ('amount_residual_currency', '!=', 0.0)]
            if self.move_type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')

            # korekty na plus
            if self.amount_total < 0.0:
                domain = [('account_id', '=', self.account_id.id),
                          ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id),
                          ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                          ('amount_residual_currency', '!=', 0.0)]
                if self.move_type in ('out_invoice', 'in_refund'):
                    domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                    type_payment = _('Outstanding credits')
                else:
                    domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                    type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': self.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = self.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == self.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        amount_to_show = line.company_id.currency_id.with_context(date=line.date).compute(
                            abs(line.amount_residual), self.currency_id)
                    if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                        continue
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, self.currency_id.decimal_places],
                    })
                info['title'] = type_payment
                self.outstanding_credits_debits_widget = json.dumps(info)
                self.has_outstanding = True


    # @api.model
    # def _get_payments_vals(self):
    #     if not self.payment_move_line_ids:
    #         return []
    #     payment_vals = []
    #     currency_id = self.currency_id
    #     for payment in self.payment_move_line_ids:
    #         payment_currency_id = False
    #         if self.move_type in ('out_invoice', 'in_refund'):
    #             amount = sum([p.amount for p in payment.matched_debit_ids if p.debit_move_id in self.line_ids])
    #             amount_currency = sum(
    #                 [p.amount_currency for p in payment.matched_debit_ids if p.debit_move_id in self.line_ids])
    #             if payment.matched_debit_ids:
    #                 payment_currency_id = all([p.currency_id == payment.matched_debit_ids[0].currency_id for p in
    #                                            payment.matched_debit_ids]) and payment.matched_debit_ids[
    #                                           0].currency_id or False
    #         elif self.move_type in ('in_invoice', 'out_refund'):
    #             # treat refunds(correcting invoices) which increase qty or price_unit as standard customer invoices
    #             if self.amount_total < 0.0:
    #                 amount = sum([p.amount for p in payment.matched_debit_ids if p.debit_move_id in self.line_ids])
    #                 amount_currency = sum(
    #                     [p.amount_currency for p in payment.matched_debit_ids if p.debit_move_id in self.line_ids])
    #                 if payment.matched_debit_ids:
    #                     payment_currency_id = all([p.currency_id == payment.matched_debit_ids[0].currency_id for p in
    #                                                payment.matched_debit_ids]) and payment.matched_debit_ids[
    #                                               0].currency_id or False
    #             else:
    #                 amount = sum(
    #                     [p.amount for p in payment.matched_credit_ids if p.credit_move_id in self.line_ids])
    #                 amount_currency = sum([p.amount_currency for p in payment.matched_credit_ids if
    #                                        p.credit_move_id in self.line_ids])
    #                 if payment.matched_credit_ids:
    #                     payment_currency_id = all([p.currency_id == payment.matched_credit_ids[0].currency_id for p in
    #                                                payment.matched_credit_ids]) and payment.matched_credit_ids[
    #                                               0].currency_id or False
    #         # get the payment value in invoice currency
    #         if payment_currency_id and payment_currency_id == self.currency_id:
    #             amount_to_show = amount_currency
    #         else:
    #             amount_to_show = payment.company_id.currency_id.with_context(date=self.date).compute(amount,
    #                                                                                                     self.currency_id)
    #         if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
    #             continue
    #         payment_ref = payment.name
    #         if payment.ref:
    #             payment_ref += ' (' + payment.ref + ')'
    #         payment_vals.append({
    #             'name': payment.name,
    #             'journal_name': payment.journal_id.name,
    #             'amount': amount_to_show,
    #             'currency': currency_id.symbol,
    #             'digits': [69, currency_id.decimal_places],
    #             'position': currency_id.position,
    #             'date': payment.date,
    #             'payment_id': payment.id,
    #             'account_payment_id': payment.payment_id.id,
    #             'invoice_id': payment.invoice_id.id,
    #             'move_id': payment.move_id.id,
    #             'ref': payment_ref,
    #         })
    #     return payment_vals


    @api.onchange('invoice_payment_term_id', 'invoice_date')
    def _onchange_payment_term_date_invoice(self):
        invoice_date = self.invoice_date
        if not invoice_date:
            invoice_date = fields.Date.context_today(self)
        if not self.invoice_payment_term_id:
            # When no payment term defined
            self.invoice_date_due = self.invoice_date_due or self.invoice_date
        else:
            pterm = self.invoice_payment_term_id
            pterm_list = pterm.compute(value=1, date_ref=invoice_date)[0]
            self.invoice_date_due = pterm_list[0]

    def _bank_home(self, partner_id, currency_id, company_id):
        bank_obj = self.env['res.partner.bank']
        if partner_id and partner_id.bank_home_id:
            return partner_id.bank_home_id
        bank_accounts = []
        if currency_id:
#                for bank in self.company_id.partner_id.bank_ids:
#rola partner_id?
            bank_accounts = bank_obj.search([('company_id','=',company_id.id),('partner_id','=',company_id.partner_id.id),('currency_id','=',currency_id.id)])
        if (not bank_accounts) and currency_id and (currency_id.id == company_id.currency_id.id):
            bank_accounts = bank_obj.search([('company_id','=',company_id.id),('partner_id','=',company_id.partner_id.id),('currency_id','=',company_id.currency_id.id)])
        if not bank_accounts:
            bank_accounts = bank_obj.search([('company_id','=',company_id.id),('partner_id','=',company_id.partner_id.id),('currency_id','=',False)])
        # _logger.warn("Bank_accounts: "+str(bank_accounts) +"CURRENCY: " +str(currency_id))
        if not bank_accounts:
            bank_accounts = bank_obj.search([('company_id','=',company_id.id), ('partner_id','=',company_id.partner_id.id)])
            # _logger.warn("Bank_accounts: "+str(bank_accounts)+"COMPANY: " +str(company_id)+ "PARTNER: "+ str(company_id.partner_id))
        # _logger.warn("Bank_accounts: "+str(bank_accounts))
        return len(bank_accounts) and bank_accounts[0] or False


    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super(AccountMove, self)._onchange_partner_id()
        bank_obj = self.env['res.partner.bank']
        if self.move_type == 'out_invoice':
            #if self.partner_id.bank_home_id:
#            bank_home = self._bank_home(self.partner_id, self.currency_id, self.company_id)
            self.partner_bank_id = self._bank_home(self.partner_id, self.currency_id, self.company_id)


#    @api.onchange('currency_id')
#    def _onchange_currency(self):
#        self._onchange_partner_id()


    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        return


    def duplicate_time(self):
        return datetime.now().strftime("%d.%m.%Y")


    def action_date_assign(self):
        for inv in self:
            if not inv.invoice_date:
                inv.write({'invoice_date': fields.Date.context_today(inv)})
            res = inv._onchange_payment_term_date_invoice()
            if (inv.move_type in ('in_refund','out_refund')):
                if not inv.reversed_entry_id:
                    inv.display_original_refund = True
                already_refund = inv.search([('reversed_entry_id', '=', inv.reversed_entry_id.id), ('state', 'in', ['open','paid'])])
            elif res and res.get('value'):
                inv.write(res['value'])
        return True

    def _calc_net_gross(self):
        for invoice in self:
            for line in invoice.invoice_line_ids:
                line._tax_and_gross_line_amounts()
        return True



    def action_invoice_open(self):
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(lambda inv: inv.amount_total < 0 and inv.move_type not in ['out_refund', 'in_refund']):
            raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()

    @api.model
    def create(self, vals):
        bank_obj = self.env['res.partner.bank']
        partner_bank_id = vals.get('partner_bank_id', False)
        invoice_type = vals.get('move_type', False)
        company_id = vals.get('company_id', False)
        currency_id = vals.get('currency_id', False)
        if not invoice_type:
            invoice_type = self.env.context.get('move_type',False)
        if not partner_bank_id and (not invoice_type or invoice_type == 'out_invoice'):
            partner_id = vals.get('partner_id', False)
            partner_obj = self.env['res.partner']
            partner = partner_obj.browse(partner_id)
            currency = currency_id and self.env['res.currency'].browse(currency_id) or False
            company = company_id and self.env['res.company'].browse(company_id) or self.env['res.company'].search([])[0]
            bank_home = self._bank_home(partner, currency, company)
            partner_bank_home_id = bank_home and bank_home.id or False
            vals.update({'partner_bank_id': partner_bank_home_id})

        res = super(AccountMove, self).create(vals)
        ctx = dict(self._context, lang=res.partner_id.lang)
        if not res.invoice_date:
            res.with_context(ctx).write({'invoice_date': fields.Date.context_today(self)})
        res.invoice_line_ids._tax_and_gross_line_amounts()
        self._calc_net_gross()

        if res.reversed_entry_id:
            for line in res.invoice_line_ids:
                tax_ids = []
                for tax in line.tax_ids:
                    tax_ids.append((4, tax.id, None))
                corr_line = self.env['correction.account.invoice.line'].create(
                    {
                        'name' : line.name,
                        'account_id' : line.account_id.id,
                        'original_quantity' : line.quantity,
                        'quantity' : 0,
                        'product_uom_id' : line.product_uom_id.id,
                        'original_price_unit' : line.price_unit,
                        'price_unit' : line.price_unit,
                        'discount' : line.discount,
                        'price_subtotal' : 0,
                        'currency_id' : line.currency_id.id,
                        'product_id' : line.product_id.id,
                        'sequence' : line.sequence,
                        'invoice_line_tax_ids' : tax_ids,#line.tax_ids,
                        'invoice_line_tax' : 0,
                        # 'invoice_line_id' : line.id,
                        'invoice_id' : res.id,
                        'display_type': line.display_type,
                    })

                line.correction_invoice_line_id = corr_line
                res.correction_invoice_line_ids = [(4, corr_line.id)]

            #invoice.invoice_line_ids.write({'price_unit': 0.0})
            # res.compute_taxes()

        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_line_tax = fields.Monetary("Tax", store=True, readonly=True, help="Tax of invoice line.")
#    invoice_line_gross = fields.Monetary("Gross", store=True, help="Gross of invoice line.")

    currency_rate_inversion_line = fields.Float(readonly=True ,digits=(12,4))

    correction_invoice_line_id = fields.Many2one('correction.account.invoice.line')

    quantity = fields.Float(string='Quantity',
        default=1.0, digits='Product Unit of Measure',
        help="The optional quantity expressed by this line, eg: number of product sold. "
             "The quantity is not a legal requirement but is very useful for some reports.")
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    tax_ids = fields.Many2many('account.tax', string='Taxes', help="Taxes that apply on the base amount")

    @api.onchange('amount_currency', 'currency_id', 'account_id')
    def _onchange_amount_currency(self):
       '''Recompute the debit/credit based on amount_currency/currency_id and date.
       However, date is a related field on account.move. Then, this onchange will not be triggered
       by the form view by changing the date on the account.move.
       To fix this problem, see _onchange_date method on account.move.
       '''
       super(AccountMoveLine, self)._onchange_amount_currency()
       force_date = self._context.get('force_date')
       for line in self:
           if line.amount_currency != 0.0:
               # _logger.warning("1) -->   Credit: {},  Debit: {}".format(line.credit, line.debit))
               company_currency_id = line.account_id.company_id.currency_id
               amount = line.amount_currency
               # force_date = False
               if line.currency_id and company_currency_id and line.currency_id != company_currency_id:
                   if not force_date:
                       if self.move_id.move_type in ['out_refund', 'in_refund'] and self.move_id.company_id.country_id.code == 'PL':
                           if self.move_id.reversed_entry_id:
                               force_date = self.move_id.reversed_entry_id.invoice_date
                   rate = self.currency_id.with_context(date=force_date or line.date or fields.Date.today()).rate
                   line.currency_rate_inversion_line = 1/rate
                   amount = line.currency_id._convert(amount, company_currency_id, line.move_id.company_id, force_date or line.date or fields.Date.today())
                   line.debit = amount > 0 and amount or 0.0
                   line.credit = amount < 0 and -amount or 0.0
                   _logger.warning("2) -->   Credit: {},  Debit: {}".format(line.credit, line.debit))


    def _recompute_debit_credit_from_amount_currency(self):
        super(AccountMoveLine, self)._recompute_debit_credit_from_amount_currency()
        force_date = self._context.get('force_date')
        _logger.warning("------------IN RECOMPUTE: %s",force_date)
        for line in self:
            # Recompute the debit/credit based on amount_currency/currency_id and date.

            company_currency = line.account_id.company_id.currency_id
            balance = line.amount_currency
            if line.currency_id and company_currency and line.currency_id != company_currency:
                if not force_date:
                    if self.move_id.move_type in ['out_refund', 'in_refund'] and self.move_id.company_id.country_id.code == 'PL':
                        if self.move_id.reversed_entry_id:
                            force_date = self.move_id.reversed_entry_id.date
                            _logger.warning("------------IN REFUND RECOMPUTE: %s",force_date)
                rate = self.currency_id.with_context(date=force_date or line.move_id.date or fields.Date.today()).rate
                line.currency_rate_inversion_line = 1/rate

                balance = line.currency_id._convert(balance, company_currency, line.account_id.company_id, force_date or line.move_id.date or fields.Date.today())
                line.debit = balance > 0 and balance or 0.0
                line.credit = balance < 0 and -balance or 0.0

#    @api.model
    def _get_fields_onchange_subtotal(self, price_subtotal=None, move_type=None, currency=None, company=None, date=None):
        self.ensure_one()
        force_date = self._context.get('force_date')
        company_currency = self.account_id.company_id.currency_id
        rate = 0.0
        if self.currency_id and company_currency and self.currency_id != company_currency:
            if not force_date:
                if self.move_id.move_type in ['out_refund', 'in_refund'] and self.move_id.company_id.country_id.code == 'PL':
                    if self.move_id.reversed_entry_id:
                        force_date = self.move_id.reversed_entry_id.date
#                        _logger.warning("------------IN SUBTOTAL REFUND RECOMPUTE: %s",force_date)
            rate = self.currency_id.with_context(date = force_date or self.move_id.date or fields.Date.today()).rate
        res = super(AccountMoveLine, self)._get_fields_onchange_subtotal(price_subtotal = price_subtotal, move_type = move_type, currency = currency, company = company, date= force_date or date)
        if rate > 0.0:
            currency_rate_inversion_line = 1/rate
            res['currency_rate_inversion_line'] = currency_rate_inversion_line
        return res

#    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids')
    def _tax_and_gross_line_amounts(self):
#        _logger.warning("------------IN TAX GROSS AMOUNTS")
        for record in self:
            if record.tax_ids:
                currency = record.currency_id or False
                price = record.price_unit * (1 - (record.discount or 0.0) / 100.0)
                taxes = record.tax_ids.compute_all(price, currency, record.quantity, product=record.product_id, partner=record.partner_id)
                record.update({'invoice_line_tax': taxes['total_included'] - taxes['total_excluded']})
#                record.update({'invoice_line_gross': taxes['total_included']})
            else:
                record.update({'invoice_line_tax': 0.0})
#                record.update({'invoice_line_gross': record.price_subtotal})

    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids')
    def _onchange_price_subtotal(self):
        super(AccountMoveLine, self)._onchange_price_subtotal()
        for line in self:
            if not line.move_id.is_invoice(include_receipts=True):
                continue
            line.update({
#                'invoice_line_gross': line.price_total,
                'invoice_line_tax' : line.price_total - line.price_subtotal
            })
#            line.update(line._get_fields_onchange_subtotal())

    def write(self, vals):
        # _logger.warning("------------IN WRITE: %s", vals)
        result = super(AccountMoveLine, self).write(vals)
        # _logger.warning("------------IN WRITE SUPER: %s", vals)
        for line in self:
            if not line.exclude_from_invoice_tab:
                to_write = line._get_price_total_and_subtotal()
                to_write.update(line._get_fields_onchange_subtotal(
                    price_subtotal=to_write['price_subtotal'],
                ))
#                _logger.warning("------------IN TO WRITE: %s", to_write)
                super(AccountMoveLine, line).write({
#                    'invoice_line_gross': to_write['price_total'],
                    'invoice_line_tax' : to_write['price_total'] - to_write['price_subtotal']
                })
#        vals['invoice_line_gross'] = vals['price_total']
        return result
