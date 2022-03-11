# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import datetime
from openerp.exceptions import UserError
from openerp.addons.account_pl_declaration_data.utils.data_to_period_utils import data_to_period, REVERSE_QUARTER_MAP

from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class WizardJpkVat2020(models.TransientModel):
    _name= 'wizard.jpk.vat.2020'
    _inherit= 'account.common.report'

    period = fields.Selection([
        ("1", 'Wybrany Miesiąc'),
        ("3/1", '1 Kwartał - Marzec'),
        ("3/2", '2 Kwartał - Czerwiec'),
        ("3/3", '3 Kwartał - Wrzesień'),
        ("3/4", '4 Kwartał - Grudzień')], 'Period Type', default="1", required=True)
    date_from = fields.Date(string='Start Date', default=lambda x: datetime.now().strftime('%Y-%m')+'-01')
    company_id = fields.Many2one("res.company", "Company", default=lambda self: self.env.user.company_id)
    vat_file = fields.Binary("Plik JPK ewidencji VAT", readonly=True)
    vat_filename = fields.Char("JPK VAT filename", readonly=True)
    cash_basis_pl = fields.Boolean("Cash basis", help="Select this if you are using chash basis method speciffic for polish accounting.", default=lambda self: self.company_id.cash_basis_pl)
    correction_number = fields.Integer("Cel złożenia", default=1, required=True, help="Wartość '1' oznacza generowanie nowego pliku za dany okres. Każda kolejna wartość '2', '3', '4' itd., oznacza numer korekty.")
    correction_record =  fields.Boolean(string="Korekta Ewidencji")
    correction_declaration =  fields.Boolean(string="Korekta Deklaracji")
    pdf_file = fields.Binary("Plik podglądowy PDF", readonly=True)
    pdf_filename = fields.Char("JPK VAT filename", readonly=True)
    natural_person =  fields.Boolean("Osoba Fizyczna", default=False)
    no_declaration_data = fields.Boolean('Rozliczenie Kwartalne ', default=False)
    declaration_data = fields.Boolean(default=False)

    p_39_vdek = fields.Float('P_39',help="Wysokość nadwyżki podatku naliczonego nad należnym z poprzedniej deklaracji.")
    p_49_vdek = fields.Float('P_49',help="Kwota wydana na zakup kas rejestrujących, do odliczenia w danym okresie rozliczeniowym pomniejszająca wysokość podatku należnego. Kwota wykazana w P_49 nie może być wyższa od różnicy kwot z P_38 i P_48. Jeżeli różnica kwot pomiędzy P_38 i P_48 jest mniejsza lub równa 0, wówczas należy wykazać 0.")
    p_50_vdek = fields.Float('P_50',help="Kwota podatku, która w przypadkach uzasadnionych interesem publicznym lub ważnym interesem podatników na podstawie rozporządzenia wydanego przez ministra właściwego do spraw finansów publicznych lub decyzji Organu podatkowego nie podlega wpłacie do urzędu.")
    p_52_vdek = fields.Float('P_52',help='Kwota wydana na zakup kas rejestrujących, do odliczenia w danym okresie rozliczeniowym przysługująca do zwrotu w danym okresie rozliczeniowym lub powiększająca wysokość podatku naliczonego do przeniesienia na następny okres rozliczeniowy. W przypadku gdy kwota wykazana w P_48 jest większa lub równa kwocie z P_38 w danym okresie rozliczeniowym lub kwota ulgi z tytułu zakupu kas rejestrujących jest wyższa od nadwyżki podatku należnego nad naliczonym wówczas w P_52 wykazuje się pozostałą nieodliczoną w P_49 kwotę ulgi z tytułu zakupu kas rejestrujących, przysługującą podatnikowi do zwrotu lub do odliczenia od podatku należnego za następne okresy rozliczeniowe.')
    p_53_vdek = fields.Integer('P_53', help='Wysokość nadwyżki podatku naliczonego nad należnym.', readonly=True)
    p_54_vdek = fields.Integer('P_54',help="Wysokość nadwyżki podatku naliczonego nad należnym do zwrotu na rachunek wskazany przez podatnika.")
    p_55_vdek = fields.Boolean('P_55', help="Zwrot na rachunek VAT, o którym mowa w art. 87 ust. 6a ustawy")
    p_56_vdek = fields.Boolean('P_56', help="Zwrot w terminie, o którym mowa w art. 87 ust. 6 ustawy")
    p_57_vdek = fields.Boolean('P_57', help="Zwrot w terminie, o którym mowa w art. 87 ust. 2 ustawy")
    p_58_vdek = fields.Boolean('P_58', help="Zwrot w terminie, o którym mowa w art. 87 ust. 5a zdanie pierwsze ustawy")
    p_59_vdek = fields.Boolean('P_59', help="Zaliczenie zwrotu podatku na poczet przyszłych zobowiązań podatkowych")
    p_60_vdek = fields.Integer('P_60',help='Wysokość zwrotu do zaliczenia na poczet przyszłych zobowiązań podatkowych.')
    p_61_vdek = fields.Text('P_61',help='Rodzaj przyszłego zobowiązania podatkowego. Podaje  się rodzaj  przyszłego  zobowiązania  podatkowego,  na  poczet którego zalicza się zwrot podatku.')
    p_62_vdek = fields.Integer('P_62',help='Wysokość nadwyżki podatku naliczonego nad należnym do przeniesienia na następny okres rozliczeniowy.')
    p_63_vdek = fields.Boolean('P_63',help="Podatnik wykonywał w okresie rozliczeniowym czynności, o których mowa w art. 119 ustawy")
    p_64_vdek = fields.Boolean('P_64',help="Podatnik wykonywał w okresie rozliczeniowym czynności, o których mowa w art. 120 ust. 4 lub 5 ustawy")
    p_65_vdek = fields.Boolean('P_65',help="Podatnik wykonywał w okresie rozliczeniowym czynności, o których mowa w art. 122 ustawy")
    p_66_vdek = fields.Boolean('P_66',help="Podatnik wykonywał w okresie rozliczeniowym czynności, o których mowa w art. 136 ustawy")
    p_67_vdek = fields.Boolean('P_67',help="Podatnik korzysta z obniżenia zobowiązania podatkowego, o którym mowa w art. 108d ustawy")
    p_67_vdek = fields.Boolean('P_67',help="Podatnik korzysta z obniżenia zobowiązania podatkowego, o którym mowa w art. 108d ustawy")


    @api.onchange('date_from', 'period')
    def _set_date_to(self):
        if self.period:
            months, quarter = self.period.partition("/")[::2]
            data_to_period.set_date_to(self, months, quarter)
        else:
            data_to_period.set_date_to(self)

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.cash_basis_pl = self.company_id.cash_basis_pl


    def _print_report(self, data):
        data['company_id'] = self.company_id
        data_to_period.check_dates(self)
        file_and_dict = self.env['report.jpk.vat.2020'].render_xml(self)
        jpk_file = file_and_dict[0]
        self.write({'vat_file': jpk_file, 'vat_filename': 'VAT-JPK-' + self.date_from.strftime('%Y-%m-') + str(self.correction_number) + '-' + datetime.now().strftime('%Y-%m-%d') + ".xml"})
        return {'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': self.id,
                    'res_model': self._name,
                    'target': 'new',
                    'context': {
                        'default_model': self._name,
                    },
                }



    def print_pdf_report(self):
        file_and_dict = self.env['report.jpk.vat.2020'].render_xml(self)
        vat_dict = file_and_dict[1]
        # pprint(vat_dict)
        data_dict = {}
        data_dict['wizard_id'] = self.id
        data_dict['wizard_model'] = self._name
        data_dict['date_from'] = self.date_from
        data_dict['date_to'] = self.date_to
        data_dict['vat_dict'] = vat_dict
        data_dict['no_declaration_data'] = self.no_declaration_data
        data_dict['correction_number'] = self.correction_number
        data_dict['correction_record'] = self.correction_record
        data_dict['correction_declaration'] = self.correction_declaration
        return self.env.ref('account_pl_cirrus.account_jpk_vat_2020_pdf').report_action(self, data=data_dict)

    def get_data(self):
        data_to_period.check_dates(self)
        self.write({'declaration_data': False})
        file_and_dict = self.env['report.jpk.vat.2020'].render_xml(self)
        if self.declaration_data == True:
            self.vat_file = None
            self.vat_filename = None
        self.write({'declaration_data': True})
        # self.write({'vat_file': jpk_file, 'vat_filename': 'VAT-JPK-' + self.date_from.strftime('%Y-%m-') + str(self.correction_number) + '-' + datetime.now().strftime('%Y-%m-%d') + ".xml"})
        return {'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'res_model': self._name,
                'target': 'new',
                'context': {
                    'default_model': self._name,
                },
                }