{
	'name': 'Downpayment Extended Functionality',
	'summary': 'Extends invoice downpayment system.',
	'author': 'myOdoo.pl',
	'website': 'https://myodoo.pl',
	'category': 'Accounting',
	'version': '[V14] 0.3',
	'depends': [
		'account',
		'account_accountant',
		'sale',
		'sale_management'
	],
	'data': [
		'data/journal_data.xml',
		'views/account_move_view.xml'
	],
	'installable': True,
	'auto_install': False
}
