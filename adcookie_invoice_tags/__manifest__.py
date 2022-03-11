{
    'name': 'AdCookie Invoice Tags',
    'summary': 'AdCookie invoice tags',
    'description': '''
    Module adds tagging funcionality to invoice documents.
    ''',
    'author': 'myOdoo.pl',
    'website': 'https://myodoo.pl',
    'category': 'Accounting/Accounting',
    'version': '[V14]_1.0',
    'depends': [
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/menuitem.xml'
    ],
    'installable': True,
    'auto_install': False,
}
