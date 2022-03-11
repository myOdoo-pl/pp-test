from odoo import models, fields, api, _

from odoo.addons.account_pl_declaration_data.utils.xml_utilities import xml_utilities
from odoo.addons.jpk_merger.data.structures import JPK_FA_BILLS

from xml.dom.minidom import Document
# from lxml import etree
import base64


class ReportJpkFaBill(models.TransientModel):
    _name = 'report_jpk_fa_bill'
    _description = 'Report JPK-FA Bill'

    def render_xml(self, wizard):
        vat_utils = self.env['wizard.vat.utils']

        vat_utils.check_company_data(wizard)
        doc = Document()

        vat_dict = vat_utils.get_vat_details(wizard, cash_basis=wizard.cash_basis_pl)
        xml_element = vat_utils.convert_to_xml(JPK_FA_BILLS, wizard, doc, vat_dict)

        ready_xml = xml_element.toprettyxml(indent="  ", encoding="UTF-8")
        ready_xml = xml_utilities.check_xml_heading(ready_xml)
        jpk_file = base64.encodebytes(ready_xml)

        # try:
        #     xml_utilities.check_xml_file(ready_xml, 'jpk_merger/schemes/jpk_fa_bills_schema.xsd')
        # except etree.XMLSchemaParseError as e:
        #     e = str(e)
        #     raise UserError(_('An error occured. Please check your internet connection.\n%s') % e)

        return jpk_file
