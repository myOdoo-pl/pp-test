from odoo import models, fields, api, _

import base64
from xml.dom.minidom import Document
from openerp.addons.account_pl_declaration_data.utils.xml_utilities import xml_utilities
from odoo.addons.account_pl_cirrus.data.structures import JPK_WB
from lxml import etree
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)
from pprint import pprint

class ReportJpkWb(models.TransientModel):
    _name='report.jpk.wb'

    def render_xml(self, wizard):
        VatUtils = self.env['wizard.vat.utils']
        # _logger.warning('\n\n\n!render_xml!!!!!\n\n')
        # VatUtils.check_company_data(wizard)
        company_id = wizard.company_id
        doc = Document()

        bank_dict = VatUtils.get_bank_details(wizard)
        # pprint(bank_dict)
        xml_element = VatUtils.convert_to_xml(JPK_WB, wizard, doc, bank_dict)
        ready_xml = xml_element.toprettyxml(indent="  ", encoding="UTF-8")
        ready_xml = xml_utilities.check_xml_heading(ready_xml)
        jpk_file = base64.encodebytes(ready_xml)

        try:
            xml_utilities.check_xml_file(ready_xml, 'account_pl_cirrus/schemes/JPK_WB(1)_v1-0.xsd')
        except Exception as e:
            e = str(e)
            raise ValidationError(_('Wrong Data in XML file!\nTry to solve the problem according to message below:\n\n%s')%e)

        return jpk_file
