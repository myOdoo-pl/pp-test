# -*- coding: utf-8 -*-

from datetime import datetime as dt
from datetime import date
from openerp import models, fields, api, _
from openerp.exceptions import UserError

from pprint import pprint
import logging
_logger = logging.getLogger(__name__)


class AccountReportTrialBalance(models.TransientModel):
    _name = "account.report.trial_balance"
    _description = "Trial Balance Report"
    _inherit = "account.common.report"

    date_from = fields.Date(string='Start Date', default=lambda self: date(day=1, month=1, year=dt.now().year))
    date_to = fields.Date(string='End Date', default=fields.Date.today())
    ob_journal_id = fields.Many2one('account.journal', "Opening Balance Journal")#, required=True
    ob_in_sales = fields.Boolean('Opening balance in yearly turnover')
    ob_sum_all = fields.Boolean('Compute opening balance from all journals')
    display_account = fields.Selection([('all','All'), ('not_zero','With balance is not equal to 0')],
                                        string='Display Accounts', required=True, default='all')
    trial_balance_file = fields.Binary('Trial Balance File', readonly=True)
    trial_balance_filename = fields.Char('Trial Balance Filename', size=64, readonly=True)

    report_file_csv = fields.Binary("Raport csv", readonly=True)
    report_file_csv_name = fields.Char("Raport Name", readonly=True)

    report_file_xlsx = fields.Binary("Raport Excel", readonly=True)
    report_file_xlsx_name = fields.Char("Raport Name", readonly=True)


    def _print_report(self, data):
        # _logger.warning("\n\ncontext %s\n\n"%str(self.env.context))
        if self.env.context.get('xml') or self.env.context.get('csv') or self.env.context.get('xlsx'):
            # pprint(data)
            data['ob_sum_all'] = self.ob_sum_all
            data['ob_journal_id'] = self.ob_journal_id.id
            data['ob_in_sales'] = self.ob_in_sales
            data['date_from'] = self.date_from
            data['date_to'] = self.date_to
            if self.env.context.get('xml'):
                jpk_file =  self.env['report.account_pl_cirrus.report_trial_balance'].generate_xml(self, data=data)
                self.write({'trial_balance_file': jpk_file, 'trial_balance_filename':'JPK-KR-' + dt.now().strftime('%Y-%m-%d') + ".xml"})
            elif self.env.context.get('xlsx'):
                xlsx_file = self.env['report.account_pl_cirrus.report_trial_balance'].generate_xlsx(self, data=data)
                self.write({'report_file_xlsx': xlsx_file, 'report_file_xlsx_name': 'ZSiO: '+ dt.now().strftime('%Y-%m-%d') + ".xlsx"})
            else:
                csv_file = self.env['report.account_pl_cirrus.report_trial_balance'].generate_csv(self, data=data)
                self.write({'report_file_csv': csv_file, 'report_file_csv_name': 'ZSiO: '+ dt.now().strftime('%Y-%m-%d') + ".csv"})
            return {'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'res_id': self.id,
                        'res_model': self._name,
                        'target': 'new',
                        'context': {
                            'default_model': self._name,
                        },
                    }

        else:

            _logger.warn("Printing Trial Balance!")
            if self.date_from > self.date_to:
                raise UserError(_("Start date must be before End Date!"))
            data['ob_sum_all'] = self.ob_sum_all
            data['ob_journal_id'] = self.ob_journal_id.id
            data['ob_in_sales'] = self.ob_in_sales
            data['date_from'] = self.date_from
            data['date_to'] = self.date_to
            data['form']['display_account'] = self.display_account
            return self.env.ref('account_pl_cirrus.account_trial_balance').report_action(self, data=data)

    # FIX datetime -> string
    def _build_contexts(self, data):
        res = super(AccountReportTrialBalance, self)._build_contexts(data)
        res['date_from'] = str(res['date_from'])
        res['date_to'] = str(res['date_to'])
        return res
