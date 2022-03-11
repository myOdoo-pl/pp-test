# -*- encoding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name" : "Poland - accounting information and data",
    "version" : "0.01 (14.0)",
    "author" : "Maciej Wichowski",
    'license': 'AGPL-3',
    "website": "http://www.openglobe.pl",
    "category" : "Localisation/Country specific stuff",
    "description":
    """
    This module adds fields to fill with necessary data for polish tax declarations and other declarations.
    \nIt is necessary to handle OpenGLOBE modules integrating with polish tax office.
    \nFor further Odoo versions, every accounting module will be dependent on this one.
    \nTODO: add accounting parameters.

    IS/US codes come from http://www.mf.gov.pl as at 18.07.2016r.

    """,
    "depends" : ['account'],
    "demo_xml" : [],
    "data" : [
            'views/company_view.xml',
            'security/ir.model.access.csv',
            'data/poland.tax.office.csv',
    ],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
