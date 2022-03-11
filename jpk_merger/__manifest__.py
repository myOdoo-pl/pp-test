{
    'name': 'JPK Merger',
    'author': 'myOdoo.pl',
    'version': '[V14]_0.5.1',
    'category': 'Accounting',
    'website': 'https://myodoo.pl',
    'depends': [
        'account',
        'account_pl_declaration_data',
        'account_pl_cirrus'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/jpk_fa_bill_wizard_view.xml',
        'views/merged_jpk_wizard_view.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}
