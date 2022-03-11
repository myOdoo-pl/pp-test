# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
import base64
from xml.dom.minidom import Document
from openerp.addons.account_pl_declaration_data.utils.xml_utilities import xml_utilities
from odoo.addons.account_pl_cirrus.data.structures import JPK_FA_2
from lxml import etree
from datetime import datetime
from openerp.exceptions import UserError


from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class ReportJpkVat2(models.TransientModel):
    _name='report.jpk.fa.2'

    def render_xml(self, wizard):
        VatUtils = self.env['wizard.vat.utils']

        VatUtils.check_company_data(wizard)
        company_id = wizard.company_id
        doc = Document()

        vat_dict = VatUtils.get_vat_details(wizard, cash_basis=wizard.cash_basis_pl)
        # pprint(vat_dict)
        xml_element = VatUtils.convert_to_xml(JPK_FA_2, wizard, doc, vat_dict)
        ready_xml = xml_element.toprettyxml(indent="  ", encoding="UTF-8")
        ready_xml = xml_utilities.check_xml_heading(ready_xml)
        jpk_file = base64.encodestring(ready_xml)
        # wizard.write({'jpk_fa_file': jpk_file, 'jpk_fa_filename':'JPK-FA-' + datetime.now().strftime('%Y-%m-%d') + ".xml"})
        # e = "File OK"
        try:
            xml_utilities.check_xml_file(ready_xml, 'account_pl_cirrus/schemes/Schemat_JPK_FA(2)_v1-0.xsd')
        except etree.XMLSchemaParseError as e:
            e = str(e)
#            raise UserError(_('An error occured. Please check your internet connection.\n%s')%e)
            e = _('An error occured. Please check your internet connection.\n%s')%e
        return jpk_file
