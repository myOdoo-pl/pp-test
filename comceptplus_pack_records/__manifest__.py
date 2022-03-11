# -*- coding: utf-8 -*-
{
    'name': "Pack records (attachments)",
    'version': '1.0',
    'license': 'AGPL-3',
    'author' : 'comceptPLUS',
    'website' : 'https://comceptplus.com',
    'support': 'odoo@comceptplus.com',
    'category': 'Tools',
    'summary': 'Export record attachments into a compressed file',
    'description': 'This module allows the user to select records and pack their attachments in a zip file.',
    'depends': [],
    'data': [
            'security/ir.model.access.csv',
            'wizard/ir_model_download_pack_view.xml'
            ],
    'images': ['static/images/main_screenshot.png'],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
