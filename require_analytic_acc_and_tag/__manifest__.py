{
    'name': "Require Analytic Account & Tag",
    'summary': 'Makes Analytic Tag and Account required on invoice line, sale order and purchase order',
    'author': 'MyOdoo.pl',
    'website': 'https://myodoo.pl',
    'category': 'Tools',
    'version': 'V14.0.1.4.1',
    'depends': [
        'account',
        'sale',
        'purchase'
    ],
    'data': [
        'views/purchase_views.xml',
        'views/sale_views.xml'
    ],
    'installable': True
}
