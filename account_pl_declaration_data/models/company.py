# -*- encoding: utf-8 -*-
from openerp import fields, models, _

class res_company(models.Model):
    _inherit = "res.company"

    regon_code = fields.Char('Regon', size=64, required=True, help="Do wydruku deklaracji podatkowych", default='-')
    county = fields.Char('Powiat', size=64, required=True, help="Do wydruku deklaracji podatkowych", default='-')
    community = fields.Char('Gmina', size=64, required=True, help="Do wydruku deklaracji podatkowych", default='-')
    street_declaration = fields.Char('Ulica', size=64, required=True, help="Do wydruku deklaracji podatkowych", default='-')
    house_number = fields.Char('Nr domu', size=64, required=True, help="Do wydruku deklaracji podatkowych", default='-')
    apartament_number = fields.Char('Nr lokalu', size=64, required=True, help="Do wydruku deklaracji podatkowych", default='-')
    post_office = fields.Char('Poczta', size=64, required=True, help="Do wydruku deklaracji podatkowych", default='-')
    tax_office = fields.Many2one('poland.tax.office', 'Urz. skarbowy', help="Do wydruku deklaracji podatkowych")
    first_name = fields.Char('Pierwsze Imię', size=64)
    surname = fields.Char('Nazwisko', size=64)
    birth_date = fields.Date('Data Urodzenia')
    natural_person =  fields.Boolean("Osoba Fizyczna", default=False)

class poland_tax_office(models.Model):
    _name = 'poland.tax.office'

    name = fields.Char(u'Nazwa urzędu', size=255, required=True)
    street = fields.Char('Ulica', size=128)
    post_code = fields.Char('Kod Pocztowy', size=10)
    city = fields.Char('Miasto', size=64)
    us_code = fields.Char('Kod IS/US', size=4)
