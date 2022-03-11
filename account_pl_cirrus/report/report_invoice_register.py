# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import UserError
from collections import OrderedDict
import datetime

import logging
from pprint import pprint

_logger = logging.getLogger(__name__)


class ReportInvoiceRegister(models.AbstractModel):
    _name = 'report.account_pl_cirrus.report_invoice_register'

    def _get_report_values(self, docids, data=None):
        doc_model = data['wizard_model']
        doc_ids = data['wizard_id']
        if data['vat_dict']['purchase_ctrl'] == {}:
            data['vat_dict']['purchase_ctrl'] = False
            data['vat_dict']['purchase_dict'] = False
        if data['vat_dict']['sale_ctrl'] == {}:
            data['vat_dict']['sale_ctrl'] = False
            data['vat_dict']['sale_dict'] = False
        # pprint(data['vat_dict']['sale_dict'])
        return {
            'doc_ids': doc_ids,
            'doc_model': doc_model,
            'docs': self.env[doc_model].browse(doc_ids),
            'data': data,
            'VatUtils': self.env['wizard.vat.utils'],
            'wizard': self.env[doc_model].browse(doc_ids),
            'OrderedDict': OrderedDict,
            'sorted': sorted,
            'strptime': datetime.datetime.strptime,
        }
