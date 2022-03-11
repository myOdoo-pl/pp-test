# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>)
#    All Rights Reserved
#    $Id$
#
#    Module account_invoice_pl_og is copyrighted by
#    Grzegorz Grzelak of OpenGLOBE (www.openglobe.pl) and Cirrus (www.cirrus.pl)
#    with the same rules as OpenObject and OpenERP platform
#    All Rights reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Poland - Localization of Invoices - Templates",
    "version" : "1.03 (14.0)",
    "author" : "OpenGLOBE",
    "website": "http://www.openglobe.pl",
    "category" : "Localisation/Country specific stuff",
    "description": """

Moduł zmieniający wydruki księgowe.
W celu zmiany bądź dostosowania do wymagań klienta, zmianie podlega ten moduł, a nie moduł bazowy account_invoice_pl_og.
    """,
    "depends" : ["account_invoice_pl_og"],
    "data" : [
            'views/report_invoice.xml',
                    ],
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
