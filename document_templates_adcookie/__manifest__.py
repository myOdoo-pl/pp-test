{
    'name': 'Document Templates Adcookie',
    'summary': 'Document Templates modified for AdCookie',
    'description': '''
    Document Templates Adcookie based on standard set 2
    ''',
    'author': 'myOdoo.pl',
    'website': 'https://myodoo.pl',
    'category': 'Templates',
    'version': '[V14] 3.8.1',
    'depends': [
        'account',
        'sale',
        'sale_management',
        'account_invoice_pl_og',
        'account_invoice_templates',
        'downpayment_modification',
        'web'
    ],
    'data': [
        'report/report.xml',
        'report/external_layout_template.xml',
        'report/invoice_report_template.xml',
        'report/invoice_duplicate_report_template.xml',
        'report/sale_report_template.xml',
        'views/account_move_view.xml',
        'views/sale_view.xml',
        'views/css_loader.xml'
    ],
    'installable': True,
    'auto_install': False
}
