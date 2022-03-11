# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from math import fabs
from collections import OrderedDict
from xml.dom.minidom import Document
import re
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period, REVERSE_QUARTER_MAP

from openerp.addons.account_pl_cirrus.data.constant_values import *

from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class WizardVatUtils(models.TransientModel):
    _name='wizard.vat.utils'

    @api.model
    def check_company_data(self, wizard):
        company = wizard.company_id

        if not company.vat:
            raise UserError(_("Please define VAT number on the company!"))
        if not company.tax_office:
            raise UserError(_("Pusty Urzad Skarbowy IS/US. Wybierz urzad skarbowy w profilu twojej firmy"))
        if not company.tax_office.us_code:
            raise UserError(_("Pusty kod IS/US. Uzupelnij kod IS/US w twoim urzedzie skarbowym"))
        if company.regon_code == '-':
            raise UserError("Uzupełnij REGON w ustawieniach swojej firmy")
        # show possible error with wrong vat
        self.get_vat(company_id=company)

    @api.model
    def make_iban(self, wizard):
        #specific case only fot polish accounts

        prefix_code = wizard.company_id.partner_id.country_id.code
        raw_acc_number = wizard.journal_id.bank_account_id.sanitized_acc_number
        # _logger.warn(raw_acc_number)
        if not raw_acc_number:
            raise ValidationError(_('Please add account number to journal {}'.format(wizard.journal_id.name)))
        acc_num = raw_acc_number
        digits = re.findall(r'\d+', raw_acc_number)[0]
        if prefix_code == 'PL':
            if len(digits) == 26:
                # valid NRB has 26 digits
                acc_num = prefix_code + digits
                # TODO: sanity check of account number to confirm its integrity
        return acc_num


    @api.model
    def get_vat(self, company_id=False, partner_id=False):
        vat = company_id and company_id.vat or partner_id.vat
        vat = vat and vat.replace(' ', '') or False
        if company_id:
            if len(vat) == 10:
                return vat
            elif len(vat) == 12:
                return vat[2:]
            else:
                raise UserError(_("Wrong Vat no. of Your company. Please check it."))
        else:
            if not vat:
                if (not partner_id.property_account_position_id or partner_id.property_account_position_id.name in (u'Kraj', u'Wspólnota')) and partner_id.company_type == 'company':
                    raise UserError(_("Please add vat number of customer %s") %partner_id.name)
                else:
                    return False

            country_code = vat[:2]
            numeric_vat = vat[2:]
            if not country_code.isalpha():
                raise UserError(_("Please enter correct VAT number for partner {0} - is has to begin with country-specific characters.".format(partner_id.name)))
            else:
                return numeric_vat

    @api.model
    def get_vat_code(self, company_id=False, partner_id=False, skip_pl=False):
        vat = company_id and company_id.vat or partner_id.vat

        if not vat:
            return False
        if partner_id and partner_id.property_account_position_id and (partner_id.property_account_position_id.name[:14] == u'Import/Eksport'):
#           _logger.warning('--------------------VAT and Export    VAT: %s'%vat)
            return False
        code = vat[:2]
        if any(char.isdigit() for char in code):
            if skip_pl:
                return False
            return 'PL'
        else:
            if (code == 'PL' or code == 'pl') and skip_pl:
                return False
            return code

    @api.model
    def get_company_zip(self, wizard):
        company = wizard.company_id
        zip = company.zip
        if zip[:3] == 'PL-':
            return zip[3:]
        else:
            return zip


    def get_sale_part(self, lp, vat_dict):
        move_id = vat_dict['purchase_dict'][str(lp)]['move_id']
        if vat_dict['sale_dict']:
            for s_lp, sale_info in vat_dict['sale_dict'].items():
                if sale_info['move_id'] == move_id:
                    return vat_dict['sale_dict'][s_lp]['tax_values']
            return {}
        else:
            return {}


    @api.model
    def get_creation_date(self):
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        # return '2020-04-01T00:00:00Z'


    @api.model
    def get_first_name(self, company_id=False):
        if company_id:
            name = company_id.first_name
            if not name:
                raise ValidationError(_('For natural person declaration You must add First Name in company section.'))
            return name

    @api.model
    def get_surname(self, company_id=False):
        if company_id:
            surname = company_id.surname
            if not surname:
                raise ValidationError(_('For natural person declaration You must add Surname in company section.'))
            return surname

    @api.model
    def get_birth(self, company_id=False):
        if company_id:
            date = company_id.birth
            if not date:
                raise ValidationError(_('For natural person declaration You must add Birth Date in company section.'))
            return date


    @api.model
    def get_address(self, company_id=False, partner_id=False):
        address = company_id and company_id.partner_id.contact_address or partner_id.contact_address

        address = list(filter(lambda x: x and not x.isspace(), address.split('\n')))[1:]

        if not address:
            raise ValidationError(_('Please add address of {}'.format(company_id and company_id.name or partner_id.name)))

        return ', '.join(address)

    @api.model
    def get_cash_basis(self, wizard):
        return 'true' if wizard.cash_basis_pl else 'false'

    @api.model
    def prepare_line_value(self, inv, company_id, value, round=False, compute=False):
        if compute:
            # value = inv.currency_id.with_context(date=inv.invoice_date).compute(value, company_id.currency_id)
            value = inv.currency_id._convert(value, company_id.currency_id, company_id, inv.invoice_date)
        if round:
            value = company_id.currency_id.round(value)
        return value


    @api.model
    def convert_to_xml(self, structure, wizard, doc, data, parent=False, loop_key=False, inner_loop=False):
        for key, item in structure.items():
            if wizard._name == 'wizard.jpk.vat.2020':
                if key == 'Deklaracja':
                    if wizard.no_declaration_data:
                        continue
                if wizard.correction_number != 1:
                    if not wizard.correction_record and key == 'Ewidencja':
                        continue
                    if not wizard.correction_declaration and key == 'Deklaracja':
                        continue

            if isinstance(item, dict) and 'skip_empty' in item.keys():
                value = data
                for data_key in item['skip_empty']:
                    data_key = loop_key if data_key == 'loop_key' else data_key
                    value = value.get(data_key, {})
                if not value: return True

            if key == 'static_value':
                parent.appendChild(doc.createTextNode(item))
            elif key == 'value':
                if item == 'loop_index':
                    value = loop_key
                else:
                    value = data
                    for data_key in item:
                        data_key = loop_key if data_key == 'loop_key' else data_key
                        if isinstance(data_key, str) and 'INT' in data_key:
                            data_key = data_key[4:]
                            value = int(value.get(data_key, {}))
                        else:
                            if 'order_line' in item and data_key != 'order_line':
                                value = data['order_downpayment'][loop_key]['order_line'][inner_loop].get(data_key, {})
                            else:
                                value = value.get(data_key, {})

                    if isinstance(value, float):
                        value = '{0:.2f}'.format(value)
                    if not value and str(value).split('.')[0] != '0':
                        return True
 # suppress P_4B or P_5B - foreign VAT id in VAT_FA (not allowed by XSD)
                    if ('numeric_vat' in item) and (('seller_data' in item) or ('purchaser_data' in item)) and (len(value) != 10 or not value.isdigit()):
                        return True

                parent.appendChild(doc.createTextNode(str(value)))

            elif key == 'attrs':
                for name, value in item.items():
                    parent.setAttribute(name, value)

            elif key == 'wizard':
                if isinstance(item, list):
                    value = wizard
                    for field in item:
                        value = value[field]
                    text_node = doc.createTextNode(str(value))
                else:
                    text_node = doc.createTextNode(str(wizard[item]))
                parent.appendChild(text_node)

            elif key == 'wizard_function':
                text_node = doc.createTextNode(getattr(self, item)(wizard))
                parent.appendChild(text_node)

            elif key == 'function':
                text_node = doc.createTextNode(getattr(self, item)())
                parent.appendChild(text_node)

            # don't do anything after checking value
            elif key == 'skip_empty': pass

            elif 'value_loop' in item.keys():
                values = data
                for data_key in item['value_loop']:
                    data_key = loop_key if data_key == 'loop_key' else data_key
                    values = values.get(data_key, {})

                if item.get('no_order', False):
                    for name, value in OrderedDict(values.items()).items():# sorted method out, because VAT-7 (18)/VAT-7K (12) structures are not ordered
                        el = doc.createElement(name)
                        if item.get('force_int', False):
                            #el.appendChild(doc.createTextNode(str(int(value))))
                            if isinstance(value, str) == True:
                                el.appendChild(doc.createTextNode(value))
                            else:
                                el.appendChild(doc.createTextNode(str(int(value))))
                        else:
                            el.appendChild(doc.createTextNode('{0:.2f}'.format(value)))
                        parent.appendChild(el)
                else:
                    for name, value in OrderedDict(sorted(values.items())).items():
                        el = doc.createElement(name)
                        if item.get('force_int', False):
                            #el.appendChild(doc.createTextNode(str(int(value))))
                            if isinstance(value, str) == True:
                                el.appendChild(doc.createTextNode(value))
                            else:
                                el.appendChild(doc.createTextNode(str(int(value))))

                        else:
                            el.appendChild(doc.createTextNode('{0:.2f}'.format(value)))
                        parent.appendChild(el)

            elif 'loop' in item.keys():

                if isinstance(item['iterator'], list):
                    loop_values = data
                    for itm in item['iterator']:
                        loop_values = loop_values[itm]
                else:
                    loop_values = data[item['iterator']]
                for i in loop_values:
                    self.convert_to_xml(item['loop'], wizard, doc, data, parent=parent, loop_key=i)
                loop_key = False

            elif 'loop_2' in item.keys():
                loop_values = data['order_downpayment'][loop_key]['order_line']
                for i in loop_values:
                    self.convert_to_xml(item['loop_2'], wizard, doc, data, parent=parent, loop_key=loop_key, inner_loop=i)
                loop_key = False

            else:
                if key == 'OsobaFizyczna' and wizard.company_id.natural_person == False:
                    continue
                elif key == 'OsobaNiefizyczna' and wizard.company_id.natural_person == True:
                    continue
                element = doc.createElement(key)
                if not self.convert_to_xml(item, wizard, doc, data, parent=element, loop_key=loop_key, inner_loop=inner_loop) and parent:
                    if not (element.tagName in ["SprzedazCtrl","ZakupCtrl","ZamowienieCtrl"]) or element.hasChildNodes():
                        parent.appendChild(element)
                #zlecenia
                elif element.tagName in ['P_7Z', 'P_8AZ', 'P_8BZ', 'P_9AZ', 'P_11NettoZ', 'P_11VatZ', 'P_12Z']:
                    parent.appendChild(element)

            if not parent:
                return element

    @api.model
    def get_vat_details(self, wizard, filter_journals=False, cash_basis=False, natural_person=False, different_period_items=False):
        AccountMove = self.env['account.move']
        moves = AccountMove
        company_id = wizard.company_id
        if wizard._name == 'wizard.jpk.vat.2020':
            purchase_taxes = TAXES_PURCHASE_VDEK_1
        else:
            purchase_taxes = TAXES_PURCHASE
        company_data = {
        'name': company_id.name,
        'email': company_id.email,
        'address': self.get_address(company_id=company_id),
        'country_code': self.get_vat_code(company_id=company_id),
        'numeric_vat': self.get_vat(company_id=company_id),
        }

        if natural_person:
            company_data['first_name'] = self.get_first_name(company_id=company_id)
            company_data['surname'] = self.get_surname(company_id=company_id)
            company_data['birth_date'] = self.get_birth(company_id=company_id)

        if wizard.date_from.month != wizard.date_to.month:
            company_data['quarter'] = REVERSE_QUARTER_MAP[wizard.date_from.month]
            if wizard._name == 'wizard.jpk.vat.2020':
                company_data['month'] = wizard.date_to.month
        else:
            company_data['month'] = wizard.date_from.month
        company_data['year'] = wizard.date_from.year

        if cash_basis:
            home_currency_id = company_id.currency_id
            payments = self.env['account.payment'].search([('payment_date', '>=', wizard.date_from), ('payment_date', '<=', wizard.date_to), ('payment_type', '!=', 'transfer')])
            move_payment_dict = {}
            for payment in payments.filtered(lambda r: not r.partner_id.property_account_position_id.name or r.partner_id.property_account_position_id.name == 'Kraj'):
                move_line_ids = payment.move_line_ids
                payment_move = move_line_ids.mapped('move_id')
                payment_move.ensure_one()

                partial_reconcile_ids = move_line_ids.mapped('matched_debit_ids') + move_line_ids.mapped('matched_credit_ids')
                move_lines = (partial_reconcile_ids.mapped('debit_move_id') + partial_reconcile_ids.mapped('credit_move_id')).filtered(lambda r: r not in move_line_ids)

                move = move_lines.mapped('move_id').filtered(lambda r: r.state == 'posted' and len(r.line_ids.mapped('tax_line_id') + r.line_ids.mapped('tax_ids')) > 0)

                if not move: continue
                elif len(move) == 1:
                    # move.ensure_one()
                    if home_currency_id in move.line_ids.mapped('currency_id') or not move.line_ids.mapped('currency_id'):
                        partial_payment = payment_move.amount / move.amount
                    else:
                        amount_move = max(move.line_ids.mapped(lambda r: fabs(r.amount_currency)))
                        amount_payment = max(payment_move.line_ids.mapped(lambda r: fabs(r.amount_currency)))
                        partial_payment = amount_payment / amount_move
                    # payment date is not predicted in JPK or other documents yet
                    if move.id not in move_payment_dict:
                        move_payment_dict[move.id] = {'partial_payment': partial_payment, 'date': payment.payment_date }
                    else:
                        move_payment_dict[move.id]['partial_payment'] += partial_payment
                        move_payment_dict[move.id]['date'] = max(move_payment_dict[move.id]['date'], payment.payment_date)

                    if move not in moves:
                        moves += move
                else:
                    for m in move:
                        move_line = m.line_ids.filtered(lambda l: fabs(l.balance) == max(m.line_ids.mapped(lambda k: fabs(k.balance))))
                        payment_lines=[]
                        payment_lines = move_line_ids.mapped('matched_debit_ids').filtered(lambda p: p.debit_move_id == move_line).mapped('credit_move_id')
                        if not payment_lines:
                            payment_lines = move_line_ids.mapped('matched_credit_ids').filtered(lambda p: p.credit_move_id == move_line).mapped('debit_move_id')
                        if home_currency_id in m.line_ids.mapped('currency_id') or not m.line_ids.mapped('currency_id'):
                            partial_payment = sum(payment_lines.mapped(lambda t: fabs(t.balance))) / fabs(m.amount)
                        else:
                            amount_move = max(m.line_ids.mapped(lambda r: fabs(r.amount_currency)))
                            amount_payment = sum(payment_lines.mapped(lambda r: fabs(r.amount_currency)))
                            partial_payment = amount_payment / amount_move
# instead of            partial_payment = (m.amount - fabs(max(m.line_ids.mapped('amount_residual')))) / m.amount
                        if m.id not in move_payment_dict:
                            move_payment_dict[m.id] = {'partial_payment': partial_payment, 'date': payment.payment_date }
                        else:
                            move_payment_dict[m.id]['partial_payment'] += partial_payment
                            move_payment_dict[m.id]['date'] = max(move_payment_dict[m.id]['date'], payment.payment_date)
                        if m not in moves:
                            moves += m

            other_moves = AccountMove.search([
                ['company_id', '=', company_id.id],
                '&','|', '&', ('tax_date', '>=', wizard.date_from), ('tax_date', '<=', wizard.date_to), '&', '&',
                ('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to), ('tax_date', '=', False), ('state', '=','posted')
                ]).filtered(lambda r: r.partner_id.property_account_position_id.name in ('Wspólnota', 'Import/Eksport') or \
                (not r.partner_id.property_account_position_id or r.partner_id.property_account_position_id.name == 'Kraj') and \
                ((r.line_ids.mapped('tax_line_id') or r.line_ids.mapped('tax_ids')) and (not r.line_ids.mapped('invoice_id') or \
                (any(move_type in ['in_refund','out_refund'] for move_type in r.line_ids.mapped('invoice_id.move_type'))))))
# or r.line_ids.mapped('invoice_id.refund_invoice_ids')))

            for m in other_moves:
                if m not in moves:
                    moves += m

            moves = moves.sorted(lambda r: move_payment_dict.get(r.id,{}).get('date', False) or r.tax_date or r.date)
        else:
            moves = AccountMove.search([
                ['company_id', '=', company_id.id],
                '&', '|', '&', ('tax_date', '>=', wizard.date_from), ('tax_date', '<=', wizard.date_to), '&', '&',
                ('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to), ('tax_date', '=', False),
                ('state', '=', 'posted')
            ])

            manual_move_lines = self.env['account.move.line'].search([('company_id', '=', company_id.id),
                                                                ('date_manual', '>=', wizard.date_from),
                                                                ('date_manual', '<=', wizard.date_to),
                                                                ])

            manual_move_ids = [move.move_id.id for move in manual_move_lines]
            manual_date_moves = AccountMove.search([('id', 'in', manual_move_ids), ('state', '=','posted')])
            for move in manual_date_moves:
                if move.id not in moves.ids:
                    moves += manual_date_moves
            moves = moves.sorted(lambda r: r.tax_date or r.date)


        if different_period_items:
            moves = AccountMove.search([
                ['company_id', '=', company_id.id],
                '|', ('tax_date', '<', wizard.date_from), ('tax_date', '>', wizard.date_to),
                ('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to), ('state', '=','posted')
                ])
            manual_move_lines = self.env['account.move.line'].search([('company_id', '=', company_id.id),
                                                                '|', ('date_manual', '<=', wizard.date_from) ,('date_manual', '>=', wizard.date_to),
                                                                ('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to),
                                                                ])

            manual_move_ids = [move.move_id.id for move in manual_move_lines]
            manual_date_moves = AccountMove.search([('id', 'in', manual_move_ids), ('state', '=','posted')])
            for move in manual_date_moves:
                if move.id not in moves.ids:
                    moves += manual_date_moves
            moves = moves.sorted(lambda r: r.tax_date or r.date)

        # invoice register
        if filter_journals:
            moves = moves.filtered(lambda r: r.journal_id in filter_journals)

        # NOTE: takes all moves and choses those with sale taxes inside
        sale_move_ids = moves.filtered(lambda x: any(tax in TAXES_SALE.keys() for tax in x.line_ids.mapped('tax_ids.tag_id.name')) or any(tax in TAXES_SALE.keys() for tax in x.line_ids.mapped('tax_line_id.tag_id.name')))
        _logger.warning('==  MOVES   :   '+str(len(moves)))
        _logger.warning('==  SALE MOVES   :   '+str(len(sale_move_ids)))
        sum_sale_taxes = 0.0
        sum_sale_base = 0.0
        sum_invoice_line = 0.0
        order_sum = 0.0
        lp = 0
        fa_lp = 0
        order_lp = 0
        sale_dict = {}
        order_downpayment = {}
        taxes_sum_dict = {}
        sale_ctrl = {}
        order_ctrl = {}
        invoice_line_dict = {}
        invoice_line_ctrl = {}
        ue_dict = {'UE_C': {}, 'UE_D': {}, 'UE_E': {}}
        taxes_check_sum = {}
        for move in sale_move_ids:
            different_month = []
            this_month = []
            different_dates_lines = [move_line for move_line in move.line_ids if move_line.date_manual != False]
            if different_dates_lines:
                for line in different_dates_lines:
                    base_tax = self.env['account.tax'].search([('children_tax_ids', 'in', line.tax_line_id.id)])
                    net_lines = [move_line.id for move_line in move.line_ids if base_tax.id in move_line.tax_ids.ids]
                    if not base_tax or not net_lines:
                        net_lines = [move_line.id for move_line in move.line_ids if line.tax_line_id.id in move_line.tax_ids.ids]

                    if line.date_manual < wizard.date_from or line.date_manual > wizard.date_to:
                        different_month.append(line.id)
                        different_month.extend(net_lines)
                    else:
                        this_month.append(line.id)
                        this_month.extend(net_lines)
            partner_id = move.line_ids.mapped('partner_id')
            if len(partner_id) > 1:
                partners = [line.partner_id for line in move.line_ids if line.tax_line_id]
                if partners:
                    partner_id = partners[0]
                else:
                    raise UserError(_('Journal Entry %s has incorrect setted partners.')% move.name)
            elif not partner_id:
                if not move.custom_partner_id:
                    raise UserError(_('Please add partner to %s Journal Entry')% move.name)
                else:
                    partner_id = move.custom_partner_id
            sale_partner_vat = 'brak'
            if partner_id.vat:
                if partner_id.vat[:2] == 'PL':
                    sale_partner_vat = partner_id.vat[2:]
                else:
                    sale_partner_vat = partner_id.vat

            partner_data = {
                'name': partner_id.name,
                'address': self.get_address(partner_id=partner_id),
                'country_code': self.get_vat_code(partner_id=partner_id, skip_pl=True),
                'numeric_vat': self.get_vat(partner_id=partner_id) or 'brak',
                'vat': self.get_vat(partner_id=partner_id) and sale_partner_vat or 'brak', # if no numeric vat the vat = false because country out of EU
            }




            display_date = move.tax_date or move.date
            date_issue = move.date_issue or display_date
            sale_date = display_date if date_issue and date_issue != display_date else False

            invoice_reference = move.name
            # inv = move.line_ids.mapped('invoice_id')
            inv = move

            if move.journal_id.type == 'purchase':
                partner_reference = inv and inv.ref or False
                main_reference = partner_reference or invoice_reference
            else:
                partner_reference = inv and inv.name or False
                main_reference = invoice_reference

            # JPK FA
            invoice_type = False
            refund_reason = False
            refunded_inv_number = False
            refunded_period = False
            down_payment_value = False
            down_payment_tax = False
            invoice_cash_basis = 'false'
            reverse_charge = 'false'
            amount_total = 0.0

            # better filtering of deposit prod.
            # compute discounts
            if inv:
                inv = inv[0]
                deposit_product_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id'))
                deposit_line = inv.invoice_line_ids.filtered(lambda r: r.product_id.id == deposit_product_id)
                negative_deposit_line  = deposit_line if deposit_line and sum(deposit_line.mapped('price_subtotal')) < 0 else False

                if inv.reversed_entry_id:
                    refund_inv_id = inv.reversed_entry_id
                    invoice_type = 'KOREKTA'
                    refund_reason = inv.name
                    refunded_inv_number = refund_inv_id.name
                    # OKRES FAKTURY KORYGOWANEJ????
                    refunded_period = (refund_inv_id.date_issue if refund_inv_id.date_issue else refund_inv_id.invoice_date).strftime('%m.%Y')

                elif deposit_line and not negative_deposit_line:
                    invoice_type = 'ZAL'
                    down_payment_value = inv.amount_total_signed
                    # down_payment_tax = inv.amount_tax
                    down_payment_tax = self.prepare_line_value(inv, company_id, inv.amount_tax, True, True)

                    sale_order_line = inv.invoice_line_ids.mapped('sale_line_ids')
                    if sale_order_line:
                        sale_order = sale_order_line[0].order_id
                        order_line_dict = {}
                        order_line_lp = 0
                        order_lp += 1
                        for order_line in sale_order.order_line:
                            if order_line.product_id.id == deposit_product_id:
                                continue
                            else:
                                order_line_lp += 1
                                order_line_dict[order_line_lp] = {
                                    'product': order_line.product_id.name,
                                    'uom': order_line.product_uom.name,
                                    'qty': order_line.product_uom_qty,
                                    'price_unit': order_line.price_unit,
                                    'price_subtotal': order_line.price_subtotal,
                                    'tax': order_line.price_tax,
                                    'tax_group': TAXES_INV_LINE[order_line.tax_ids.tag_id.name]
                                }

                        order_sum += sale_order.amount_total

                        if sale_order:
                            order_downpayment[order_lp] = {
                                'main_reference': main_reference,
                                'order_total': sale_order.amount_total,
                                'order_line': order_line_dict
                            }

                else:
                    invoice_type = 'VAT'

                down_payment_discount = 0
                if negative_deposit_line:
                    dp = self.prepare_line_value(inv, company_id, abs(sum(negative_deposit_line.mapped('price_total'))), compute=True)
                    down_payment_discount = dp / (inv.amount_total_signed + dp)

                amount_total = inv.amount_total_signed

                for line in inv.invoice_line_ids.filtered(lambda r : (r not in (negative_deposit_line or [])) and (r.display_type == False)):
                    fa_lp += 1
                    sum_invoice_line += line.price_subtotal

                    # unit_gross = line.price_unit
                    price_unit = self.prepare_line_value(inv, company_id, line.price_unit - line.price_unit * down_payment_discount, True, True)
                    unit_gross = self.prepare_line_value(inv, company_id, line.price_unit - line.price_unit * down_payment_discount, True, True)

                    if line.tax_ids:
                        unit_taxes = line.tax_ids.compute_all(line.price_unit, inv.currency_id, 1, product=line.product_id, partner=partner_id)
                        # unit_gross = unit_taxes['total_included']
                        unit_taxes_value = unit_taxes['total_included']
                        unit_gross = self.prepare_line_value(inv, company_id, unit_taxes_value - unit_taxes_value * down_payment_discount, True, True)

                    discount = self.prepare_line_value(inv, company_id, (line.price_unit * line.quantity) * ((line.discount/100) + down_payment_discount), True, True)
                    subtotal = self.prepare_line_value(inv, company_id, line.price_subtotal - line.price_subtotal * down_payment_discount, round=True)
                    gross = self.prepare_line_value(inv, company_id, line.price_total - line.price_total * down_payment_discount, True, True)
                    # FIXME CORRECT VALUES FOR CREDIT NOTES (-)
                    # TODO: CHECK for any discounts in multiple units
                    invoice_line_dict[fa_lp] = {
                        'invoice_reference': main_reference,
                        'name': line.name,
                        'uom': line.product_uom_id.name,
                        'qty': line.quantity,
                        # 'price_unit': line.price_unit,
                        'price_unit': price_unit,
                        'unit_gross': unit_gross,
                        'subtotal': subtotal,
                        # 'gross': line.price_total,
                        'discount': discount,
                        'gross': gross,
                        'tax_group': TAXES_INV_LINE[line.tax_ids.tag_id.name],
                    }

                seller_data = company_data.copy() if inv.move_type in ['out_invoice', 'out_refund'] else partner_data.copy()
                purchaser_data = partner_data.copy() if inv.move_type in ['out_invoice', 'out_refund'] else company_data.copy()

                if (not partner_id.property_account_position_id or partner_id.property_account_position_id.name == 'Kraj') and inv.move_type in ['out_invoice', 'out_refund'] and cash_basis:
                    invoice_cash_basis = 'true'
                if any([tax in REVERSE_CHARGE_TAXES for tax in inv.invoice_line_ids.mapped('tax_ids.tag_id.name')]):
                    reverse_charge = 'true'

            else:
                seller_data = company_data.copy()
                purchaser_data = partner_data.copy()

            move_taxes = {}
            tax_values = {}
            expected_taxes = []
            product_tax_markers = {}
            procedures_markers = {}
            doc_type_vdek = False
            if inv:
                if inv.split_payment_method:
                    procedures_markers['MPP'] = 1
                if inv.sw:
                    procedures_markers['SW'] = 1
                if inv.ee:
                    procedures_markers['EE'] = 1
                if inv.tp:
                    procedures_markers['TP'] = 1
                if inv.tt_wnt:
                    procedures_markers['TT_WNT'] = 1
                if inv.tt_d:
                    procedures_markers['TT_D'] = 1
                if inv.mr_t:
                    procedures_markers['MR_T'] = 1
                if inv.mr_uz:
                    procedures_markers['MR_UZ'] = 1
                if inv.i_42:
                    procedures_markers['I_42'] = 1
                if inv.i_63:
                    procedures_markers['I_63'] = 1
                if inv.b_spv:
                    procedures_markers['B_SPV'] = 1
                if inv.b_spv_dostawa:
                    procedures_markers['B_SPV_DOSTAWA'] = 1
                if inv.b_mpv_prowizja:
                    procedures_markers['B_MPV_PROWIZJA'] = 1
                if inv.doc_type_vdek:
                    doc_type_vdek = inv.doc_type_vdek

            for move_line in move.line_ids:
                skip_month = False

                if move_line.product_id.product_tmpl_id.get_tax_marker():
                    marker = move_line.product_id.product_tmpl_id.get_tax_marker()
                    product_tax_markers[marker.name] = 1


                if move_line.id in different_month or move_line.id in this_month:
                    if move_line.id in different_month:
                        continue
                else:
                    if different_period_items:
                        if not move_line.date_manual:
                            if not move.tax_date:
                                continue
                            elif move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                                continue
                        else:
                            if not (move_line.date_manual < wizard.date_from or move_line.date_manual > wizard.date_to):
                                continue
                    else:
                        #jeżeli date_manual jest z innego miesiąca
                        if move_line.date_manual:
                            if not (move_line.date_manual >= wizard.date_from and move_line.date_manual <= wizard.date_to):
                                continue
                        #jeżeli data jest z innego miesiaca
                        else:
                            if move.date < wizard.date_from or move.date > wizard.date_to:
                                #i nie ma date_manual i tax_date
                                if not move_line.date_manual and not move.tax_date:
                                    continue
                                if move.tax_date:
                                    #i tax_date jest z innego miesiąca
                                    if not (move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to):
                                        continue
                            #jeżeli data jest z tego miesiąca
                            if move.date >= wizard.date_from and move.date <= wizard.date_to:
                                # i nie ma date manual a tax_date jest z innego miesiąca
                                if move.tax_date and not move_line.date_manual:
                                    if not (move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to):
                                        continue

                if wizard._name == 'wizard.jpk.vat.2020' and (wizard.date_from.month != wizard.date_to.month and wizard.period != 1) and wizard.no_declaration_data == False:
                    if move_line.date_manual:
                        if not (move_line.date_manual.month == wizard.date_to.month):
                            skip_month = True
                    else:
                        if move.tax_date:
                            if not (move.tax_date.month == wizard.date_to.month):
                                skip_month = True
                        else:
                            if not (move.date.month == wizard.date_to.month):
                                skip_month = True

                netto_name = move_line.tax_ids.tag_id.name
                tax_name = move_line.tax_line_id.tag_id.name
                tax_value = move_line.tax_value

                control_tax_name = False
                control_netto_name = False

                if tax_value != 0:
                    credit = fabs(tax_value) if tax_value < 0 else 0.0
                    debit = tax_value if tax_value > 0 else 0.0
                else:
                    credit = move_line.credit
                    debit = move_line.debit

                if cash_basis and move_payment_dict.get(move.id, False):
                    credit = move_payment_dict[move.id]['partial_payment'] * credit
                    debit = move_payment_dict[move.id]['partial_payment'] * debit


                if move_line.tax_basic_custom > 0.0:
                    control_netto_name = TAXES_SALE[tax_name][0]
                    if len(TAXES_SALE[tax_name]) > 1:
                        control_tax_name = TAXES_SALE[tax_name][1]
                    if move.ref:
                        main_reference = move.ref
                    debit_custom_value = 0.0
                    credit_custom_value = move_line.tax_basic_custom
                    if control_netto_name not in move_taxes.keys():
                        move_taxes[control_netto_name] = {'credit': float("{0:.2f}".format(credit_custom_value)),
                                                               'debit' : float("{0:.2f}".format(debit_custom_value))}
                    else:
                        move_taxes[control_netto_name]['credit'] += float("{0:.2f}".format(credit_custom_value))
                        move_taxes[control_netto_name]['debit'] += float("{0:.2f}".format(debit_custom_value))
                    if not skip_month:
                        sum_sale_taxes += float("{0:.2f}".format(credit_custom_value))

                else:
                    if netto_name in TAXES_SALE.keys():

                        control_netto_name = TAXES_SALE[netto_name][0]
                        if len(TAXES_SALE[netto_name]) > 1:
                            control_tax_name = TAXES_SALE[netto_name][1]

                        if control_netto_name not in move_taxes.keys():
                            move_taxes[control_netto_name] = {'credit': float("{0:.2f}".format(credit)),
                                                                     'debit' : float("{0:.2f}".format(debit))}
                        else:
                            move_taxes[control_netto_name]['credit'] += float("{0:.2f}".format(credit))
                            move_taxes[control_netto_name]['debit'] += float("{0:.2f}".format(debit))

                        if netto_name == 'WSU':
                            if 'K_12' not in move_taxes.keys():
                                move_taxes['K_12'] = {'credit': float("{0:.2f}".format(credit)),
                                                      'debit':  float("{0:.2f}".format(debit))}
                            else:
                                move_taxes['K_12']['credit'] += float("{0:.2f}".format(credit))
                                move_taxes['K_12']['debit'] += float("{0:.2f}".format(debit))

                            if 'K_12' not in expected_taxes:
                                expected_taxes.append('K_12')

                        # invoice register
                        if not skip_month:
                            if move.journal_id.type == 'purchase':
                                sum_sale_base += float("{0:.2f}".format(debit)) - float("{0:.2f}".format(credit))
                            else:
                                sum_sale_base += float("{0:.2f}".format(credit)) - float("{0:.2f}".format(debit))

                    # both sale and purchase are in sale part. No need to get WNT value from purchase part
                    if netto_name in TAXES_UE.keys():
                        ue_name = TAXES_UE[netto_name]
                        if partner_data['vat'] not in ue_dict[ue_name]:
                            ue_dict[ue_name][partner_data['vat']] = {'country_code': partner_data['country_code'], 'vat': partner_data['numeric_vat'], 'amount': 0.0}

                        if netto_name in TAXES_UE_SALE:
                            ue_dict[ue_name][partner_data['vat']]['amount'] += credit - debit
                        else:
                            ue_dict[ue_name][partner_data['vat']]['amount'] += debit - credit
                if tax_name in TAXES_SALE.keys():
                    control_netto_name = TAXES_SALE[tax_name][0]
                    if len(TAXES_SALE[tax_name]) > 1:
                        control_tax_name = TAXES_SALE[tax_name][1]

                    if tax_name == 'VWEW' and move.customs:
                        if move.ref:
                            main_reference = move.ref
                        debit_vwew = 0.0
                        credit_vwew = move.customs
                        if control_netto_name not in move_taxes.keys():
                            move_taxes[control_netto_name] = {'credit': float("{0:.2f}".format(credit_vwew)),
                                                                   'debit' : float("{0:.2f}".format(debit_vwew))}
                        else:
                            move_taxes[control_netto_name]['credit'] += float("{0:.2f}".format(credit_vwew))
                            move_taxes[control_netto_name]['debit'] += float("{0:.2f}".format(debit_vwew))
                        if not skip_month:
                            sum_sale_taxes += float("{0:.2f}".format(credit_vwew))


                    if control_tax_name not in move_taxes.keys():
                        move_taxes[control_tax_name] = {'credit': float("{0:.2f}".format(credit)),
                                                               'debit' : float("{0:.2f}".format(debit))}
                    else:
                        move_taxes[control_tax_name]['credit'] += float("{0:.2f}".format(credit))
                        move_taxes[control_tax_name]['debit'] += float("{0:.2f}".format(debit))
                    if not skip_month:
                        sum_sale_taxes += float("{0:.2f}".format(credit)) - float("{0:.2f}".format(debit))

                if control_netto_name and control_netto_name not in expected_taxes:
                    expected_taxes.append(control_netto_name)
                if control_tax_name and control_tax_name not in expected_taxes:
                    expected_taxes.append(control_tax_name)

            taxes_check = move_taxes.keys()
            if len(expected_taxes) != len(taxes_check) or len(set(expected_taxes) - set(taxes_check)) > 0:
                raise UserError(_("Error ocured while JPK taxes validation. Please correct taxes in Journal Entry %s") %move.name)

            sorted_move_taxes = OrderedDict(sorted(move_taxes.items()))
            value_check = False
            for tax_name, amount in sorted_move_taxes.items():
                if amount['credit'] != 0 or amount['debit'] != 0:
                    # purchase taxes in sale part
                    if tax_name in ['K_23', 'K_25','K_27', 'K_29', 'K_34']:
                        value = amount['debit'] - amount['credit']
                    else:
                        value = amount['credit'] - amount['debit']
                    if not skip_month:
                        if not value_check and value != 0:
                            value_check = True

                    # JPK
                    tax_values[tax_name] = float("{0:.2f}".format(value))
                    if not skip_month:
                        if taxes_check_sum.get(tax_name):
                            taxes_check_sum[tax_name] += float("{0:.2f}".format(value))
                        else:
                            taxes_check_sum[tax_name] = float("{0:.2f}".format(value))
                    # VAT documents
                    report_tax_name = tax_name.replace('K', 'P')
                    if report_tax_name not in taxes_sum_dict.keys():
                        taxes_sum_dict[report_tax_name] = value
                    else:
                        taxes_sum_dict[report_tax_name] += value
                else:
                    tax_values[tax_name] = 0


            product_tax_markers = OrderedDict(sorted(product_tax_markers.items()))

            if value_check:
                lp += 1
                sale_dict[lp] = {
                    'partner_data': partner_data.copy(),
                    'seller_data': seller_data.copy(),
                    'purchaser_data': purchaser_data.copy(),
                    'tax_values': tax_values.copy(),
                    'product_tax_markers' : product_tax_markers.copy(),
                    'procedures_markers' : procedures_markers.copy(),

                    'display_date': display_date,
                    'date_issue': date_issue,
                    'sale_date': sale_date,
                    'original_move_date': move.date,

                    'main_reference': main_reference,
                    'invoice_reference': invoice_reference,
                    'partner_reference': partner_reference,
                    'invoice_type': invoice_type,

                    'refund_reason': refund_reason,
                    'refunded_inv_number': refunded_inv_number,
                    'refunded_period': refunded_period,

                    'down_payment_value': down_payment_value,
                    'down_payment_tax': down_payment_tax,
                    'amount_total': amount_total,

                    'cash_basis': invoice_cash_basis,
                    'reverse_charge': reverse_charge,

                    'sale_type': inv.wew,
                    'move_id': move.id,
                    'doc_type_vdek': inv.doc_type_vdek,
                }
        if lp > 0:
            sale_ctrl = {
                'lp': lp,
                'sum_taxes': float("{0:.2f}".format(sum_sale_taxes)),
                'sum_base': float("{0:.2f}".format(sum_sale_base)),
                'sum_all': float("{0:.2f}".format(sum_sale_taxes + sum_sale_base)),
                'taxes_check_sum': taxes_check_sum,
            }

        else:
            if wizard._name == 'wizard.jpk.vat.2020':
                sale_ctrl = {
                    'lp': 0,
                    'sum_taxes': 0,
                    'sum_base': 0,
                    'sum_all': 0,
                    'taxes_check_sum': 0
                    }

        if fa_lp > 0:
            invoice_line_ctrl = {
                'lp': fa_lp,
                'sum_invoice_line': sum_invoice_line,
            }

        if order_lp > 0:
            order_ctrl = {
                'lp' : order_lp,
                'order_sum' : order_sum
            }

        sum_purchase_base = 0.0
        sum_purchase_taxes = 0.0
        lp = 0
        purchase_dict = {}
        purchase_ctrl = {}

        purchas_move_ids = moves.filtered(lambda x: any(tax in purchase_taxes.keys() for tax in x.line_ids.mapped('tax_ids.tag_id.name')) or any(tax in purchase_taxes.keys() for tax in x.line_ids.mapped('tax_line_id.tag_id.name')))
        for move in purchas_move_ids:
            partner_id = move.line_ids.mapped('partner_id')
            if len(partner_id) > 1:
                partners = [line.partner_id for line in move.line_ids if line.tax_line_id]
                if partners:
                    partner_id = partners[0]
                else:
                    raise UserError(_('Journal Entry %s has incorrect setted partners.')% move.name)
            elif not partner_id:
                if not move.custom_partner_id:
                    raise UserError(_('Please add partner to %s Journal Entry')% move.name)
                else:
                    partner_id = move.custom_partner_id


            if partner_id.vat:
                if partner_id.vat[:2] == 'PL':
                    partner_vat = partner_id.vat[2:]
                else:
                    partner_vat = partner_id.vat
            else:
                partner_vat = None
            if not partner_vat:
                if (not partner_id.property_account_position_id or partner_id.property_account_position_id.name in (u'Kraj', u'Wspólnota')) and partner_id.company_type == 'company':
                    raise UserError(_("Please define Vat no. for vendor %s.")% partner_id.name)
                else:
                    partner_vat = 'brak'

            partner_country_code = self.get_vat_code(partner_id=partner_id, skip_pl=True)
            numeric_vat = self.get_vat(partner_id=partner_id) or 'brak'
            address = ''

            if partner_id.street: address += partner_id.street + ' '
            if partner_id.street2: address += partner_id.street2 + ' '
            if partner_id.zip: address += partner_id.zip + ' '
            if partner_id.city: address += partner_id.city

            if not address:
                raise UserError(_("Please add address of %s vendor.")% partner_id.name)

            inv = move
            invoice_reference = move.name
            partner_reference = inv and inv.ref or False
            main_reference = partner_reference or invoice_reference

            purchase_date = move.tax_date or move.date
            date_issue = move.date_issue

            move_taxes = {}
            tax_values = {}

            procedures_markers = {}
            date_recived = False
            purchase_doc_vdek = False
            if inv:
                if inv.split_payment_method:
                    procedures_markers['MPP'] = 1
                if inv.sw:
                    procedures_markers['SW'] = 1
                if inv.ee:
                    procedures_markers['EE'] = 1
                if inv.tp:
                    procedures_markers['TP'] = 1
                if inv.tt_wnt:
                    procedures_markers['TT_WNT'] = 1
                if inv.tt_d:
                    procedures_markers['TT_D'] = 1
                if inv.mr_t:
                    procedures_markers['MR_T'] = 1
                if inv.mr_uz:
                    procedures_markers['MR_UZ'] = 1
                if inv.i_42:
                    procedures_markers['I_42'] = 1
                if inv.i_63:
                    procedures_markers['I_63'] = 1
                if inv.b_spv:
                    procedures_markers['B_SPV'] = 1
                if inv.b_spv_dostawa:
                    procedures_markers['B_SPV_DOSTAWA'] = 1
                if inv.b_mpv_prowizja:
                    procedures_markers['B_MPV_PROWIZJA'] = 1
                if inv.imp:
                    procedures_markers['IMP'] = 1
                if inv.date_recived:
                    date_recived = inv.date_recived
                if inv.purchase_doc_vdek:
                    purchase_doc_vdek = inv.purchase_doc_vdek

            for move_line in move.line_ids:
                skip_month = False
                if different_period_items:
                    if not move_line.date_manual:
                        if not move.tax_date:
                            continue
                        elif move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                            continue
                    else:
                        if not (move_line.date_manual < wizard.date_from or move_line.date_manual > wizard.date_to):
                            continue
                else:
                    #jeżeli date_manual jest z innego miesiąca
                    if move_line.date_manual:
                        if not (move_line.date_manual >= wizard.date_from and move_line.date_manual <= wizard.date_to):
                            continue
                    #jeżeli data jest z innego miesiaca
                    else:
                        if move.date < wizard.date_from or move.date > wizard.date_to:
                            #i nie ma date_manual i tax_date
                            if not move_line.date_manual and not move.tax_date:
                                continue
                            if move.tax_date:
                                #i tax_date jest z innego miesiąca
                                if not (move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to):
                                    continue
                        #jeżeli data jest z tego miesiąca
                        if move.date >= wizard.date_from and move.date <= wizard.date_to:
                            # i nie ma date manual a tax_date jest z innego miesiąca
                            if move.tax_date and not move_line.date_manual:
                                if not (move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to):
                                    continue

                if wizard._name == 'wizard.jpk.vat.2020' and (wizard.date_from.month != wizard.date_to.month and wizard.period != 1) and wizard.no_declaration_data == False:
                    if move_line.date_manual:
                        if not (move_line.date_manual.month == wizard.date_to.month):
                            skip_month = True
                    else:
                        if move.tax_date:
                            if not (move.tax_date.month == wizard.date_to.month):
                                skip_month = True
                        else:
                            if not (move.date.month == wizard.date_to.month):
                                skip_month = True

                netto_name = move_line.tax_ids.tag_id.name
                tax_name = move_line.tax_line_id.tag_id.name
                tax_value = move_line.tax_value

                if tax_value != 0:
                    credit = fabs(tax_value) if tax_value < 0 else 0.0
                    debit = tax_value if tax_value > 0 else 0.0
                else:
                    credit = move_line.credit
                    debit = move_line.debit

                if cash_basis and move_payment_dict.get(move.id, False):
                    credit = move_payment_dict[move.id]['partial_payment'] * credit
                    debit = move_payment_dict[move.id]['partial_payment'] * debit

                if netto_name == 'ZLP':
                    credit = round(credit/2.0, 2)
                    debit = round(debit/2.0, 2)
                if move_line.tax_basic_custom > 0.0:
                    if move.ref:
                        main_reference = move.ref
                    netto_name_custom = move_line.tax_line_id.tag_id.name
                    debit_custom_value = move_line.tax_basic_custom
                    credit_custom_value = 0
                    if purchase_taxes[netto_name_custom][0] not in move_taxes.keys():
                        move_taxes[purchase_taxes[netto_name_custom][0]] = {'debit': float("{0:.2f}".format(debit_custom_value)),
                                                                         'credit':float("{0:.2f}".format(credit_custom_value))}
                    else:
                        move_taxes[purchase_taxes[netto_name_custom][0]]['debit'] += float("{0:.2f}".format(debit_custom_value))
                        move_taxes[purchase_taxes[netto_name_custom][0]]['credit'] += float("{0:.2f}".format(credit_custom_value))
                    if not skip_month:
                        sum_purchase_base += float("{0:.2f}".format(debit_custom_value))
                else:
                    if netto_name in purchase_taxes.keys():
                        if purchase_taxes[netto_name][0] not in move_taxes.keys():
                            move_taxes[purchase_taxes[netto_name][0]] = {'debit': float("{0:.2f}".format(debit)),
                                                                         'credit':float("{0:.2f}".format(credit))}
                        else:
                            move_taxes[purchase_taxes[netto_name][0]]['debit'] += float("{0:.2f}".format(debit))
                            move_taxes[purchase_taxes[netto_name][0]]['credit'] += float("{0:.2f}".format(credit))
                        if not skip_month:
                            sum_purchase_base += float("{0:.2f}".format(debit)) - float("{0:.2f}".format(credit))

                if tax_name in purchase_taxes.keys():

                    if purchase_taxes[tax_name][1] not in move_taxes.keys():
                        move_taxes[purchase_taxes[tax_name][1]] = {'debit': float("{0:.2f}".format(debit)),
                                                                   'credit':float("{0:.2f}".format(credit))}
                    else:
                        move_taxes[purchase_taxes[tax_name][1]]['debit'] += float("{0:.2f}".format(debit))
                        move_taxes[purchase_taxes[tax_name][1]]['credit'] += float("{0:.2f}".format(credit))
                    if not skip_month:
                        sum_purchase_taxes += float("{0:.2f}".format(debit)) - float("{0:.2f}".format(credit))

            for move_line in move.line_ids:

                if different_period_items:
                    if not move_line.date_manual:
                        if not move.tax_date:
                            continue
                        elif move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                            continue
                    else:
                        if not (move_line.date_manual < wizard.date_from or move_line.date_manual > wizard.date_to):
                            continue
                else:
                    #jeżeli date_manual jest z innego miesiąca
                    if move_line.date_manual:
                        if not (move_line.date_manual >= wizard.date_from and move_line.date_manual <= wizard.date_to):
                            continue
                    #jeżeli data jest z innego miesiaca
                    else:
                        if move.date < wizard.date_from or move.date > wizard.date_to:
                            #i nie ma date_manual i tax_date
                            if not move_line.date_manual and not move.tax_date:
                                continue
                            if move.tax_date:
                                #i tax_date jest z innego miesiąca
                                if not (move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to):
                                    continue
                        #jeżeli data jest z tego miesiąca
                        if move.date >= wizard.date_from and move.date <= wizard.date_to:
                            # i nie ma date manual a tax_date jest z innego miesiąca
                            if move.tax_date and not move_line.date_manual:
                                if not (move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to):
                                    continue

                netto_name = move_line.tax_ids.tag_id.name
                tax_name = move_line.tax_line_id.tag_id.name

                if netto_name in purchase_taxes.keys() and purchase_taxes[netto_name][0] in move_taxes.keys() and len(purchase_taxes[netto_name]) == 2 and purchase_taxes[netto_name][1] not in move_taxes.keys():
                    move_taxes[purchase_taxes[netto_name][1]] = {'debit': 0, 'credit': 0}

            sorted_move_taxes = OrderedDict(sorted(move_taxes.items()))
            value_check = False
            for tax_name, amount in sorted_move_taxes.items():
                if amount['debit'] != 0 or amount['credit'] != 0:
                    value = amount['debit'] - amount['credit']

                    if not skip_month:
                        if not value_check and value != 0:
                            value_check = True

                    # JPK
                    tax_values[tax_name] = float("{0:.2f}".format(value))

                    # VAT documents
                    report_tax_name = tax_name.replace('K', 'P')
                    if report_tax_name not in taxes_sum_dict.keys():
                        # if move.customs > 0:
                        #     taxes_sum_dict[report_tax_name] = move.customs
                        # else:
                        taxes_sum_dict[report_tax_name] = value
                    else:
                        taxes_sum_dict[report_tax_name] += value

                else:
                    tax_values[tax_name] = 0

            if value_check:
                lp += 1
                purchase_dict[lp] = {
                    'country_code': partner_country_code,
                    'numeric_vat' : numeric_vat,
                    'vat': partner_vat,
                    'partner_name': partner_id.name,
                    'address': address,
                    'main_reference': main_reference,
                    'invoice_reference': invoice_reference,
                    'partner_reference': partner_reference,
                    'purchase_date': purchase_date,
                    'date_issue': date_issue or False,
                    'original_move_date': move.date,
                    'tax_values': tax_values.copy(),
                    'move_id': move.id,
                    'procedures_markers' : procedures_markers.copy(),
                    'date_recived': date_recived,
                    'purchase_doc_vdek': purchase_doc_vdek,
                }


        if lp > 0:
            purchase_ctrl = {
                'lp': lp,
                'sum_taxes': float("{0:.2f}".format(sum_purchase_taxes)),
                'sum_base': float("{0:.2f}".format(sum_purchase_base)),
            }
        else:
            if wizard._name == 'wizard.jpk.vat.2020':
                purchase_ctrl = {
                    'lp': 0,
                    'sum_taxes': 0,
                    'sum_base': 0
                    }

        # different fields for different declarations
        if wizard._name == 'account.report.vat.7.18':
            vat_data = CELLS_DICT_VAT_7_18.copy()
        elif wizard._name == 'wizard.jpk.vat.2020':
            vat_data = CELLS_DICT_VDEK.copy()
            if wizard.p_39_vdek:
                vat_data.update({'P_39': wizard.p_39_vdek})
            if wizard.p_49_vdek:
                vat_data.update({'P_49': wizard.p_49_vdek})
            if wizard.p_50_vdek:
                vat_data.update({'P_50': wizard.p_50_vdek})
            if wizard.p_52_vdek:
                vat_data.update({'P_52': wizard.p_52_vdek})

        else:
            vat_data = CELLS_DICT.copy()
        # pprint(taxes_sum_dict)
        vat_data.update(OrderedDict(taxes_sum_dict.items()))

        invoice_register = False
        if wizard._name == 'account.report.invoice_register':
            invoice_register = True
        for cell, value in vat_data.items():
            tax_return = False
            if isinstance(value, dict):
                cell_value = 0
                for op, cell_list in value.items():
                    for cell_item in cell_list:
                        cell_value = OPERATOR_MAP[op](cell_value, vat_data[cell_item])
                if invoice_register:
                    vat_data[cell] = float(round(cell_value, 2)) if cell_value > 0 else 0
                else:
                    if wizard._name == 'wizard.jpk.vat.2020':
                        if cell == 'P_51' and int(round(cell_value, 0)) < 0:
                            tax_return = abs(int(round(cell_value, 0)))
                    vat_data[cell] = int(round(cell_value, 0)) if cell_value > 0 else 0
            else:
                if invoice_register:
                    vat_data[cell] = float(round(value, 2))
                else:
                    vat_data[cell] = int(round(value, 0))
            if wizard._name == 'wizard.jpk.vat.2020':
                if wizard.p_59_vdek and tax_return:
                    vat_data.update({'P_59': 1})
                    vat_data.update({'P_60': tax_return})
                elif tax_return:
                    1==1
                    #vat_data.update({'P_53': tax_return})
                    #if wizard.p_54_vdek:
                     #   vat_data.update({'P_54': 1})
        if wizard._name == 'wizard.jpk.vat.2020':
            vat_data.update({'P_38': (vat_data['P_16']+vat_data['P_18']+vat_data['P_20']+vat_data['P_24']+vat_data['P_26']+vat_data['P_28']
                                            +vat_data['P_30']+vat_data['P_32']+vat_data['P_33']+vat_data['P_34'])-(vat_data['P_35']-vat_data['P_36'])})
            vat_data.update({'P_48': (vat_data['P_39']+vat_data['P_41']+vat_data['P_43']+vat_data['P_44']+vat_data['P_45']+vat_data['P_46']+vat_data['P_49'])})
            if (vat_data['P_38']) - vat_data['P_48'] > 0:
                vat_data.update({'P_51': (vat_data['P_38'] - vat_data['P_48'] - vat_data['P_49'] - vat_data['P_50'])})
            else:
                vat_data.update({'P_51': 0})
            if (vat_data['P_48'])-vat_data['P_38']>=0:
                vat_data.update({'P_53': (vat_data['P_48'] - vat_data['P_38'] +vat_data['P_52'])})
                vat_data.p_53_vdek=(vat_data['P_48'] - vat_data['P_38'] +vat_data['P_52'])
                wizard.p_53_vdek=vat_data.p_53_vdek
                #if wizard.p_54_vdek>0:
                vat_data.update({'P_54':wizard.p_54_vdek}) # jeżeli jest zwrot to te pole musibyć w xml plus zaznaczone któreś z klejnych pól 55,56,57,58
            else:
                vat_data.update({'P_53': 0})
                wizard.write({'p_53_vdek': 0})

            if wizard.p_55_vdek:
                vat_data.update({'P_55': 1})
            if wizard.p_56_vdek:
                vat_data.update({'P_56': 1})
            if wizard.p_57_vdek:
                vat_data.update({'P_57': 1})
            if wizard.p_58_vdek:
                vat_data.update({'P_58': 1})
            if wizard.p_59_vdek:
                vat_data.update({'P_59': 1})
            if wizard.p_60_vdek:
                vat_data.update({'P_60': wizard.p_60_vdek})
            if wizard.p_61_vdek:
                vat_data.update({'P_61': wizard.p_61_vdek})
            if (vat_data['P_53'])>0 and wizard.p_62_vdek>0:
                vat_data.update({'P_62': (wizard.p_62_vdek)})
            if wizard.p_63_vdek:
                vat_data.update({'P_63': 1})
            if wizard.p_64_vdek:
                vat_data.update({'P_64': 1})
            if wizard.p_65_vdek:
                vat_data.update({'P_65': 1})
            if wizard.p_66_vdek:
                vat_data.update({'P_66': 1})
            if wizard.p_67_vdek:
                vat_data.update({'P_67': 1})

        vat_dict = {
            'sale_dict': sale_dict,
            'sale_ctrl': sale_ctrl,
            'invoice_lines': invoice_line_dict,
            'invoice_line_ctrl': invoice_line_ctrl,
            'order_downpayment': order_downpayment,
            'order_ctrl' : order_ctrl,
            'purchase_dict': purchase_dict,
            'purchase_ctrl': purchase_ctrl,
            'taxes_sum_dict': vat_data,
            'ue_dict': ue_dict,
            'company_data': company_data,
        }
        # pprint(vat_dict)
        return vat_dict

    #JPK_KR
    @api.model
    def get_account_details(self, wizard, acc_details):
        # pprint(wizard)
        # pprint(acc_details)
        # pprint(self.env.context)
        acc_dict = {}
        journal_dict = {}
        journal_ctrl = {}
        acc_ml_dict = {}
        acc_ml_ctrl = {}
        count = 0
        count_j = 0
        count_ml = 0
        sum_amount_j = 0.00
        sum_debit = 0.00
        sum_credit = 0.00
        company_data = {
            'numeric_vat': self.get_vat(company_id=wizard.company_id),
        }

        accounts_list = self.env['account.account'].search([('deprecated','=',False)])
        for line in accounts_list:
            for res in acc_details['account_res']:
                if line.code == res['code']:
                    count += 1
                    acc_dict[count] = {
                        'name': line.name,
                        'code': line.code,
                        'type': line.user_type_id.name,
                        'group_code': line.code[0],
                        'group_name': line.name,
                        'category_name': line.name,
                        'balance_credit': float("{0:.2f}".format(res['balance_credit'])),
                        'balance_debit': float("{0:.2f}".format(res['balance_debit'])),
                        'month_credit': float("{0:.2f}".format(res['month_credit'])),
                        'month_debit': float("{0:.2f}".format(res['month_debit'])),
                        'ob_credit': float("{0:.2f}".format(res['ob_credit'])),
                        'ob_debit': float("{0:.2f}".format(res['ob_debit'])),
                        'year_credit': float("{0:.2f}".format(res['year_credit'])),
                        'year_debit': float("{0:.2f}".format(res['year_debit'])),
                    }
                    #add category
                    if line.code.find('-') != -1:
                        acc_dict[count].update({
                            'category_code':line.code[:line.code.find('-')],
                            'subcategory_code':line.code[line.code.find('-')+1:]
                        })
                    else:
                        acc_dict[count].update({
                            'category_code':line.code[:3],
                        })

        journal_details = self.env['account.move'].search([('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to)], order='date')
        for line in journal_details:
            count_j += 1
            #sale, purchase - faktura,
            #cash - raport kasowy,
            #bank = wyciąg bankowy
            #miscellanous - inna
            sum_amount_j += line.amount_total
            # _logger.warning('\n\n')
            # _logger.warning('%s'%[move_line.name for move_line in line.line_ids])
            # _logger.warning('first line')
            # _logger.warning('%s'%line.id)
            # # _logger.warning('%s'%[move_line.name for move_line in line.line_ids][0])
            # _logger.warning('\n\n')
            journal_dict[count_j] = {
                'lp': count_j,
                'nr_zapisu':line.name,
                'description':line.journal_id.name,
                'ref':line.name,
                'operation_date': line.date,# data operacji pewnie date_issue
                'document_date': line.date,# data dowodu pewnie invoice_date
                'inv_date':line.date,# jako data księgowania
                'operator_code':line.create_uid.id,#
                'operation_descr':line.ref if line.ref else line.partner_id.display_name or '/',# [move_line.name for move_line in line.line_ids][0] or
                'amount':float("{0:.2f}".format(line.amount_total)),
            }

            if line.journal_id.type == 'sale' or line.journal_id.type == 'purchase':
                journal_dict[count_j]['type'] = 'faktura'
            elif line.journal_id.type == 'cash':
                journal_dict[count_j]['type'] = 'raport kasowy'
            elif line.journal_id.type == 'bank':
                journal_dict[count_j]['type'] = 'wyciąg bankowy'
            elif line.journal_id.type == 'general':
                journal_dict[count_j]['type'] = 'inne'

        journal_ctrl = {
            'lj':count_j,
            'sum_amount_journal': float("{0:.2f}".format(sum_amount_j)),
        }

        acc_move_line_details = self.env['account.move.line'].search([('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to)], order='date')
        for line in acc_move_line_details:
            count_ml += 1
            sum_debit += float("{0:.2f}".format(line.debit))
            sum_credit += float("{0:.2f}".format(line.credit))
            acc_ml_dict[count_ml] = {
                'lp': count_ml,
                'nr_zapisu': line.move_id.name,
                'desc_debit': line.name if line.debit > 0 else '',
                'desc_credit': line.name if line.credit > 0 else '',
                'account_debit': line.account_id.code if line.debit > 0 else 'null',
                'account_credit': line.account_id.code if line.credit > 0 else 'null',
                'debit': float("{0:.2f}".format(line.debit)),
                'credit': float("{0:.2f}".format(line.credit)),
            }

            if line.amount_currency > 0:
                acc_ml_dict[count_ml].update({
                    'amount_currency_debit': float("{0:.2f}".format(line.amount_currency)),
                    'currency_code_debit': line.currency_id.name,
                })
            elif line.amount_currency < 0:
                acc_ml_dict[count_ml].update({
                    'amount_currency_credit': float("{0:.2f}".format(abs(line.amount_currency))),
                    'currency_code_credit': line.currency_id.name,
                })
        acc_ml_ctrl = {
            'lp': count_ml,
            'sum_debit': float("{0:.2f}".format(sum_debit)),
            'sum_credit': float("{0:.2f}".format(sum_credit)),
        }
        # pprint(acc_ml_dict)
        return {
            'company_data': company_data,
            'acc_dict': acc_dict,
            'journal_dict': journal_dict,
            'journal_ctrl': journal_ctrl,
            'acc_ml_dict': acc_ml_dict,
            'acc_ml_ctrl':acc_ml_ctrl,
        }

    # JPK_WB
    @api.model
    def get_bank_details(self, wizard):
        balance = {}
        balance_ln = {}
        balance_ln_ctrl = {}
        op_balance = 0.0
        count_line = 0
        charge_sum = 0.0
        credit_sum = 0.0
        period = wizard.period

        company_data = {
            'numeric_vat': self.get_vat(company_id=wizard.company_id),
        }

        acc_number = self.make_iban(wizard)

        balance_details = self.env['account.bank.statement'].search([('journal_id', '=', wizard.journal_id.id),('date', '>=', wizard.date_from),('date', '<=', wizard.date_to)], order='date')
        for index, line in enumerate(balance_details):
            # if there is only one bank statement indexing might not work properly, thus we need to cover that case
            if len(balance_details) == 1:
                balance['balance_start'] = float("{0:.2f}".format(line.balance_start))
                balance['balance_end'] = float("{0:.2f}".format(line.balance_end_real))
            else:
                if index == 0:
                    balance['balance_start'] = float("{0:.2f}".format(line.balance_start))
                if index == len(balance_details)-1:
                    balance['balance_end'] = float("{0:.2f}".format(line.balance_end_real))

        if 'balance_start' in balance:
            op_balance = float("{0:.2f}".format(balance['balance_start']))
        elif not balance:
            raise UserError(_('No data to display.'))
        else:
            raise UserError(_("Please check if the details e.g., dates you provided are correct or at least one bank statement is present for the given date!"))

        balance_lines_details = self.env['account.bank.statement.line'].search([('journal_id', '=', wizard.journal_id.id),('date', '>=', wizard.date_from),('date', '<=', wizard.date_to)], order='date')
        for bl in balance_lines_details:
            count_line += 1
            op_balance += float("{0:.2f}".format(bl.amount))
            balance_ln[count_line] = {
                'lp': count_line,
                'date': bl.date,
                'name': bl.partner_id.display_name,
                'op_desc': bl.name,
                'amount': float("{0:.2f}".format(bl.amount)),
                'balance': float("{0:.2f}".format(op_balance)),
            }
            if bl.amount < 0:
                charge_sum += float("{0:.2f}".format(bl.amount))
            else:
                credit_sum += float("{0:.2f}".format(bl.amount))
            if not bl.partner_id.display_name:
                balance_ln[count_line].update({
                    'name': 'brak',
                })
        balance_ln_ctrl = {
            'lp': count_line,
            'charge_sum': abs(float("{0:.2f}".format(charge_sum))),
            'credit_sum': float("{0:.2f}".format(credit_sum)),
        }

        return {
            'company_data': company_data,
            'acc_number': acc_number,
            'balance': balance,
            'balance_ln': balance_ln,
            'balance_ln_ctrl': balance_ln_ctrl,
        }
