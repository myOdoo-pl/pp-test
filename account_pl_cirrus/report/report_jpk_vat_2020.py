# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _

import base64
from xml.dom.minidom import Document, parse
from odoo.addons.account_pl_cirrus.data.structures import  JPK_V7M, JPK_V7K
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

class ReportJpkVat2020(models.TransientModel):
    _name='report.jpk.vat.2020'


    def render_xml(self, wizard):
        VatUtils = self.env['wizard.vat.utils']

        VatUtils.check_company_data(wizard)
        company_id = wizard.company_id
        doc = Document()

        if wizard.period != '1':
            xsd_schema = 'account_pl_cirrus/schemes/Schemat_JPK_V7K(1)_v1-1.xsd'
            jpk_structure = JPK_V7K
            wizard.no_declaration_data = False
        elif wizard.no_declaration_data:
            jpk_structure = JPK_V7K
            xsd_schema = 'account_pl_cirrus/schemes/Schemat_JPK_V7K(1)_v1-1.xsd'
        else:
            xsd_schema = 'account_pl_cirrus/schemes/Schemat_JPK_V7M(1)_v1-1.xsd'
            jpk_structure = JPK_V7M

        vat_dict = VatUtils.get_vat_details(wizard, cash_basis=wizard.cash_basis_pl, natural_person=wizard.company_id.natural_person)
        # pprint(vat_dict)

        xml_element = VatUtils.convert_to_xml(jpk_structure, wizard, doc, vat_dict)

        ready_xml = xml_element.toprettyxml(indent="  ", encoding="UTF-8")

        # pprint(ready_xml)

        ready_xml = xml_utilities.check_xml_heading(ready_xml)
        jpk_file = base64.encodestring(ready_xml)
        if wizard.no_declaration_data==True:
            try:
                xml_utilities.check_xml_file(ready_xml, xsd_schema)
            except etree.XMLSchemaParseError as e:
                e = str(e)
                raise UserError(_('An error occured. Please check your internet connection.\n%s')%e)
        return [jpk_file, vat_dict]


class ReportJpkVat2020(models.AbstractModel):
    _name = 'report.account_pl_cirrus.report_jpk_vat_2020_pdf'

    @api.model
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
