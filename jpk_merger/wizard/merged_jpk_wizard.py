from odoo import models, fields, api, _

from odoo.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period

from xml.etree import ElementTree
from datetime import datetime
import logging
import base64

_logger = logging.getLogger(__name__)


class MergedJPKWizard(models.TransientModel):
    _name = 'merged_jpk_wizard'
    _description = 'Merged JPK Wizard'
    _inherit = 'account.common.report'

    @api.onchange('date_from', 'period')
    def _set_date_to(self):
        if self.period:
            months, quarter = self.period.partition("/")[::2]
            data_to_period.set_date_to(self, months, quarter)
        else:
            data_to_period.set_date_to(self)

    period = fields.Selection([
        ('1', 'Monthly'),
        ('3/1', '1st Quarter'),
        ('3/2', '2nd Quarter'),
        ('3/3', '3rd Quarter'),
        ('3/4', '4th Quarter')
    ], string='Period Type', default='1', required=True)
    date_from = fields.Date(string='Start Date', required=True,
                            default=lambda x: datetime.now().strftime('%Y-%m') + '-01')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    merged_jpk_file = fields.Binary(string='Merged JPK File', readonly=True)
    merged_jpk_filename = fields.Char(string='Merged JPK Filename', readonly=True)
    cash_basis_pl = fields.Boolean(string='Cash basis',
                                   help="Select this if you're using cash basis method specific for polish accounting.")
    correction_number = fields.Integer('Correction No.', default=0, required=True,
                                       help='Value "0" means generating new file for provided period.'
                                            'Every next value: "1", "2", "3" etc. means correction number.')
    error_message = fields.Text(string='Message')

    @staticmethod
    def merge_jpk(files):
        _logger.info(f'MERGER METHOD START!')
        body = None
        for file in files:
            _logger.info(f'BEGIN: {body}')
            _logger.info(f'FILE 1: {file}')
            data = ElementTree.fromstring(file)
            _logger.info(f'DATA 1: {data}')
            child_data = list(data)
            _logger.info(f'CHILD DATA: {child_data}')
            header_data, company_data, remaining_data = child_data[0], child_data[1], child_data[2:]
            _logger.info(f'HEADER DATA: {header_data}')
            _logger.info(f'COMPANY DATA: {company_data}')
            _logger.info(f'REMAINING DATA: {remaining_data}')

            if body is None:
                body = data
                _logger.info(f'BODY 1: {body}')
            else:
                _logger.info(f'BODY 2: {body}')
                for element in remaining_data:
                    body.extend(element)
                    _logger.info(f'BODY LOOP: {body}')

        if body is not None:
            _logger.info(f'BODY 3: {body}')
            result = ElementTree.tostring(body)
            result = base64.encodebytes(result)
            return result

    def _print_report(self, data):
        _logger.info(f'PRINT REPORT BEGIN: {self} / {data}')
        data['company_id'] = self.company_id
        data_to_period.check_dates(self)

        jpk_fa_file = self.env['report.jpk.fa.3'].render_xml(self)
        _logger.info(f'JPK FA DATA: {jpk_fa_file}')
        decoded_jpk_fa_file = base64.decodebytes(jpk_fa_file)
        _logger.info(f'JPK FA DATA DECODED: {decoded_jpk_fa_file}')
        _logger.info(f'JPK FA RENDERED!')

        jpk_fa_bill_file = self.env['report_jpk_fa_bill'].render_xml(self)
        _logger.info(f'JPK VAT DATA: {jpk_fa_bill_file}')
        decoded_jpk_fa_bill_file = base64.decodebytes(jpk_fa_bill_file)
        _logger.info(f'JPK VAT DATA DECODED: {decoded_jpk_fa_bill_file}')
        _logger.info(f'JPK VAT RENDERED!')

        result = self.merge_jpk([decoded_jpk_fa_file, decoded_jpk_fa_bill_file])
        self.write({
            'merged_jpk_file': result,
            'merged_jpk_filename': 'Merged-JPK-' + datetime.now().strftime('%Y-%m-%d') + '.xml'
        })

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'res_model': self._name,
            'target': 'new',
            'context': {
                'default_model': self._name,
            },
        }
