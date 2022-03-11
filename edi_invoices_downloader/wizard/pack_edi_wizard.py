from odoo import models, fields, api, _

from datetime import datetime
from zipfile import ZipFile

import logging
import base64

_logger = logging.getLogger(__name__)


class PackEDIWizard(models.TransientModel):
    _name = 'pack_edi_wizard'
    _description = 'Pack EDI Wizard'

    vendor_bill_check = fields.Boolean(string='Vendor Bills', default=True,
                                       help='Check this, if you want to package EDI files of vendor bills as well.')
    start_date = fields.Date(string='Start Date', required=True, help='Start date of collecting invoices for package.',
                             default=lambda x: datetime.now().strftime('%Y-%m') + '-01')
    end_date = fields.Date(string='End Date', required=True, help='End date of collecting invoices for package.',
                           default=fields.Date.today())

    def pack_edi_files(self):
        # TODO: CHECK EDI MODEL FOR FILES!!!
        # move_types = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
        edi_file_list = list()
        # invoices = self.env['account.move'].search([('move_type', 'in', move_types), ('state', '=', 'posted')])
        edi_recordset = self.env['account.edi.document'].search([
            ('move_id', '!=', False), ('attachment_id', '!=', False)
        ])

        zip_file = ZipFile('/odootest/test.zip', 'w')
        for edi_record in edi_recordset:
            _logger.info(f'\nEDI FILE: {edi_record.attachment_id.datas}\nTYPE: {type(edi_record.attachment_id.datas)}\n')
            file_content = base64.decodebytes(edi_record.attachment_id.datas)
            _logger.info(f'\nEDI FILE XML: {file_content}\nTYPE: {type(file_content)}\n')
            _logger.info(f'INV NAME 1: {edi_record.move_id.name}')
            inv_name = edi_record.move_id.name.replace('/', '_')
            _logger.info(f'INV NAME 2: {inv_name}')
            # f = open(f'/odootest/edi_{inv_name}.xml', 'wb')
            f = open(f'/odootest/edi_{inv_name}.xml', 'wb')
            # f.write(edi_record.attachment_id.datas)
            f.write(file_content)
            # zip_file.write(edi_record.attachment_id.datas)
            f.close()
            # zip_file.write(f'/odootest/edi_{inv_name}.xml')
            zip_file.write(f'/odootest/edi_{inv_name}.xml')
        zip_file.close()
