# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _

import base64
from xml.dom.minidom import Document, parse
from odoo.addons.account_pl_cirrus.data.structures import JPK_VAT_3
from openerp.addons.account_pl_declaration_data.utils.xml_utilities import xml_utilities
from datetime import datetime
from lxml import etree
from math import fabs
import collections
from collections import OrderedDict


from openerp.exceptions import UserError

from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class ReportJpkVat(models.TransientModel):
    _name='report.jpk.vat.3'

    def render_xml(self, wizard):
        VatUtils = self.env['wizard.vat.utils']

        VatUtils.check_company_data(wizard)
        company_id = wizard.company_id
        doc = Document()

        vat_dict = VatUtils.get_vat_details(wizard, cash_basis=wizard.cash_basis_pl)
        # pprint(vat_dict)

        xml_element = VatUtils.convert_to_xml(JPK_VAT_3, wizard, doc, vat_dict)

        ready_xml = xml_element.toprettyxml(indent="  ", encoding="UTF-8")

        ready_xml = xml_utilities.check_xml_heading(ready_xml)
        jpk_file = base64.encodestring(ready_xml)

        try:
            xml_utilities.check_xml_file(ready_xml, 'account_pl_cirrus/schemes/VAT_JPK(3)_v1-1.xsd')
        except etree.XMLSchemaParseError as e:
            e = str(e)
            raise UserError(_('An error occured. Please check your internet connection.\n%s')%e)

        return [jpk_file, vat_dict]


class ReportJpkVat3(models.AbstractModel):
    _name = 'report.account_pl_cirrus.report_jpk_vat3_pdf'

    def _get_report_values(self, docids, data=None):
        doc_model = data['wizard_model']
        doc_ids = data['wizard_id']
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
            'strptime': datetime.strptime,
        }
