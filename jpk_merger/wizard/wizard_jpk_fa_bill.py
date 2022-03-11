from odoo import models, fields, api, _

from odoo.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period, REVERSE_QUARTER_MAP

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class WizardJpkFaBill(models.TransientModel):
    _name = 'wizard_jpk_fa_bill'
    _inherit = 'account.common.report'

    period = fields.Selection([
        ('1', 'Monthly'),
        ('3/1', '1st Quarter'),
        ('3/2', '2nd Quarter'),
        ('3/3', '3rd Quarter'),
        ('3/4', '4th Quarter')
    ], 'Period Type', default='1', required=True)
    date_from = fields.Date(string='Start Date', required=True,
                            default=lambda x: datetime.now().strftime('%Y-%m') + '-01')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    jpk_fa_bill_file = fields.Binary(string='JPK FA BILL File', readonly=True)
    jpk_fa_bill_filename = fields.Char(string='Merged JPK Filename', readonly=True)
    cash_basis_pl = fields.Boolean(string='Cash basis',
                                   help="Select this if you're using cash basis method specific for polish accounting.")
    correction_number = fields.Integer('Correction No.', default=0, required=True,
                                       help='Value "0" means generating new file for provided period.'
                                            'Every next value: "1", "2", "3" etc. means correction number.')
    error_message = fields.Text(string='Message')

    @api.onchange('date_from', 'period')
    def _set_date_to(self):
        if self.period:
            months, quarter = self.period.partition("/")[::2]
            data_to_period.set_date_to(self, months, quarter)
        else:
            data_to_period.set_date_to(self)

    def _print_report(self, data):
        data['company_id'] = self.company_id
        data_to_period.check_dates(self)
        jpk_file = self.env['report_jpk_fa_bill'].render_xml(self)
        self.write({
            'jpk_fa_bill_file': jpk_file,
            'jpk_fa_bill_filename': 'JPK-FA-BILL-' + datetime.now().strftime('%Y-%m-%d') + '.xml'
        })

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'res_model': self._name,
            'target': 'new',
            'context': {
                'default_model': self._name
            }
        }
