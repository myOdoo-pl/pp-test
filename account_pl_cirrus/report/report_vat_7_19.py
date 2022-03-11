# -*- coding: utf-8 -*-

import base64
from xml.dom.minidom import Document

from openerp import api, models, fields, _
from collections import OrderedDict

from openerp.exceptions import UserError
from openerp.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period, REVERSE_QUARTER_MAP
from openerp.addons.account_pl_declaration_data.utils.xml_utilities import xml_utilities
from odoo.addons.account_pl_cirrus.data.structures import JPK_VAT_7_19
from openerp.exceptions import ValidationError
import logging
from pprint import pprint

_logger = logging.getLogger(__name__)

# MIN_CELL_VALUE_EQ_0_CELL_NUMBERS = ['P_52', 'P_53', 'P_54', 'P_56']


class ReportVat7_19(models.AbstractModel):
    _name = 'report.account_pl_cirrus.report_vat_7_19'

    # TODO: do we even need this?
    def _save_vat_config(self, data):
        vat_config = self.env['vat.7.config'].search(
            [['period_month', '=', data['month']], ['period_year', '=', data['year']]])
        if vat_config:
            vat_config.write({
                'date': fields.Datetime.now(),
                'transition_amount': data['P_62']
            })
        else:
            self.env['vat.7.config'].create({
                'date': fields.Datetime.now(),
                'period_month': data['month'],
                'period_year': data['year'],
                'transition_amount': data['P_62']
            })
        return True

    def _get_transition_amount(self, data):
        if 'vat-7k' in data.keys() and data['vat-7k']:
            if int(data['quarter']) == 1:
                last_period_quarter = '4'
                last_period_year = str(int(data['year']) - 1)
            else:
                last_period_quarter = str(int(data['quarter']) - 1)
                last_period_year = data['year']

            last_period_declarations = self.env['vat.7k.config'].search([['period_quarter', '=', last_period_quarter], ['period_year', '=', last_period_year]])
        else:
            if int(data['month']) == 1:
                last_period_month = '12'
                last_period_year = str(int(data['year']) - 1)
            else:
                last_period_month = "{:02d}".format(int(data['month']) - 1)
                last_period_year = data['year']

            last_period_declarations = self.env['vat.7.config'].search([['period_month', '=', last_period_month], ['period_year', '=', last_period_year]])

        if last_period_declarations:
            last_declaration = reduce(
                lambda x, y: x.date > y.date and x or y, last_period_declarations)
            return last_declaration.transition_amount or 0
        else:
            return 0

    @api.model
    def _get_report_values(self, docids, data=None):
        doc_model = data['wizard_model']
        doc_ids = data['wizard_id']
        # pprint(data)
        return {
            'doc_ids': doc_ids,
            'doc_model': doc_model,
            'docs': self.env[doc_model].browse(doc_ids),
            'data': data,
            'vat_data': data['vat_dict']['taxes_sum_dict'],
            'VatUtils': self.env['wizard.vat.utils'],
            'wizard': self.env[doc_model].browse(doc_ids)
        }


    def render_xml(self, data):
        _logger.warn("Generating XML!")
        VatUtils = self.env['wizard.vat.utils']

        wizard = self.env[data['wizard_model']].browse(data['wizard_id'])
        vat_dict = data['vat_dict']

         # TODO:
         # self._save_vat_config(data)
         # data['P_42'] = self._get_transition_amount(data)

        doc = Document()
        xml_element = VatUtils.convert_to_xml(JPK_VAT_7_19, wizard, doc, vat_dict)
        ready_xml = xml_element.toprettyxml(indent="  ", encoding="UTF-8")
        ready_xml = xml_utilities.check_xml_heading(ready_xml)
        vat7_file = base64.encodestring(ready_xml)
        try:
            xml_utilities.check_xml_file(ready_xml, 'account_pl_cirrus/schemes/VAT-7(19)_v1-0.xsd')
        except Exception as e:
            e = str(e)
            raise ValidationError(_('Wrong Data in XML file!\nTry to solve the problem according to message below:\n\n%s')%e)
        return vat7_file
