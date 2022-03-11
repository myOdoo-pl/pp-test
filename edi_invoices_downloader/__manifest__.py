{
    'name': 'EDI Invoices Downloader',
    'author': 'myOdoo.pl',
    'version': '[V14] 0.3',
    'category': 'Accounting',
    'website': 'https://myodoo.pl',
    'depends': [
        'account',
        'account_edi',
        'account_reports'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/pack_edi_wizard_view.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}
