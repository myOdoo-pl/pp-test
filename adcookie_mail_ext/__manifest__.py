{
    'name': 'AdCookie mail ext',
    'summary': 'AdCookie mail ext',
    'description': '''
    Mail extension module for AdCookie changing default from mail address.
    ''',
    'author': 'myOdoo.pl',
    'website': 'https://myodoo.pl',
    'category': 'Tools',
    'version': '[V14]_0.4.1',
    'depends': [
        'mail',
        'mail_debrand'
    ],
    'data': [
        'data/config_parameters.xml'
    ],
    'installable': True,
    'auto_install': False,
}
