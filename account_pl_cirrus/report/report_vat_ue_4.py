# -*- coding: utf-8 -*-

import base64
from xml.dom.minidom import Document

from openerp import models, api, _
from openerp.exceptions import UserError, ValidationError
from openerp.addons.account_pl_declaration_data.utils.xml_utilities import xml_utilities
from odoo.addons.account_pl_cirrus.data.structures import JPK_UE_4

import logging
from pprint import pprint

_logger = logging.getLogger(__name__)


class ReportVatUE_4(models.AbstractModel):
    _name = 'report.account_pl_cirrus.report_vat_ue_4'

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
            'vat_data': data['vat_dict']['ue_dict'],
            'VatUtils': self.env['wizard.vat.utils'],
            'wizard': self.env[doc_model].browse(doc_ids),
            'sorted': sorted,
        }


    def render_xml(self, data):
        _logger.warn("Generating XML!")
        VatUtils = self.env['wizard.vat.utils']
        wizard = self.env['account.report.vat.ue4'].browse(data['wizard_id'])

        vat_dict = data['vat_dict']
        # pprint(vat_dict)
        doc = Document()
        xml_element = VatUtils.convert_to_xml(JPK_UE_4, wizard, doc, vat_dict)
        ready_xml = xml_element.toprettyxml(indent="  ", encoding="UTF-8")
        ready_xml = xml_utilities.check_xml_heading(ready_xml)
        vat_ue_file = base64.encodestring(ready_xml)
        try:
            xml_utilities.check_xml_file(ready_xml, 'account_pl_cirrus/schemes/VAT-UE(4)_v1-0E.xsd')
        except Exception as e:
            e = str(e)
            raise ValidationError(_('Wrong Data in XML file!\nTry to solve the problem according to message below:\n\n%s')%e)
        return vat_ue_file
