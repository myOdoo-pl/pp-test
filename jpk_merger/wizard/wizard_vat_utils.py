from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _

from odoo.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period, REVERSE_QUARTER_MAP
from odoo.addons.account_pl_cirrus.data.constant_values import *
from odoo.addons.jpk_merger.data.structures import *

from collections import OrderedDict
from math import fabs
import logging

_logger = logging.getLogger(__name__)


class WizardVatUtils(models.TransientModel):
    _inherit = 'wizard.vat.utils'

    @api.model
    def get_vat_details(
            self, wizard, filter_journals=False, cash_basis=False, natural_person=False, different_period_items=False
    ):
        account_move_obj = self.env['account.move']
        moves = account_move_obj
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
            'numeric_vat': self.get_vat(company_id=company_id)
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
            payments = self.env['account.payment'].search([
                ('payment_date', '>=', wizard.date_from),
                ('payment_date', '<=', wizard.date_to),
                ('payment_type', '!=', 'transfer')
            ])
            move_payment_dict = {}

            for payment in payments.filtered(
                    lambda r: not r.partner_id.property_account_position_id.name
                    or r.partner_id.property_account_position_id.name == 'Kraj'
            ):
                move_line_ids = payment.move_line_ids
                payment_move = move_line_ids.mapped('move_id')
                payment_move.ensure_one()

                partial_reconcile_ids = move_line_ids.mapped('matched_debit_ids') + move_line_ids.mapped(
                    'matched_credit_ids'
                )
                move_lines = (
                        partial_reconcile_ids.mapped('debit_move_id') + partial_reconcile_ids.mapped('credit_move_id')
                ).filtered(lambda r: r not in move_line_ids)

                move = move_lines.mapped('move_id').filtered(
                    lambda r: r.state == 'posted' and len(
                        r.line_ids.mapped('tax_line_id') + r.line_ids.mapped('tax_ids')
                    ) > 0
                )

                if not move:
                    continue

                elif len(move) == 1:
                    if home_currency_id in move.line_ids.mapped('currency_id') or not \
                            move.line_ids.mapped('currency_id'):
                        partial_payment = payment_move.amount / move.amount
                    else:
                        amount_move = max(move.line_ids.mapped(lambda r: fabs(r.amount_currency)))
                        amount_payment = max(payment_move.line_ids.mapped(lambda r: fabs(r.amount_currency)))
                        partial_payment = amount_payment / amount_move

                    if move.id not in move_payment_dict:
                        move_payment_dict[move.id] = {
                            'partial_payment': partial_payment,
                            'date': payment.payment_date
                        }
                    else:
                        move_payment_dict[move.id]['partial_payment'] += partial_payment
                        move_payment_dict[move.id]['date'] = max(
                            move_payment_dict[move.id]['date'], payment.payment_date
                        )

                    if move not in moves:
                        moves += move

                else:
                    for m in move:
                        move_line = m.line_ids.filtered(
                            lambda l: fabs(l.balance) == max(m.line_ids.mapped(lambda k: fabs(k.balance)))
                        )

                        payment_lines = move_line_ids.mapped('matched_debit_ids').filtered(
                            lambda p: p.debit_move_id == move_line
                        ).mapped('credit_move_id')

                        if not payment_lines:
                            payment_lines = move_line_ids.mapped('matched_credit_ids').filtered(
                                lambda p: p.credit_move_id == move_line
                            ).mapped('debit_move_id')

                        if home_currency_id in m.line_ids.mapped('currency_id') or not m.line_ids.mapped('currency_id'):
                            partial_payment = sum(payment_lines.mapped(lambda t: fabs(t.balance))) / fabs(m.amount)
                        else:
                            amount_move = max(m.line_ids.mapped(lambda r: fabs(r.amount_currency)))
                            amount_payment = sum(payment_lines.mapped(lambda r: fabs(r.amount_currency)))
                            partial_payment = amount_payment / amount_move

                        if m.id not in move_payment_dict:
                            move_payment_dict[m.id] = {
                                'partial_payment': partial_payment,
                                'date': payment.payment_date
                            }
                        else:
                            move_payment_dict[m.id]['partial_payment'] += partial_payment
                            move_payment_dict[m.id]['date'] = max(move_payment_dict[m.id]['date'], payment.payment_date)

                        if m not in moves:
                            moves += m

            other_moves = account_move_obj.search([
                ['company_id', '=', company_id.id],
                '&', '|', '&', ('tax_date', '>=', wizard.date_from), ('tax_date', '<=', wizard.date_to),
                '&', '&', ('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to), ('tax_date', '=', False),
                ('state', '=', 'posted')
            ]).filtered(
                lambda r: r.partner_id.property_account_position_id.name in ('Wspólnota', 'Import/Eksport') or (
                        not r.partner_id.property_account_position_id or
                        r.partner_id.property_account_position_id.name == 'Kraj'
                ) and ((r.line_ids.mapped('tax_line_id') or r.line_ids.mapped('tax_ids')) and
                       (not r.line_ids.mapped('invoice_id') or
                        (any(move_type in ['in_refund', 'out_refund'] for
                             move_type in r.line_ids.mapped('invoice_id.move_type')))))
            )

            for m in other_moves:
                if m not in moves:
                    moves += m

            moves = moves.sorted(lambda r: move_payment_dict.get(r.id, {}).get('date', False) or r.tax_date or r.date)

        else:
            moves = account_move_obj.search([
                ['company_id', '=', company_id.id],
                '&', '|', '&', ('tax_date', '>=', wizard.date_from), ('tax_date', '<=', wizard.date_to),
                '&', '&', ('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to), ('tax_date', '=', False),
                ('state', '=', 'posted')
            ])

            manual_move_lines = self.env['account.move.line'].search([
                ('company_id', '=', company_id.id),
                ('date_manual', '>=', wizard.date_from),
                ('date_manual', '<=', wizard.date_to)
            ])

            manual_move_ids = [move.move_id.id for move in manual_move_lines]
            manual_date_moves = account_move_obj.search([('id', 'in', manual_move_ids), ('state', '=', 'posted')])

            for move in manual_date_moves:
                if move.id not in moves.ids:
                    moves += manual_date_moves

            moves = moves.sorted(lambda r: r.tax_date or r.date)

        if different_period_items:
            moves = account_move_obj.search([
                ['company_id', '=', company_id.id],
                '|', ('tax_date', '<', wizard.date_from), ('tax_date', '>', wizard.date_to),
                ('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to), ('state', '=', 'posted')
            ])
            manual_move_lines = self.env['account.move.line'].search([
                ('company_id', '=', company_id.id),
                '|', ('date_manual', '<=', wizard.date_from),
                ('date_manual', '>=', wizard.date_to),
                ('date', '>=', wizard.date_from),
                ('date', '<=', wizard.date_to)
            ])

            manual_move_ids = [move.move_id.id for move in manual_move_lines]
            manual_date_moves = account_move_obj.search([('id', 'in', manual_move_ids), ('state', '=', 'posted')])

            for move in manual_date_moves:
                if move.id not in moves.ids:
                    moves += manual_date_moves

            moves = moves.sorted(lambda r: r.tax_date or r.date)

        # invoice register
        if filter_journals:
            moves = moves.filtered(lambda r: r.journal_id in filter_journals)

        sale_move_ids = moves.filtered(
            lambda x: any(tax in TAXES_SALE.keys() for tax in x.line_ids.mapped('tax_ids.tag_id.name')) or any(
                tax in TAXES_SALE.keys() for tax in x.line_ids.mapped('tax_line_id.tag_id.name')
            )
        )

        # TODO: PIERWSZA PRÓBA MODYFIKACJI.
        purchase_move_ids = moves.filtered(
            lambda x: any(tax in TAXES_PURCHASE.keys() for tax in x.line_ids.mapped('tax_ids.tag_id.name')) or any(
                tax in TAXES_PURCHASE.keys() for tax in x.line_ids.mapped('tax_line_id.tag_id.name')
            )
        )

        _logger.warning('MOVES: ' + str(len(moves)))
        _logger.warning('SALE MOVES: ' + str(len(sale_move_ids)))
        _logger.info('PURCHASE MOVES: ' + str(len(purchase_move_ids)))

        sum_sale_taxes = 0.0
        sum_purchase_taxes = 0.0
        sum_sale_base = 0.0
        sum_purchase_base = 0.0
        sum_invoice_line = 0.0
        po_sum_invoice_line = 0.0
        order_sum = 0.0
        purchase_order_sum = 0.0
        lp = 0
        po_lp = 0
        fa_lp = 0
        po_fa_lp = 0
        order_lp = 0
        purchase_order_lp = 0
        sale_dict = {}
        purchase_dict = {}
        order_downpayment = {}
        purchase_order_downpayment = {}
        taxes_sum_dict = {}
        sale_ctrl = {}
        purchase_ctrl = {}
        order_ctrl = {}
        purchase_order_ctrl = {}
        invoice_line_dict = {}
        purchase_invoice_line_dict = {}
        invoice_line_ctrl = {}
        purchase_invoice_line_ctrl = {}
        ue_dict = {'UE_C': {}, 'UE_D': {}, 'UE_E': {}}
        taxes_check_sum = {}

        if wizard._name != 'wizard_jpk_fa_bill':
            for move in sale_move_ids:
                different_month = []
                this_month = []
                different_dates_lines = [move_line for move_line in move.line_ids if move_line.date_manual is not False]

                if different_dates_lines:
                    for line in different_dates_lines:
                        base_tax = self.env['account.tax'].search([('children_tax_ids', 'in', line.tax_line_id.id)])
                        net_lines = [
                            move_line.id for move_line in move.line_ids if base_tax.id in move_line.tax_ids.ids
                        ]

                        if not base_tax or not net_lines:
                            net_lines = [
                                move_line.id for move_line in move.line_ids if
                                line.tax_line_id.id in move_line.tax_ids.ids
                            ]

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
                        raise UserError(_('Journal Entry %s has incorrect settled partners.') % move.name)

                elif not partner_id:
                    if not move.custom_partner_id:
                        raise UserError(_('Please add partner to %s Journal Entry') % move.name)
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
                    'vat': self.get_vat(partner_id=partner_id) and sale_partner_vat or 'brak'
                }

                display_date = move.tax_date or move.date
                date_issue = move.date_issue or display_date
                sale_date = display_date if date_issue and date_issue != display_date else False
                invoice_reference = move.name
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

                # better filtering of deposit prod and compute discounts
                if inv:
                    inv = inv[0]
                    deposit_product_id = int(
                        self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
                    )
                    deposit_line = inv.invoice_line_ids.filtered(lambda r: r.product_id.id == deposit_product_id)
                    negative_deposit_line = deposit_line if deposit_line and sum(
                        deposit_line.mapped('price_subtotal')
                    ) < 0 else False

                    if inv.reversed_entry_id:
                        refund_inv_id = inv.reversed_entry_id
                        invoice_type = 'KOREKTA'
                        refund_reason = inv.name
                        refunded_inv_number = refund_inv_id.name
                        refunded_period = (
                            refund_inv_id.date_issue if refund_inv_id.date_issue else refund_inv_id.invoice_date
                        ).strftime('%m.%Y')

                    elif deposit_line and not negative_deposit_line:
                        invoice_type = 'ZAL'
                        down_payment_value = inv.amount_total_signed
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
                        dp = self.prepare_line_value(
                            inv, company_id, abs(sum(negative_deposit_line.mapped('price_total'))), compute=True
                        )
                        down_payment_discount = dp / (inv.amount_total_signed + dp)

                    amount_total = inv.amount_total_signed
                    for line in inv.invoice_line_ids.filtered(
                            lambda r: (r not in (negative_deposit_line or [])) and (r.display_type is False)
                    ):
                        fa_lp += 1
                        sum_invoice_line += line.price_subtotal

                        price_unit = self.prepare_line_value(
                            inv, company_id, line.price_unit - line.price_unit * down_payment_discount, True, True
                        )
                        unit_gross = self.prepare_line_value(
                            inv, company_id, line.price_unit - line.price_unit * down_payment_discount, True, True
                        )

                        if line.tax_ids:
                            unit_taxes = line.tax_ids.compute_all(
                                line.price_unit, inv.currency_id, 1, product=line.product_id, partner=partner_id
                            )
                            unit_taxes_value = unit_taxes['total_included']
                            unit_gross = self.prepare_line_value(
                                inv, company_id, unit_taxes_value - unit_taxes_value * down_payment_discount, True, True
                            )

                        discount = self.prepare_line_value(
                            inv, company_id, (line.price_unit * line.quantity) * (
                                    (line.discount / 100) + down_payment_discount
                            ), True, True)
                        subtotal = self.prepare_line_value(
                            inv, company_id, line.price_subtotal - line.price_subtotal * down_payment_discount,
                            round=True
                        )
                        gross = self.prepare_line_value(
                            inv, company_id, line.price_total - line.price_total * down_payment_discount, True, True
                        )

                        invoice_line_dict[fa_lp] = {
                            'invoice_reference': main_reference,
                            'name': line.name,
                            'uom': line.product_uom_id.name,
                            'qty': line.quantity,
                            'price_unit': price_unit,
                            'unit_gross': unit_gross,
                            'subtotal': subtotal,
                            'discount': discount,
                            'gross': gross,
                            'tax_group': TAXES_INV_LINE[line.tax_ids.tag_id.name]
                        }

                    seller_data = company_data.copy() if inv.move_type in [
                        'out_invoice', 'out_refund'
                    ] else partner_data.copy()
                    purchaser_data = partner_data.copy() if inv.move_type in [
                        'out_invoice', 'out_refund'
                    ] else company_data.copy()

                    if (not partner_id.property_account_position_id or
                        partner_id.property_account_position_id.name == 'Kraj') and inv.move_type in [
                        'out_invoice', 'out_refund'
                    ] and cash_basis:
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
                                elif (move.tax_date >= wizard.date_from) and (move.tax_date <= wizard.date_to):
                                    continue
                            else:
                                if not (move_line.date_manual < wizard.date_from or
                                        move_line.date_manual > wizard.date_to):
                                    continue
                        else:
                            if move_line.date_manual:
                                if not move_line.date_manual >= wizard.date_from and \
                                        move_line.date_manual <= wizard.date_to:
                                    continue

                            else:
                                if move.date < wizard.date_from or move.date > wizard.date_to:
                                    if not move_line.date_manual and not move.tax_date:
                                        continue

                                    if move.tax_date:
                                        if not move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                                            continue

                                if (move.date >= wizard.date_from) and (move.date <= wizard.date_to):
                                    if move.tax_date and not move_line.date_manual:
                                        if not move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                                            continue

                    if wizard._name == 'wizard.jpk.vat.2020' and \
                            (wizard.date_from.month != wizard.date_to.month and wizard.period != 1) and \
                            wizard.no_declaration_data is False:
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
                            move_taxes[control_netto_name] = {
                                'credit': float("{0:.2f}".format(credit_custom_value)),
                                'debit': float("{0:.2f}".format(debit_custom_value))
                            }
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
                                move_taxes[control_netto_name] = {
                                    'credit': float("{0:.2f}".format(credit)),
                                    'debit': float("{0:.2f}".format(debit))
                                }
                            else:
                                move_taxes[control_netto_name]['credit'] += float("{0:.2f}".format(credit))
                                move_taxes[control_netto_name]['debit'] += float("{0:.2f}".format(debit))

                            if netto_name == 'WSU':
                                if 'K_12' not in move_taxes.keys():
                                    move_taxes['K_12'] = {
                                        'credit': float("{0:.2f}".format(credit)),
                                        'debit': float("{0:.2f}".format(debit))
                                    }
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
                                ue_dict[ue_name][partner_data['vat']] = {
                                    'country_code': partner_data['country_code'],
                                    'vat': partner_data['numeric_vat'],
                                    'amount': 0.0
                                }

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
                                move_taxes[control_netto_name] = {
                                    'credit': float("{0:.2f}".format(credit_vwew)),
                                    'debit': float("{0:.2f}".format(debit_vwew))
                                }
                            else:
                                move_taxes[control_netto_name]['credit'] += float("{0:.2f}".format(credit_vwew))
                                move_taxes[control_netto_name]['debit'] += float("{0:.2f}".format(debit_vwew))

                            if not skip_month:
                                sum_sale_taxes += float("{0:.2f}".format(credit_vwew))

                        if control_tax_name not in move_taxes.keys():
                            move_taxes[control_tax_name] = {
                                'credit': float("{0:.2f}".format(credit)),
                                'debit': float("{0:.2f}".format(debit))
                            }
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
                    raise UserError(_(
                        "Error ocured while JPK taxes validation. Please correct taxes in Journal Entry %s"
                    ) % move.name)

                sorted_move_taxes = OrderedDict(sorted(move_taxes.items()))
                value_check = False
                for tax_name, amount in sorted_move_taxes.items():
                    if amount['credit'] != 0 or amount['debit'] != 0:
                        if tax_name in ['K_23', 'K_25', 'K_27', 'K_29', 'K_34']:
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
                        'product_tax_markers': product_tax_markers.copy(),
                        'procedures_markers': procedures_markers.copy(),
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
                        'doc_type_vdek': inv.doc_type_vdek
                    }
        # TODO: SALE DICT LOOP END!

        # TODO: PURCHASE DICT LOOP START!
        if wizard._name == 'wizard_jpk_fa_bill':
            for move in purchase_move_ids:
                _logger.info(f'MOVE: {move}')
                _logger.info(f'MOVE NAME: {move.name}')
                different_month = []
                this_month = []
                different_dates_lines = [move_line for move_line in move.line_ids if move_line.date_manual is not False]

                if different_dates_lines:
                    for line in different_dates_lines:
                        base_tax = self.env['account.tax'].search([('children_tax_ids', 'in', line.tax_line_id.id)])
                        net_lines = [
                            move_line.id for move_line in move.line_ids if base_tax.id in move_line.tax_ids.ids
                        ]
                        if not base_tax or not net_lines:
                            net_lines = [
                                move_line.id for move_line in move.line_ids if
                                line.tax_line_id.id in move_line.tax_ids.ids
                            ]

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
                        raise UserError(_('Journal Entry %s has incorrect setted partners.') % move.name)

                elif not partner_id:
                    if not move.custom_partner_id:
                        raise UserError(_('Please add partner to %s Journal Entry') % move.name)
                    else:
                        partner_id = move.custom_partner_id

                purchase_partner_vat = 'brak'
                if partner_id.vat:
                    if partner_id.vat[:2] == 'PL':
                        purchase_partner_vat = partner_id.vat[2:]
                    else:
                        purchase_partner_vat = partner_id.vat

                partner_data = {
                    'name': partner_id.name,
                    'address': self.get_address(partner_id=partner_id),
                    'country_code': self.get_vat_code(partner_id=partner_id, skip_pl=True),
                    'numeric_vat': self.get_vat(partner_id=partner_id) or 'brak',
                    'vat': self.get_vat(partner_id=partner_id) and purchase_partner_vat or 'brak'
                }

                display_date = move.tax_date or move.date
                date_issue = move.date_issue or display_date
                sale_date = display_date if date_issue and date_issue != display_date else False
                invoice_reference = move.name
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
                    deposit_product_id = int(
                        self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
                    )
                    deposit_line = inv.invoice_line_ids.filtered(lambda r: r.product_id.id == deposit_product_id)
                    negative_deposit_line = deposit_line if deposit_line and sum(
                        deposit_line.mapped('price_subtotal')
                    ) < 0 else False

                    if inv.reversed_entry_id:
                        refund_inv_id = inv.reversed_entry_id
                        invoice_type = 'KOREKTA'
                        refund_reason = inv.name
                        refunded_inv_number = refund_inv_id.name
                        refunded_period = (
                            refund_inv_id.date_issue if refund_inv_id.date_issue else refund_inv_id.invoice_date
                        ).strftime('%m.%Y')

                    elif deposit_line and not negative_deposit_line:
                        invoice_type = 'ZAL'
                        down_payment_value = inv.amount_total_signed
                        down_payment_tax = self.prepare_line_value(inv, company_id, inv.amount_tax, True, True)
                        purchase_order_line = inv.invoice_line_ids.mapped('purchase_line_id')

                        if purchase_order_line:
                            purchase_order = purchase_order_line[0].order_id
                            purchase_order_line_dict = {}
                            purchase_order_line_lp = 0
                            purchase_order_lp += 1

                            for order_line in purchase_order.order_line:
                                if order_line.product_id.id == deposit_product_id:
                                    continue

                                else:
                                    purchase_order_line_lp += 1
                                    purchase_order_line_dict[purchase_order_line_lp] = {
                                        'product': order_line.product_id.name,
                                        'uom': order_line.product_uom.name,
                                        'qty': order_line.product_qty,
                                        'price_unit': order_line.price_unit,
                                        'price_subtotal': order_line.price_subtotal,
                                        'tax': order_line.price_tax,
                                        'tax_group': TAXES_INV_LINE[order_line.tax_ids.tag_id.name]
                                    }

                            purchase_order_sum += purchase_order.amount_total
                            if purchase_order:
                                purchase_order_downpayment[purchase_order_lp] = {
                                    'main_reference': main_reference,
                                    'order_total': purchase_order.amount_total,
                                    'order_line': purchase_order_line_dict
                                }

                    else:
                        invoice_type = 'VAT'

                    down_payment_discount = 0
                    if negative_deposit_line:
                        dp = self.prepare_line_value(
                            inv, company_id, abs(sum(negative_deposit_line.mapped('price_total'))), compute=True
                        )
                        down_payment_discount = dp / (inv.amount_total_signed + dp)

                    amount_total = inv.amount_total_signed
                    for line in inv.invoice_line_ids.filtered(
                            lambda r: (r not in (negative_deposit_line or [])) and (r.display_type is False)
                    ):
                        po_fa_lp += 1
                        po_sum_invoice_line += line.price_subtotal
                        price_unit = self.prepare_line_value(
                            inv, company_id, line.price_unit - line.price_unit * down_payment_discount, True, True
                        )
                        unit_gross = self.prepare_line_value(
                            inv, company_id, line.price_unit - line.price_unit * down_payment_discount, True, True
                        )

                        if line.tax_ids:
                            unit_taxes = line.tax_ids.compute_all(
                                line.price_unit, inv.currency_id, 1, product=line.product_id, partner=partner_id
                            )
                            unit_taxes_value = unit_taxes['total_included']
                            unit_gross = self.prepare_line_value(
                                inv, company_id, unit_taxes_value - unit_taxes_value * down_payment_discount, True, True
                            )

                        discount = self.prepare_line_value(
                            inv, company_id,
                            (line.price_unit * line.quantity) * ((line.discount / 100) + down_payment_discount),
                            True, True
                        )
                        subtotal = self.prepare_line_value(
                            inv, company_id, line.price_subtotal - line.price_subtotal * down_payment_discount,
                            round=True
                        )
                        gross = self.prepare_line_value(
                            inv, company_id, line.price_total - line.price_total * down_payment_discount, True, True
                        )
                        purchase_invoice_line_dict[po_fa_lp] = {
                            'invoice_reference': main_reference,
                            'name': line.name,
                            'uom': line.product_uom_id.name,
                            'qty': line.quantity,
                            'price_unit': price_unit,
                            'unit_gross': unit_gross,
                            'subtotal': subtotal,
                            'discount': discount,
                            'gross': gross,
                            'tax_group': TAXES_INV_LINE[line.tax_ids.tag_id.name]
                        }

                    vendor_bill_types = ['in_invoice', 'in_refund']
                    account_position = partner_id.property_account_position_id
                    seller_data = company_data.copy() if inv.move_type in vendor_bill_types else partner_data.copy()
                    purchaser_data = partner_data.copy() if inv.move_type in vendor_bill_types else company_data.copy()

                    if (not account_position or account_position.name == 'Kraj') and \
                            inv.move_type in vendor_bill_types and cash_basis:
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

                                elif (move.tax_date >= wizard.date_from) and (move.tax_date <= wizard.date_to):
                                    continue

                            else:
                                if not (move_line.date_manual < wizard.date_from or
                                        move_line.date_manual > wizard.date_to):
                                    continue

                        else:
                            if move_line.date_manual:
                                if not move_line.date_manual >= wizard.date_from and \
                                        move_line.date_manual <= wizard.date_to:
                                    continue

                            else:
                                if move.date < wizard.date_from or move.date > wizard.date_to:
                                    if not move_line.date_manual and not move.tax_date:
                                        continue

                                    if move.tax_date:
                                        if not move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                                            continue

                                if (move.date >= wizard.date_from) and (move.date <= wizard.date_to):
                                    if move.tax_date and not move_line.date_manual:
                                        if not move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                                            continue

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
                        control_netto_name = TAXES_PURCHASE[tax_name][0]

                        if len(TAXES_PURCHASE[tax_name]) > 1:
                            control_tax_name = TAXES_PURCHASE[tax_name][1]

                        if move.ref:
                            main_reference = move.ref

                        debit_custom_value = 0.0
                        credit_custom_value = move_line.tax_basic_custom
                        if control_netto_name not in move_taxes.keys():
                            move_taxes[control_netto_name] = {
                                'credit': float("{0:.2f}".format(credit_custom_value)),
                                'debit': float("{0:.2f}".format(debit_custom_value))
                            }

                        else:
                            move_taxes[control_netto_name]['credit'] += float("{0:.2f}".format(credit_custom_value))
                            move_taxes[control_netto_name]['debit'] += float("{0:.2f}".format(debit_custom_value))

                        if not skip_month:
                            sum_purchase_taxes += float("{0:.2f}".format(credit_custom_value))

                    else:
                        if netto_name in TAXES_PURCHASE.keys():
                            control_netto_name = TAXES_PURCHASE[netto_name][0]

                            if len(TAXES_PURCHASE[netto_name]) > 1:
                                control_tax_name = TAXES_PURCHASE[netto_name][1]

                            if control_netto_name not in move_taxes.keys():
                                move_taxes[control_netto_name] = {
                                    'credit': float("{0:.2f}".format(credit)),
                                    'debit': float("{0:.2f}".format(debit))
                                }
                            else:
                                move_taxes[control_netto_name]['credit'] += float("{0:.2f}".format(credit))
                                move_taxes[control_netto_name]['debit'] += float("{0:.2f}".format(debit))

                            if netto_name == 'WSU':
                                if 'K_12' not in move_taxes.keys():
                                    move_taxes['K_12'] = {
                                        'credit': float("{0:.2f}".format(credit)),
                                        'debit': float("{0:.2f}".format(debit))
                                    }
                                else:
                                    move_taxes['K_12']['credit'] += float("{0:.2f}".format(credit))
                                    move_taxes['K_12']['debit'] += float("{0:.2f}".format(debit))

                                if 'K_12' not in expected_taxes:
                                    expected_taxes.append('K_12')

                            if not skip_month:
                                if move.journal_id.type == 'purchase':
                                    sum_purchase_base += float("{0:.2f}".format(debit)) - float(
                                        "{0:.2f}".format(credit)
                                    )
                                else:
                                    sum_purchase_base += float("{0:.2f}".format(credit)) - float(
                                        "{0:.2f}".format(debit)
                                    )

                        if netto_name in TAXES_UE.keys():
                            ue_name = TAXES_UE[netto_name]
                            if partner_data['vat'] not in ue_dict[ue_name]:
                                ue_dict[ue_name][partner_data['vat']] = {
                                    'country_code': partner_data['country_code'],
                                    'vat': partner_data['numeric_vat'],
                                    'amount': 0.0
                                }

                            if netto_name in TAXES_UE_SALE:
                                ue_dict[ue_name][partner_data['vat']]['amount'] += credit - debit
                            else:
                                ue_dict[ue_name][partner_data['vat']]['amount'] += debit - credit

                    if tax_name in TAXES_PURCHASE.keys():
                        control_netto_name = TAXES_PURCHASE[tax_name][0]

                        if len(TAXES_PURCHASE[tax_name]) > 1:
                            control_tax_name = TAXES_PURCHASE[tax_name][1]

                        if tax_name == 'VWEW' and move.customs:
                            if move.ref:
                                main_reference = move.ref

                            debit_vwew = 0.0
                            credit_vwew = move.customs

                            if control_netto_name not in move_taxes.keys():
                                move_taxes[control_netto_name] = {
                                    'credit': float("{0:.2f}".format(credit_vwew)),
                                    'debit': float("{0:.2f}".format(debit_vwew))
                                }
                            else:
                                move_taxes[control_netto_name]['credit'] += float("{0:.2f}".format(credit_vwew))
                                move_taxes[control_netto_name]['debit'] += float("{0:.2f}".format(debit_vwew))

                            if not skip_month:
                                sum_purchase_taxes += float("{0:.2f}".format(credit_vwew))

                        if control_tax_name not in move_taxes.keys():
                            move_taxes[control_tax_name] = {
                                'credit': float("{0:.2f}".format(credit)),
                                'debit': float("{0:.2f}".format(debit))
                            }
                        else:
                            move_taxes[control_tax_name]['credit'] += float("{0:.2f}".format(credit))
                            move_taxes[control_tax_name]['debit'] += float("{0:.2f}".format(debit))

                        if not skip_month:
                            sum_purchase_taxes += float("{0:.2f}".format(credit)) - float("{0:.2f}".format(debit))

                    if control_netto_name and control_netto_name not in expected_taxes:
                        expected_taxes.append(control_netto_name)

                    if control_tax_name and control_tax_name not in expected_taxes:
                        expected_taxes.append(control_tax_name)

                taxes_check = move_taxes.keys()
                if len(expected_taxes) != len(taxes_check) or len(set(expected_taxes) - set(taxes_check)) > 0:
                    raise UserError(_(
                        'Error occured while JPK taxes validation. Please correct taxes in Journal Entry %s'
                    ) % move.name)

                sorted_move_taxes = OrderedDict(sorted(move_taxes.items()))
                value_check = False
                for tax_name, amount in sorted_move_taxes.items():
                    if amount['credit'] != 0 or amount['debit'] != 0:
                        if tax_name in ['K_23', 'K_25', 'K_27', 'K_29', 'K_34']:
                            value = amount['debit'] - amount['credit']
                        else:
                            value = amount['credit'] - amount['debit']

                        if not skip_month:
                            if not value_check and value != 0:
                                value_check = True

                        tax_values[tax_name] = float("{0:.2f}".format(value))
                        if not skip_month:
                            if taxes_check_sum.get(tax_name):
                                taxes_check_sum[tax_name] += float("{0:.2f}".format(value))
                            else:
                                taxes_check_sum[tax_name] = float("{0:.2f}".format(value))

                        report_tax_name = tax_name.replace('K', 'P')
                        if report_tax_name not in taxes_sum_dict.keys():
                            taxes_sum_dict[report_tax_name] = value
                        else:
                            taxes_sum_dict[report_tax_name] += value

                    else:
                        tax_values[tax_name] = 0

                product_tax_markers = OrderedDict(sorted(product_tax_markers.items()))
                if value_check:
                    po_lp += 1
                    _logger.info(f'REFERENCE: {main_reference}')
                    _logger.info(f'DATE ISSUE: {date_issue}')
                    purchase_dict[po_lp] = {
                        'partner_data': partner_data.copy(),
                        'seller_data': seller_data.copy(),
                        'purchaser_data': purchaser_data.copy(),
                        'tax_values': tax_values.copy(),
                        'product_tax_markers': product_tax_markers.copy(),
                        'procedures_markers': procedures_markers.copy(),
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
                        'doc_type_vdek': inv.doc_type_vdek
                    }
        # TODO: KONIEC PĘTLI PURCHASE DICT

        if lp > 0:
            sale_ctrl = {
                'lp': lp,
                'sum_taxes': float("{0:.2f}".format(sum_sale_taxes)),
                'sum_base': float("{0:.2f}".format(sum_sale_base)),
                'sum_all': float("{0:.2f}".format(sum_sale_taxes + sum_sale_base)),
                'taxes_check_sum': taxes_check_sum,
            }

        # TODO: MODYFIKACJA!!!
        if wizard._name == 'wizard_jpk_fa_bill':
            if po_lp > 0:
                purchase_ctrl = {
                    'po_lp': po_lp,
                    'po_sum_taxes': float("{0:.2f}".format(sum_purchase_taxes)),
                    'po_sum_base': float("{0:.2f}".format(sum_purchase_base)),
                    'po_sum_all': float("{0:.2f}".format(sum_purchase_taxes + sum_purchase_base)),
                    'taxes_check_sum': taxes_check_sum
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

                # TODO: MODYFIKACJA!!!
                if wizard._name == 'wizard_jpk_fa_bill':
                    purchase_ctrl = {
                        'po_lp': 0,
                        'po_sum_taxes': 0,
                        'po_sum_base': 0,
                        'po_sum_all': 0,
                        'taxes_check_sum': 0
                    }

        if fa_lp > 0:
            invoice_line_ctrl = {
                'lp': fa_lp,
                'sum_invoice_line': sum_invoice_line,
            }

        # TODO: MODYFIKACJA!!!
        if wizard._name == 'wizard_jpk_fa_bill':
            if po_fa_lp > 0:
                purchase_invoice_line_ctrl = {
                    'po_lp': po_fa_lp,
                    'po_sum_invoice_line': po_sum_invoice_line
                }

        if order_lp > 0:
            order_ctrl = {
                'lp': order_lp,
                'order_sum': order_sum
            }

        # TODO: MODYFIKACJA!!!
        if wizard._name == 'wizard_jpk_fa_bill':
            if purchase_order_lp > 0:
                purchase_order_ctrl = {
                    'lp': purchase_order_lp,
                    'purchase_order_sum': purchase_order_sum
                }

        lp = 0
        if wizard._name != 'wizard_jpk_fa_bill':
            sum_purchase_base = 0.0
            sum_purchase_taxes = 0.0
            purchase_dict = {}
            purchase_ctrl = {}

        purchase_move_ids = moves.filtered(
            lambda x: any(tax in purchase_taxes.keys() for tax in x.line_ids.mapped('tax_ids.tag_id.name')) or any(
                tax in purchase_taxes.keys() for tax in x.line_ids.mapped('tax_line_id.tag_id.name')
            )
        )

        if wizard._name != 'wizard_jpk_fa_bill':
            for move in purchase_move_ids:
                partner_id = move.line_ids.mapped('partner_id')
                if len(partner_id) > 1:
                    partners = [line.partner_id for line in move.line_ids if line.tax_line_id]

                    if partners:
                        partner_id = partners[0]
                    else:
                        raise UserError(_('Journal Entry %s has incorrect settled partners.') % move.name)

                elif not partner_id:
                    if not move.custom_partner_id:
                        raise UserError(_('Please add partner to %s Journal Entry') % move.name)
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
                    if (not partner_id.property_account_position_id or
                        partner_id.property_account_position_id.name in (u'Kraj', u'Wspólnota')) and \
                            partner_id.company_type == 'company':
                        raise UserError(_("Please define Vat no. for vendor %s.") % partner_id.name)
                    else:
                        partner_vat = 'brak'

                partner_country_code = self.get_vat_code(partner_id=partner_id, skip_pl=True)
                numeric_vat = self.get_vat(partner_id=partner_id) or 'brak'
                address = ''

                if partner_id.street:
                    address += partner_id.street + ' '

                if partner_id.street2:
                    address += partner_id.street2 + ' '

                if partner_id.zip:
                    address += partner_id.zip + ' '

                if partner_id.city:
                    address += partner_id.city

                if not address:
                    raise UserError(_("Please add address of %s vendor.") % partner_id.name)

                inv = move
                invoice_reference = move.name
                partner_reference = inv and inv.ref or False
                main_reference = partner_reference or invoice_reference
                purchase_date = move.tax_date or move.date
                date_issue = move.date_issue
                move_taxes = {}
                tax_values = {}
                procedures_markers = {}
                date_received = False
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
                        date_received = inv.date_recived
                    if inv.purchase_doc_vdek:
                        purchase_doc_vdek = inv.purchase_doc_vdek

                for move_line in move.line_ids:
                    skip_month = False

                    if different_period_items:
                        if not move_line.date_manual:
                            if not move.tax_date:
                                continue

                            elif (move.tax_date >= wizard.date_from) and (move.tax_date <= wizard.date_to):
                                continue

                        else:
                            if not (move_line.date_manual < wizard.date_from or move_line.date_manual > wizard.date_to):
                                continue

                    else:
                        if move_line.date_manual:
                            if not move_line.date_manual >= wizard.date_from and \
                                    move_line.date_manual <= wizard.date_to:
                                continue

                        else:
                            if move.date < wizard.date_from or move.date > wizard.date_to:
                                if not move_line.date_manual and not move.tax_date:
                                    continue

                                if move.tax_date:
                                    if not move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                                        continue

                            if (move.date >= wizard.date_from) and (move.date <= wizard.date_to):
                                if move.tax_date and not move_line.date_manual:
                                    if not move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                                        continue

                    if wizard._name == 'wizard.jpk.vat.2020' and (
                            wizard.date_from.month != wizard.date_to.month and wizard.period != 1
                    ) and wizard.no_declaration_data is False:
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
                        credit = round(credit / 2.0, 2)
                        debit = round(debit / 2.0, 2)

                    if move_line.tax_basic_custom > 0.0:
                        if move.ref:
                            main_reference = move.ref

                        netto_name_custom = move_line.tax_line_id.tag_id.name
                        debit_custom_value = move_line.tax_basic_custom
                        credit_custom_value = 0
                        if purchase_taxes[netto_name_custom][0] not in move_taxes.keys():
                            move_taxes[purchase_taxes[netto_name_custom][0]] = {
                                'debit': float("{0:.2f}".format(debit_custom_value)),
                                'credit': float("{0:.2f}".format(credit_custom_value))
                            }
                        else:
                            move_taxes[purchase_taxes[netto_name_custom][0]]['debit'] += float(
                                "{0:.2f}".format(debit_custom_value)
                            )
                            move_taxes[purchase_taxes[netto_name_custom][0]]['credit'] += float(
                                "{0:.2f}".format(credit_custom_value)
                            )

                        if not skip_month:
                            sum_purchase_base += float("{0:.2f}".format(debit_custom_value))

                    else:
                        if netto_name in purchase_taxes.keys():
                            if purchase_taxes[netto_name][0] not in move_taxes.keys():
                                move_taxes[purchase_taxes[netto_name][0]] = {
                                    'debit': float("{0:.2f}".format(debit)),
                                    'credit': float("{0:.2f}".format(credit))
                                }
                            else:
                                move_taxes[purchase_taxes[netto_name][0]]['debit'] += float("{0:.2f}".format(debit))
                                move_taxes[purchase_taxes[netto_name][0]]['credit'] += float("{0:.2f}".format(credit))

                            if not skip_month:
                                sum_purchase_base += float("{0:.2f}".format(debit)) - float("{0:.2f}".format(credit))

                    if tax_name in purchase_taxes.keys():
                        if purchase_taxes[tax_name][1] not in move_taxes.keys():
                            move_taxes[purchase_taxes[tax_name][1]] = {
                                'debit': float("{0:.2f}".format(debit)),
                                'credit': float("{0:.2f}".format(credit))
                            }
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

                            elif (move.tax_date >= wizard.date_from) and (move.tax_date <= wizard.date_to):
                                continue

                        else:
                            if not (move_line.date_manual < wizard.date_from or move_line.date_manual > wizard.date_to):
                                continue
                    else:
                        if move_line.date_manual:
                            if not move_line.date_manual >= wizard.date_from and \
                                    move_line.date_manual <= wizard.date_to:
                                continue

                        else:
                            if move.date < wizard.date_from or move.date > wizard.date_to:
                                if not move_line.date_manual and not move.tax_date:
                                    continue

                                if move.tax_date:
                                    if not move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                                        continue

                            if (move.date >= wizard.date_from) and (move.date <= wizard.date_to):
                                if move.tax_date and not move_line.date_manual:
                                    if not move.tax_date >= wizard.date_from and move.tax_date <= wizard.date_to:
                                        continue

                    netto_name = move_line.tax_ids.tag_id.name
                    tax_name = move_line.tax_line_id.tag_id.name

                    if netto_name in purchase_taxes.keys() and purchase_taxes[netto_name][0] in \
                            move_taxes.keys() and len(purchase_taxes[netto_name]) == 2 and \
                            purchase_taxes[netto_name][1] not in move_taxes.keys():
                        move_taxes[purchase_taxes[netto_name][1]] = {
                            'debit': 0,
                            'credit': 0
                        }

                sorted_move_taxes = OrderedDict(sorted(move_taxes.items()))
                value_check = False
                for tax_name, amount in sorted_move_taxes.items():
                    if amount['debit'] != 0 or amount['credit'] != 0:
                        value = amount['debit'] - amount['credit']

                        if not skip_month:
                            if not value_check and value != 0:
                                value_check = True

                        tax_values[tax_name] = float("{0:.2f}".format(value))
                        report_tax_name = tax_name.replace('K', 'P')

                        if report_tax_name not in taxes_sum_dict.keys():
                            taxes_sum_dict[report_tax_name] = value
                        else:
                            taxes_sum_dict[report_tax_name] += value

                    else:
                        tax_values[tax_name] = 0

                if value_check:
                    lp += 1
                    purchase_dict[lp] = {
                        'country_code': partner_country_code,
                        'numeric_vat': numeric_vat,
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
                        'procedures_markers': procedures_markers.copy(),
                        'date_received': date_received,
                        'purchase_doc_vdek': purchase_doc_vdek
                    }

        if lp > 0:
            purchase_ctrl = {
                'lp': lp,
                'sum_taxes': float("{0:.2f}".format(sum_purchase_taxes)),
                'sum_base': float("{0:.2f}".format(sum_purchase_base))
            }
        else:
            if wizard._name == 'wizard.jpk.vat.2020':
                purchase_ctrl = {
                    'lp': 0,
                    'sum_taxes': 0,
                    'sum_base': 0
                }

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

        if wizard._name == 'wizard.jpk.vat.2020':
            vat_data.update({
                'P_38': (vat_data['P_16'] + vat_data['P_18'] + vat_data['P_20'] + vat_data['P_24'] + vat_data['P_26'] +
                         vat_data['P_28'] + vat_data['P_30'] + vat_data['P_32'] + vat_data['P_33'] + vat_data['P_34']) -
                        (vat_data['P_35'] - vat_data['P_36'])
            })
            vat_data.update({
                'P_48': (vat_data['P_39'] + vat_data['P_41'] + vat_data['P_43'] + vat_data['P_44'] + vat_data['P_45'] +
                         vat_data['P_46'] + vat_data['P_49'])
            })

            if (vat_data['P_38']) - vat_data['P_48'] > 0:
                vat_data.update({'P_51': (vat_data['P_38'] - vat_data['P_48'] - vat_data['P_49'] - vat_data['P_50'])})
            else:
                vat_data.update({'P_51': 0})

            if (vat_data['P_48']) - vat_data['P_38'] >= 0:
                vat_data.update({'P_53': (vat_data['P_48'] - vat_data['P_38'] + vat_data['P_52'])})
                vat_data.p_53_vdek = (vat_data['P_48'] - vat_data['P_38'] + vat_data['P_52'])
                wizard.p_53_vdek = vat_data.p_53_vdek
                vat_data.update({'P_54': wizard.p_54_vdek})
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
            if (vat_data['P_53']) > 0 and wizard.p_62_vdek > 0:
                vat_data.update({'P_62': wizard.p_62_vdek})
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
            'purchase_dict': purchase_dict,
            'sale_ctrl': sale_ctrl,
            'invoice_lines': invoice_line_dict,
            'purchase_invoice_lines': purchase_invoice_line_dict,
            'invoice_line_ctrl': invoice_line_ctrl,
            'purchase_invoice_line_ctrl': purchase_invoice_line_ctrl,
            'order_downpayment': order_downpayment,
            'purchase_order_downpayment': purchase_order_downpayment,
            'order_ctrl': order_ctrl,
            'purchase_order_ctrl': purchase_order_ctrl,
            'purchase_ctrl': purchase_ctrl,
            'taxes_sum_dict': vat_data,
            'ue_dict': ue_dict,
            'company_data': company_data
        }
        _logger.info(f'VALS DICT SALE: {vat_dict["sale_dict"]}')
        _logger.info(f'VALS DICT PURCHASE: {vat_dict["purchase_dict"]}')
        return vat_dict
