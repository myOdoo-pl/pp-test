# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    e-deklaracje_pl_2012
#    Copyrigt (C) 2012 Andrzej Grymkowski & OpenGLOBE Grzegorz Grzelak (www.openglobe.pl)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# from openerp.osv import osv
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)

import collections
from odoo.tools import mimetypes

# To allow create XML file by normal users, Odoo treated files beginned with < (like '<?xml') as image/svg and didn't allowed to create
_Entry = collections.namedtuple('_Entry', ['mimetype', 'signatures', 'discriminants'])
mime_list = list(mimetypes._mime_mappings)
mime_list.insert(0,
            # xml
        _Entry('text/xml', [b'<?xml'], []),
)
mimetypes._mime_mappings = tuple(mime_list)
#_logger.warn("CHECK: "+str(mimetypes._mime_mappings))

class xml_utilities:

    @staticmethod
    def sendUnsign(self, cr, uid, xml_file):
        from suds import WebFault
        from suds.client import Client

        url='https://test-bramka.edeklaracje.gov.pl/uslugi/dokumenty?wsdl'
        client = Client(url)
        save = client.service.sendUnsignDocument(document=xml_file)

    @staticmethod
    def send(self, cr, uid, xml_file):
        from suds import WebFault
        from suds.client import Client

        url='https://test-bramka.edeklaracje.gov.pl/uslugi/dokumenty?wsdl'
        client = Client(url)
        save = client.service.sendDocument(document=xml_file)
        self.refId =save.refId

    @staticmethod
    def request(self, cr, uid):
        from suds.client import Client

        url='https://test-bramka.edeklaracje.gov.pl/uslugi/dokumenty?wsdl'
        client = Client(url)
        receive = client.service.requestUPO(refId =self.refId)
        if receive.status != 200:
            # raise osv.except_osv(_("ERROR"), _(receive.statusOpis))
            raise ValidationError(receive.statusOpis)

    @staticmethod
    def check_xml_file(xml_file, scheme_file, doc = False):
        from lxml import etree
        from openerp import tools
        f_schema = tools.file_open(scheme_file)
        schema_doc = etree.parse(f_schema)
        schema = etree.XMLSchema(schema_doc)

        parser = etree.XMLParser(schema = schema)
        return etree.fromstring(xml_file, parser)

    @staticmethod
    def check_xml_heading(xml_file):
        """Because sometimes xml files doesn't have XML heading
           we need to make sure it is present
           for compatibility in some apps (e.g. Adobe Reader DC)

        """

        try:
            if not str(xml_file).startswith('<?xml version="1.0"'):
                _logger.warning('NO XML HEADING')
                xml_file = b'<?xml version="1.0" encoding="utf-8"?>\n' + xml_file
        except TypeError:
            return xml_file
        return xml_file
