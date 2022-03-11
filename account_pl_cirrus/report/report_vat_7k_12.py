# -*- coding: utf-8 -*-

import base64
from xml.dom.minidom import Document

from openerp import api, models, fields, _

from openerp.exceptions import UserError
from openerp.addons.account_pl_declaration_data.utils.xml_utilities import xml_utilities
from odoo.addons.account_pl_cirrus.data.structures import JPK_VAT_7K_12
from openerp.exceptions import ValidationError
import logging
from pprint import pprint

_logger = logging.getLogger(__name__)


class ReportVat7k_12(models.AbstractModel):
    _name = 'report.account_pl_cirrus.report_vat_7k_12'

    def _save_vat_config(self, data):
        vat_config = self.env['vat.7k.config'].search(
            [['period_quarter', '=', data['quarter']], ['period_year', '=', data['year']]])
        if vat_config:
            vat_config.write({
                'date': fields.Datetime.now(),
                'transition_amount': data['P_62']
            })
        else:
            self.env['vat.7k.config'].create({
                'date': fields.Datetime.now(),
                'period_quarter': data['quarter'],
                'period_year': data['year'],
                'transition_amount': data['P_62']
            })
        return True

    def _get_transition_amount(self, data):
        if int(data['quarter']) == 1:
            last_period_quarter = '4'
            last_period_year = str(int(data['year']) - 1)
        else:
            last_period_quarter = str(int(data['quarter']) - 1)
            last_period_year = data['year']

        last_period_declarations = self.env['vat.7k.config'].search([
            ['period_quarter', '=', last_period_quarter], ['period_year', '=', last_period_year]])

        if last_period_declarations:
            last_declaration = reduce(
                lambda x, y: x.date > y.date and x or y, last_period_declarations)
            return last_declaration.transition_amount
        else:
            return 0

    @api.model
    def _get_report_values(self, docids, data=None):
        doc_model = data['wizard_model']
        doc_ids = data['wizard_id']
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
        doc = Document()
        vat_dict = data['vat_dict']

        # TODO:
        # self._save_vat_config(data)
        # data['P_42'] = self._get_transition_amount(data)

        xml_element = VatUtils.convert_to_xml(JPK_VAT_7K_12, wizard, doc, vat_dict)
        ready_xml = xml_element.toprettyxml(indent="  ", encoding="UTF-8")
        ready_xml = xml_utilities.check_xml_heading(ready_xml)
        vat7k_file = base64.encodestring(ready_xml)
        try:
            xml_utilities.check_xml_file(ready_xml, 'account_pl_cirrus/schemes/VAT-7K(12)_v1-2E.xsd')
        except Exception as e:
            e = str(e)
            raise ValidationError(_('Wrong Data in XML file!\nTry to solve the problem according to message below:\n\n%s')%e)

        return vat7k_file
