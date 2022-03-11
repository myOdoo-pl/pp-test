{
    'name': 'HR Extended Reports',
    'author': 'myOdoo.pl',
    'version': '[V14]_0.6',
    'category': 'HR',
    'website': 'https://myodoo.pl',
    'depends': [
        'hr',
        'hr_contract',
        'hr_timesheet',
        'sale',
        'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
        'views/hr_extended_report_view.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}
