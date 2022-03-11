# -*- coding: utf-8 -*-
from openerp import api, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.exceptions import ValidationError
from openerp.tools import config
from io import BytesIO
import csv
import xlsxwriter

import logging

import base64
from xml.dom.minidom import Document
from odoo.addons.account_pl_cirrus.data.structures import JPK_KR
from openerp.addons.account_pl_declaration_data.utils.xml_utilities import xml_utilities

from pprint import pprint

_logger = logging.getLogger(__name__)

class ReportTrialBalance(models.AbstractModel):
    _name = 'report.account_pl_cirrus.report_trial_balance'

    def _get_account_values(self, account_ids):
        ''' based on how these credit/debit values are calculated in core modules '''

        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"', '')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(account_ids),) + tuple(where_params)
        self.env.cr.execute(request, params)

        account_result = {}
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        payable_recivable_type = self.env['account.account.type'].search([('type','in',['payable', 'receivable'])]).ids
        pay_rec_acc_ids = self.env['account.account'].search([('user_type_id','in', payable_recivable_type)]).ids

        for account_id in account_result:
            if not account_id in pay_rec_acc_ids:
                continue
            request = ("SELECT account_id AS acc_id, SUM(debit) AS debit, SUM(credit) AS credit, account_move_line.partner_id AS partner" +\
                       " FROM " + tables + " WHERE account_id = %s" + filters + " GROUP BY account_id, account_move_line.partner_id")
            params = (tuple([account_id]),) + tuple(where_params)
            self.env.cr.execute(request, params)
            partners_details = self.env.cr.dictfetchall()
            account_result[account_id]['partners'] = partners_details

        # pprint(account_result)
        if self.env.context.get('opening_balance'):
            current_year_earning_account = self.env.ref('account.data_unaffected_earnings')
            initial_balance_account_types = self.env['account.account.type'].search([('include_initial_balance', '=', False)])

            if not current_year_earning_account:
                raise ValidationError(_('Current Year Earnings account type is not found. Please add account.data_unaffected_earnings ID to account type or use Opening Journal.'))

            financial_result_account_id = self.env['account.account'].search([('deprecated', '=', False), ('user_type_id', '=', current_year_earning_account.id)])
            initial_balance_account_ids = self.env['account.account'].search([('deprecated', '=', False), ('user_type_id', 'in', initial_balance_account_types.ids)])

            if len(financial_result_account_id) != 1:
                raise ValidationError(_('Financial Result account not found. Please add {0} account type to financial result account or use Opening Journal'.format(current_year_earning_account.name)))

            financial_result_dict = account_result.get(financial_result_account_id.id, {'credit': 0.0, 'debit': 0.0})
            for account_id in initial_balance_account_ids:
                result = account_result.get(account_id.id)
                if result:
                    financial_result_dict['credit'] += result['debit']
                    financial_result_dict['debit'] += result['credit']
                    account_result[account_id.id] = {'debit': 0.0, 'credit': 0.0}

            account_result[financial_result_account_id.id] = financial_result_dict.copy()

        return account_result

    def _get_account_dict(self, accounts):
        account_dict = {}
        for account in accounts:
            if account.deprecated or account.code[0] == '9':
                continue
            account_dict[account.id] = {'ob_debit': 0, 'ob_credit': 0, 'month_debit': 0,
                'month_credit': 0, 'year_debit': 0, 'year_credit':0, 'balance_debit': 0,
                'balance_credit': 0,
                'partners': {} }

        return account_dict

    def _get_lines(self, display_account, ob_journal_id, ob_in_sales, ob_sum_all):
        accounts_all = self.env['account.account'].search([('deprecated', '=', False)])
        accounts = self.env['account.account']
        for acc in accounts_all:
            if acc.code[0] == '9':
                continue
            accounts += acc
        account_dict = self._get_account_dict(accounts)
        dict_positions = {'ob_debit': 0, 'ob_credit': 0, 'month_debit': 0,
            'month_credit': 0, 'year_debit': 0, 'year_credit':0, 'balance_debit': 0,
            'balance_credit': 0, 'code' : 'Partner'}

        # obroty narastajaco
        ctx = self.env.context.copy()
        if ob_sum_all:
            ctx.update({'journal_ids': [j_id for j_id in self.env.context['journal_ids']]})
        else:
            ctx.update({'journal_ids': [j_id for j_id in self.env.context['journal_ids'] if j_id != ob_journal_id]})
        account_year_values = self.with_context(ctx)._get_account_values(accounts.ids)

        for account_id in account_year_values:
            account_dict[account_id]['year_debit'] += account_year_values[account_id]['debit']
            account_dict[account_id]['year_credit'] += account_year_values[account_id]['credit']
            if account_year_values[account_id].get('partners'):
                for partner in account_year_values[account_id]['partners']:
                    if not account_dict[account_id]['partners'].get(partner['partner']):
                        account_dict[account_id]['partners'][partner['partner']] = dict_positions.copy()
                    account_dict[account_id]['partners'][partner['partner']]['year_debit'] += partner['debit']
                    account_dict[account_id]['partners'][partner['partner']]['year_credit'] += partner['credit']




        # obroty miesiaca
        ctx = self.env.context.copy()
        if ob_sum_all:
            ctx.update({'date_from': '{0}01'.format(ctx['date_to'][:8]), 'journal_ids': [j_id for j_id in self.env.context['journal_ids']]})
        else:
            ctx.update({'date_from': '{0}01'.format(ctx['date_to'][:8]), 'journal_ids': [j_id for j_id in self.env.context['journal_ids'] if j_id != ob_journal_id]})
        account_month_values = self.with_context(ctx)._get_account_values(accounts.ids)

        for account_id in account_month_values:
            account_dict[account_id]['month_debit'] += account_month_values[account_id]['debit']
            account_dict[account_id]['month_credit'] += account_month_values[account_id]['credit']
            if account_month_values[account_id].get('partners'):
                for partner in account_month_values[account_id]['partners']:
                    if not account_dict[account_id]['partners'].get(partner['partner']):
                        account_dict[account_id]['partners'][partner['partner']] = dict_positions.copy()
                    account_dict[account_id]['partners'][partner['partner']]['month_debit'] += partner['debit']
                    account_dict[account_id]['partners'][partner['partner']]['month_credit'] += partner['credit']

        # bilans otwarcia
        ctx = self.env.context.copy()
        if ob_sum_all:
            date_from = datetime.strptime(ctx['date_from'], DF)
            date_from -= relativedelta(days=1)
            ctx.update({'journal_ids': [j_id for j_id in self.env.context['journal_ids']], 'date_to': datetime.strftime(date_from, DF), 'date_from': False, 'opening_balance': True})
        else:
            ctx.update({'journal_ids': [ob_journal_id], 'date_from': '{0}-01-01'.format(ctx['date_to'][:4])})
        account_ob_values = self.with_context(ctx)._get_account_values(accounts.ids)

        for account_id in account_ob_values:
            debit_diff = account_ob_values[account_id]['debit']
            credit_diff = account_ob_values[account_id]['credit']
            if account_ob_values[account_id].get('partners'):
                debit_diff = 0
                credit_diff = 0
                for partner in account_ob_values[account_id]['partners']:
                    if not account_dict[account_id]['partners'].get(partner['partner']):
                        account_dict[account_id]['partners'][partner['partner']] = dict_positions.copy()
                    if partner['debit'] == partner['credit']:
                        continue
                    elif partner['debit'] > partner['credit']:
                        differenece = partner['debit'] - partner['credit']
                        account_dict[account_id]['partners'][partner['partner']]['ob_debit'] += differenece
                        debit_diff += differenece
                        if ob_in_sales:
                            account_dict[account_id]['partners'][partner['partner']]['year_debit'] += differenece
                    else:
                        differenece = partner['credit'] - partner['debit']
                        account_dict[account_id]['partners'][partner['partner']]['ob_credit'] += differenece
                        credit_diff += differenece
                        if ob_in_sales:
                            account_dict[account_id]['partners'][partner['partner']]['year_credit'] += differenece
                    # if ob_in_sales:
                    #     account_dict[account_id]['partners'][partner['partner']]['year_debit'] += partner['debit']
                    #     account_dict[account_id]['partners'][partner['partner']]['year_credit'] += partner['credit']

            account_dict[account_id]['ob_debit'] += debit_diff
            account_dict[account_id]['ob_credit'] += credit_diff
            if ob_in_sales:
                account_dict[account_id]['year_debit'] += debit_diff
                account_dict[account_id]['year_credit'] += credit_diff




        account_res = []
        account_sums = {'ob_debit': 0, 'ob_credit': 0, 'month_debit': 0, 'month_credit': 0,
                        'year_debit': 0, 'year_credit': 0, 'balance_debit': 0, 'balance_credit': 0}

        # obliczanie sald i sum

        for account_id in account_dict:
            balance_deb = account_dict[account_id]['year_debit'] + account_dict[account_id]['ob_debit']
            balance_cred = account_dict[account_id]['year_credit'] + account_dict[account_id]['ob_credit']
            if ob_in_sales:
                balance_deb = account_dict[account_id]['year_debit']
                balance_cred = account_dict[account_id]['year_credit']

            if balance_deb > balance_cred:
                sum_value = balance_deb - balance_cred
                account_dict[account_id]['balance_debit'] = sum_value
            elif balance_cred > balance_deb:
                sum_value = balance_cred - balance_deb
                account_dict[account_id]['balance_credit'] = sum_value

            if account_dict[account_id].get('partners'):
                debit_value = 0
                credit_value = 0
                for partner in account_dict[account_id]['partners']:
                    # if not account_dict[account_id]['partners'].get(partner['partner']):
                    #     account_dict[account_id]['partners'][partner['partner']] = dict_positions.copy()
                    partner_name = self.env['res.partner'].search([('id','=',partner)]).name
                    account_dict[account_id]['partners'][partner]['name'] = partner_name

                    partner_balance_deb = account_dict[account_id]['partners'][partner]['year_debit'] + account_dict[account_id]['partners'][partner]['ob_debit']
                    partner_balance_cred =  account_dict[account_id]['partners'][partner]['year_credit'] + account_dict[account_id]['partners'][partner]['ob_credit']
                    if ob_in_sales:
                        partner_balance_deb = account_dict[account_id]['partners'][partner]['year_debit']
                        partner_balance_cred =  account_dict[account_id]['partners'][partner]['year_credit']

                    if partner_balance_deb > partner_balance_cred:
                        sum_value = partner_balance_deb - partner_balance_cred
                        account_dict[account_id]['partners'][partner]['balance_debit'] = sum_value
                        debit_value += sum_value
                    elif partner_balance_cred > partner_balance_deb:
                        sum_value = partner_balance_cred - partner_balance_deb
                        account_dict[account_id]['partners'][partner]['balance_credit'] = sum_value
                        credit_value += sum_value

                account_dict[account_id]['balance_debit'] = debit_value
                account_dict[account_id]['balance_credit'] = credit_value

            # balance_cred = (account_dict[account_id]['year_debit'] + account_dict[account_id]['ob_debit'])
            # balance_deb = (account_dict[account_id]['year_credit'] + account_dict[account_id]['ob_credit'])
            # balance = (account_dict[account_id]['year_debit'] + account_dict[account_id]['ob_debit']) - (
            #             account_dict[account_id]['year_credit'] + account_dict[account_id]['ob_credit'])
            # account = self.env['account.account'].browse(account_id)
            # if account.user_type_id.type in ['payable', 'receivable']:
            #     account_dict[account_id]['balance_debit'] = abs(balance_deb)
            #     account_dict[account_id]['balance_credit'] = abs(balance_cred)
            # else:
            #     if balance > 0:
            #         account_dict[account_id]['balance_debit'] = balance
            #     elif balance < 0:
            #         account_dict[account_id]['balance_credit'] = abs(balance)
            #
            # if account_dict[account_id].get('partners'):
            #     for partner in account_dict[account_id]['partners']:
            #         partner_name = self.env['res.partner'].search([('id','=',partner)]).name
            #         account_dict[account_id]['partners'][partner]['name'] = partner_name
            #         partner_balance_cred = account_dict[account_id]['partners'][partner]['year_debit'] + account_dict[account_id]['partners'][partner]['ob_debit']
            #         partner_balance_deb = account_dict[account_id]['partners'][partner]['year_credit'] + account_dict[account_id]['partners'][partner]['ob_credit']
            #         account_dict[account_id]['partners'][partner]['balance_debit'] = partner_balance_cred
            #         account_dict[account_id]['partners'][partner]['balance_credit'] = abs(partner_balance_deb)


            account = self.env['account.account'].browse(account_id)
            for column in account_dict[account_id]:
                if column == 'partners':
                    continue
                account_sums[column] += account_dict[account_id][column]

            if display_account == 'all' or any(account_dict[account_id].values()):
                account_dict[account_id]['name'] = account.name
                account_dict[account_id]['code'] = account.code
                account_res.append(account_dict[account_id])

        account_res = sorted(account_res, key=lambda k: k['code'])

        return (account_res, account_sums)

    def pl_rounding(self, value):
        return '{:.2f}'.format(value).replace('.',',')


    @api.model
    def _get_report_values(self, docids, data=None):
        # report_obj = self.env['report']
        display_account = data['form'].get('display_account')
        account_res, account_sums = self.with_context(data['form'].get('used_context'))._get_lines(
            display_account, data['ob_journal_id'], data['ob_in_sales'], data['ob_sum_all'])
        docargs = {
            'doc_ids': self._ids,
            'doc_model': self._name,
            'docs': self,
            'data': data['form'],
            'account_res': account_res,
            'account_sums': account_sums,
            'ob_in_sales': data['ob_in_sales']
        }
        return docargs


    def generate_xml(self, wizard, data):
        VatUtils = self.env['wizard.vat.utils']

        VatUtils.check_company_data(wizard)
        company_id = wizard.company_id
        doc = Document()
        display_account = data['form'].get('display_account')
        account_res, account_sums = self.with_context(data['form'].get('used_context'))._get_lines(
            display_account, data['ob_journal_id'], data['ob_in_sales'], data['ob_sum_all'])
        acc_details = {
            'account_res':account_res,
            'account_sums':account_sums,
        }
        # journal = data['ob_journal_id']
        account_dict = VatUtils.get_account_details(wizard, acc_details)
        xml_element = VatUtils.convert_to_xml(JPK_KR, wizard, doc, account_dict)
        ready_xml = xml_element.toprettyxml(indent="  ", encoding="UTF-8")
        ready_xml = xml_utilities.check_xml_heading(ready_xml)
        trial_balance_file = base64.encodebytes(ready_xml)
        try:
            xml_utilities.check_xml_file(ready_xml, 'account_pl_cirrus/schemes/Schemat_JPK_KR(1)_v1-0.xsd')
        except Exception as e:
            e = str(e)
            raise ValidationError(_('Wrong Data in XML file!\nTry to solve the problem according to message below:\n\n%s')%e)

        return trial_balance_file


    def _build_csv(self, data, acc_details):
        data_dir = config['data_dir']
        # pprint(acc_details)
        with open(data_dir + '/report.csv', 'w', newline='') as file:
            report = csv.writer(file)
            report.writerow(["Konta", "", "Bilans otwarcia", "", "Obroty za "+ data['date_to'].strftime("%Y-%m"), "", "Obroty narastająco od początku roku", "", "Salda na dzień "+data['date_to'].strftime("%Y-%m-%d")])
            report.writerow(["Kod", "Nazwa", "Wn", "Ma", "Wn", "Ma", "Wn", "Ma", "Wn", "Ma"])
            for account in acc_details['account_res']:
                report.writerow([account['code'],
                                account['name'],
                                account['ob_debit'],
                                account['ob_credit'],
                                account['month_debit'],
                                account['month_credit'],
                                account['year_debit'],
                                account['year_credit'],
                                account['balance_debit'],
                                account['balance_credit']])
                if account['partners'] != {}:
                    for partner_id in account['partners']:
                        report.writerow([account['partners'][partner_id]['code'],
                                        account['partners'][partner_id]['name'],
                                        account['partners'][partner_id]['ob_debit'],
                                        account['partners'][partner_id]['ob_credit'],
                                        account['partners'][partner_id]['month_debit'],
                                        account['partners'][partner_id]['month_credit'],
                                        account['partners'][partner_id]['year_debit'],
                                        account['partners'][partner_id]['year_credit'],
                                        account['partners'][partner_id]['balance_debit'],
                                        account['partners'][partner_id]['balance_credit']])

            sum = acc_details['account_sums']
            report.writerow(["",
                            "Suma razem",
                            sum['ob_debit'],
                            sum['ob_credit'],
                            sum['month_debit'],
                            sum['month_credit'],
                            sum['year_debit'],
                            sum['year_credit'],
                            sum['balance_debit'],
                            sum['balance_credit']])
        with open(data_dir + '/report.csv', 'r') as file:
            data = file.read()
        csv_bytes = data.encode()
        csv_bytes = base64.encodestring(csv_bytes)
        return csv_bytes


    def generate_csv(self, wizard, data):
        VatUtils = self.env['wizard.vat.utils']

        VatUtils.check_company_data(wizard)
        company_id = wizard.company_id
        doc = Document()
        display_account = data['form'].get('display_account')
        account_res, account_sums = self.with_context(data['form'].get('used_context'))._get_lines(
            display_account, data['ob_journal_id'], data['ob_in_sales'], data['ob_sum_all'])
        acc_details = {
            'account_res':account_res,
            'account_sums':account_sums,
        }
        # pprint(acc_details)
        csv_file = self._build_csv(acc_details=acc_details, data=data)
        return csv_file



    def _build_xlsx(self, data, acc_details):
        data_dir = config['data_dir']

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        report = workbook.add_worksheet()

        row = 0
        col = 0
        header = ["Konta", "", "Bilans otwarcia", "", "Obroty za "+ data['date_to'].strftime("%Y-%m"), "", "Obroty narastająco od początku roku", "", "Salda na dzień "+data['date_to'].strftime("%Y-%m-%d")]
        header_2 = ["Kod", "Nazwa", "Wn", "Ma", "Wn", "Ma", "Wn", "Ma", "Wn", "Ma"]
        for item in header:
            report.write(row, col, item)
            col += 1

        row += 1
        col = 0
        for item in header_2:
            report.write(row, col, item)
            col += 1

        col = 0
        for account in acc_details['account_res']:
            row += 1
            report.write(row, col, account['code'])
            report.write(row, col + 1, account['name'])
            report.write(row, col + 2, account['ob_debit'])
            report.write(row, col + 3, account['ob_credit'])
            report.write(row, col + 4, account['month_debit'])
            report.write(row, col + 5, account['month_credit'])
            report.write(row, col + 6, account['year_debit'])
            report.write(row, col + 7, account['year_credit'])
            report.write(row, col + 8, account['balance_debit'])
            report.write(row, col + 9, account['balance_credit'])
            if account['partners'] != {}:
                for partner_id in account['partners']:
                    row += 1
                    report.write(row, col, account['partners'][partner_id]['code'])
                    report.write(row, col + 1, account['partners'][partner_id]['name'])
                    report.write(row, col + 2, account['partners'][partner_id]['ob_debit'])
                    report.write(row, col + 3, account['partners'][partner_id]['ob_credit'])
                    report.write(row, col + 4, account['partners'][partner_id]['month_debit'])
                    report.write(row, col + 5, account['partners'][partner_id]['month_credit'])
                    report.write(row, col + 6, account['partners'][partner_id]['year_debit'])
                    report.write(row, col + 7, account['partners'][partner_id]['year_credit'])
                    report.write(row, col + 8, account['partners'][partner_id]['balance_debit'])
                    report.write(row, col + 9, account['partners'][partner_id]['balance_credit'])

        sum = acc_details['account_sums']
        row += 1
        col = 0
        report.write(row, col + 1, 'Suma razem')
        report.write(row, col + 2, sum['ob_debit'])
        report.write(row, col + 3, sum['ob_credit'])
        report.write(row, col + 4, sum['month_debit'])
        report.write(row, col + 5, sum['month_credit'])
        report.write(row, col + 6, sum['year_debit'])
        report.write(row, col + 7, sum['year_credit'])
        report.write(row, col + 8, sum['balance_debit'])
        report.write(row, col + 9, sum['balance_credit'])
        workbook.close()

        xlsx_bytes = base64.encodestring(output.getvalue())

        return xlsx_bytes



    
    def generate_xlsx(self, wizard, data):
        VatUtils = self.env['wizard.vat.utils']

        VatUtils.check_company_data(wizard)
        company_id = wizard.company_id
        doc = Document()
        display_account = data['form'].get('display_account')
        account_res, account_sums = self.with_context(data['form'].get('used_context'))._get_lines(
            display_account, data['ob_journal_id'], data['ob_in_sales'], data['ob_sum_all'])
        acc_details = {
            'account_res':account_res,
            'account_sums':account_sums,
        }
        # pprint(acc_details)
        xlsx_file = self._build_xlsx(acc_details=acc_details, data=data)
        return xlsx_file
