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
    "name" : "Poland - Localization of Invoices",
    "version" : "1.21 (14.0)",
    "author" : "OpenGLOBE",
    "website": "http://www.openglobe.pl",
    "category" : "Localisation/Country specific stuff",
    "description": """
This is the module to manage Polish specific accounting functionality in Open ERP.
==================================================================================

To jest moduł do obsługi specyficznych księgowych wymagań funkcjonalnych
w Polsce.

Dodano:
-------
* Pola Podatek i Brutto do pozycji faktur
* Do faktury pole id faktury pierwotnej - stosowane do powiązania faktury korygującej z pierwotną
* Widok partnerów po numerach NIP
* Daty wystawienia i otrzymania faktury
* Kod identyfikacyjny banku na wydruku faktur
* Due date obliczane na podstawie issue date
* Wyszukiwanie faktur po numerze NIP
* Dodanie pola numeru bankowego w widoku partnera. To konto zostanie wykorzystane do wpłat dokonywanych przez danego klienta
* Dodanie zakładek, jednej pokazującej docelowe pozycje faktury korygującej, drugiej pokazującą wartości korygujące.
* Dodanie duplikatu faktury
    """,
    "depends" : ["account",
                 "base_iban",
                 "base_vat",
                 "base_setup",
                 "sale",
                 "web",
                ],
    "demo_xml" : [],
    "data" : [
            "views/partner_view.xml",
            "views/product_view.xml",
            "data/account_data.xml",
            'views/report_invoice.xml',
            'views/invoice_report.xml',
            'views/template_invoice_pl_og.xml',
            'views/account_fiscal_position_view.xml',
            'security/ir.model.access.csv',
            'views/account_move_view.xml',
                    ],
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
