# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2009 - now Grzegorz Grzelak grzegorz.grzelak@openglobe.pl

{
    'name' : 'Poland - Account/Tax Chart by OpenGLOBE',
    'version' : '1.01 (14.0)',
    'author' : 'Grzegorz Grzelak (OpenGLOBE)',
    'website': 'http://www.openglobe.pl',
    'category' : 'Accounting/Localizations/Account Charts',
    'description': """
This is the module to manage the accounting chart and taxes for Poland in Odoo.
==================================================================================

To jest moduł do tworzenia wzorcowego planu kont, podatków, obszarów podatkowych i
rejestrów podatkowych. Moduł ustawia też konta do kupna i sprzedaży towarów
zakładając, że wszystkie towary są w obrocie hurtowym.

Moduł moze nie być kompatybilny z funkcjonalnościa Odoo Enterprise
""",
    'depends' : ['account', 'base_iban', 'base_vat'],
    'data' : [
              'account_chart.xml',
              'data/account.account.template.csv',
              'account_chart_2.xml',
              'account_tax.xml',
              'fiscal_position.xml',
              'country_pl.xml',
              #'account_chart_template.yml'
    ],
}
