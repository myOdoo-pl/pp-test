# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _

import base64
from xml.dom.minidom import Document
from openerp.addons.account_pl_declaration_data.utils.xml_utilities import xml_utilities
from odoo.addons.account_pl_cirrus.data.structures import JPK_FA_1
from lxml import etree

from openerp.exceptions import UserError, ValidationError

from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class ReportJpkVat(models.TransientModel):
    _name='report.jpk.fa.1'

    def render_xml(self, wizard):
        VatUtils = self.env['wizard.vat.utils']

        VatUtils.check_company_data(wizard)
        company_id = wizard.company_id
        doc = Document()

        vat_dict = VatUtils.get_vat_details(wizard, cash_basis=wizard.cash_basis_pl)
        # pprint(vat_dict)
        xml_element = VatUtils.convert_to_xml(JPK_FA_1, wizard, doc, vat_dict)
        ready_xml = xml_element.toprettyxml(indent="  ", encoding="UTF-8")
        ready_xml = xml_utilities.check_xml_heading(ready_xml)
        jpk_file = base64.encodestring(ready_xml)

        try:
            xml_utilities.check_xml_file(ready_xml, 'account_pl_cirrus/schemes/FA_JPK(1)_v1-0.xsd')
        except Exception as e:
            e = str(e)
            if 'P_5B' not in e:
                raise ValidationError(_('Wrong Data in XML file!\nTry to solve the problem according to message below:\n\n%s')%e)
            else:
                _logger.warn('JPK FA PARTNER VAT ERROR:\n{0}'.format(e))
        return jpk_file
