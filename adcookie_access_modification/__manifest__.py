{
    'name': 'AdCookie Access Rights Modification',
    'summary': 'AdCookie Access Rights Modification',
    'description': '''
    Access rights modification module for AdCookie. Adds security group
    with limited Accounting documents access.
    ''',
    'author': 'myOdoo.pl',
    'website': 'https://myodoo.pl',
    'category': 'Accounting/Accounting',
    'version': '[V14]_1.8.6',
    'depends': [
        'account',
        'account_accountant',
        'account_budget',
        'account_invoice_pl_og',
        'analytic',
        'project',
        'purchase',
        'sale'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_budget_views.xml',
        'views/account_move_views.xml',
        'views/analytic_account_views.xml',
        'views/menuitem.xml',
        'wizard/sensitive_data_modifier_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
