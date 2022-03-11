# -*- coding: utf-8 -*-

import requests
import datetime
import re
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, Warning

from .regon import REGONAPI
_logger = logging.getLogger(__name__)

try:
    from stdnum.eu.vat import check_vies
    from stdnum.exceptions import InvalidComponent
except ImportError:
    _logger.debug("Cannot import check_vies method from python stdnum.")


class ResPartner(models.Model):
    _inherit = "res.partner"

    vat_subjected = fields.Boolean('VAT Validated')
    message_post_on_create = fields.Char()

    def gus_api_search(self):
        gus_code = self.env['ir.config_parameter'].sudo().get_param('res_partner.use_gus_code') and self.env.user.company_id.gus_code
        # _logger.warning(gus_code)
        if gus_code:
            regon_api = REGONAPI("https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc")
            sid = regon_api.login(gus_code)
            vat = self.vat.strip().upper()
            vat_country, vat_number = self._split_vat(vat)
            if vat_country.upper() != 'PL':
                return {}
            try:
                entities = regon_api.search(nip=vat_number)
            except:
                raise ValidationError(_("Cannot validate VAT in GUS. Incorrect VAT entered!"))

            res = {}

            if entities:
                if entities[0].find('DataZakonczeniaDzialalnosci'):
                    date_finish =entities[0].find('DataZakonczeniaDzialalnosci').text
                    if date_finish:
                        raise ValidationError(_('Podmiot o tym numerze NIP zakończył działalność %s')%(date_finish) )

                regon = entities[0].find('Regon').text if entities[0].find('Regon') else False
                res['city'] = entities[0].find('Miejscowosc').text if entities[0].find('Miejscowosc') else ''
                res['zip'] = entities[0].find('KodPocztowy').text if entities[0].find('KodPocztowy') else ''
                res['street'] = entities[0].find('Ulica').text if entities[0].find('Ulica') else ''
                res['state'] = entities[0].find('Wojewodztwo').text if entities[0].find('Wojewodztwo') else ''
                res['name'] = entities[0].find('Nazwa').text if entities[0].find('Nazwa') else ''

                country_code = False

                if entities[0].find('Typ') and entities[0].find('Typ').text == "F":
                    detailed_report = regon_api.full_report(regon, 'PublDaneRaportDzialalnoscFizycznejCeidg')
                    if len(detailed_report):
                        street_number = str(detailed_report[0].find('fiz_adSiedzNumerNieruchomosci'))
                        home_number = str(detailed_report[0].find('fiz_adSiedzNumerLokalu'))
                        country_code = str(detailed_report[0].find('fiz_adSiedzKraj_Symbol'))
                        res['website'] = str(detailed_report[0].find('fiz_adresStronyinternetowej')) if detailed_report[0].find('fiz_adresStronyinternetowej') else ''
                        res['email'] = str(detailed_report[0].find('fizC_adresEmail')) if detailed_report[0].find('fizC_adresEmail') else ''
                        res['phone'] = str(detailed_report[0].find('fizC_numerTelefonu')) if detailed_report[0].find('fizC_numerTelefonu') else ''
                        if home_number:
                            street_number = street_number+"/"+home_number
                        if res['street']:
                            res['street'] =  res['street']+" "+street_number
                        if not res['street']:
                            res['street'] = "Brak dokładnego adresu w bazie GUS/Vies"


                elif entities[0].find('Typ') and entities[0].find('Typ').text == "P":
                    detailed_report = regon_api.full_report(regon, 'PublDaneRaportPrawna')
                    if len(detailed_report):
                        street_number = str(detailed_report[0].find('praw_adSiedzNumerNieruchomosci'))
                        home_number = str(detailed_report[0].find('praw_adSiedzNumerLokalu'))
                        nip = str(detailed_report[0].find('praw_nip'))
                        country_code = str(detailed_report[0].find('praw_adSiedzKraj_Symbol'))
                        res['website'] = str(detailed_report[0].find('praw_adresStronyinternetowej')) if detailed_report[0].find('praw_adresStronyinternetowej') else ''
                        res['email'] = str(detailed_report[0].find('prawC_adresEmail')) if detailed_report[0].find('prawC_adresEmail') else ''
                        res['phone'] = str(detailed_report[0].find('prawC_numerTelefonu')) if detailed_report[0].find('prawC_numerTelefonu') else ''
                        if home_number:
                            if type(home_number) == str:
                                street_number = street_number+"/"+home_number
                        if res['street']:
                            res['street'] =  res['street']+" "+street_number
                        if not res['street']:
                            res['street'] = "Brak dokładnego adresu w bazie GUS/Vies"


                if country_code:
                    country = self.env['res.country'].search([('code','ilike',country_code)])
                    if country:
                        res['country_id'] = country.id

                        if 'state' in res:
                            state_rec = self.env['res.country.state'].search([('country_id','=',country.id),('name','=ilike',res.pop('state'))])
                            if state_rec:
                                res['state_id'] = state_rec[0].id
                res['vat_subjected'] = True
            else:
                raise UserError(_('Nie znaleziono wyniku !'))
                res['vat_subjected'] = False

            return res
        else:
            return {}

    @api.model
    def _get_vies_data(self):
        res = {}
        vat = self.vat.strip().upper()
        vat_country, vat_number = self._split_vat(vat)
        try:
            result = check_vies(vat)
            _logger.warning(str(result))
        except InvalidComponent:
            raise ValidationError(_("Cannot validate VAT in VIES. Incorrect VAT entered!"))
        if result.name is None:
            raise ValidationError(_("The partner is not listed on Vies "
                                    "Webservice."))
        res['vat'] = vat
        res['vat_subjected'] = result.valid
        if result.name != '---':
            res['name'] = result.name.upper()
        country = self.env['res.country'].search([('code', 'ilike', vat_country)])
        if country:
            res['country_id'] = country[0].id

        return res

    @api.onchange('vat')
    def vat_change(self):
        res = {'value': {}}
        # with self.env.do_in_onchange():

        if self.vat:
            white_list_check = self.get_data_from_white_list()
            try:
                if white_list_check:
                    result = self.gus_api_search()

                    if result.get('website') and result.get('website') != '':
                        res['value'].update({'website': result['website']})

                    if result.get('email') and result.get('email') != '':
                        res['value'].update({'email': result['email']})

                    if result.get('phone') and result.get('phone') != '':
                        res['value'].update({'phone': result['phone']})

                    if result.get('country_id'):
                        res['value'].update({'country_id': result['country_id']})

                    if result.get('state_id'):
                        res['value'].update({'state_id': result['state_id']})

                    if result.get('vat_subjected'):
                        res['value'].update({'vat_subjected': result['vat_subjected']})

                    return res
            except:
                connection_error = True
            #check GUS first then VIES on GUS error
            try:
                result = self.gus_api_search()
                connection_error = False
            except:
                result = False
                connection_error = True
            if (not result or not result.get('vat_subjected')) and not connection_error:
                result = self._get_vies_data()
                res['value'].update(result)
        return res

    def get_vies_data_from_vat(self):
        if self.vat:
            #check GUS first then VIES on GUS error
            result = self.gus_api_search()

            if not result or not result.get('vat_subjected'):
                result = self._get_vies_data()
                
            if result.get('street') == '':
                del result['street']
            if result.get('city') == '':
                del result['city']
            if result.get('zip') == '':
                del result['zip']
            if result.get('country') == '':
                del result['country']
            if result.get('website') == '':
                del result['website']
            if result.get('email') == '':
                del result['email']
            if result.get('phone') == '':
                del result['phone']

            self.sudo().update(result)

    # splits address string from json into 3 strings: street, zip_code, city
    def split_address(self, str_address):
        zip_formats = [
            "\d\d-\d\d\d",
            "\d\d\d\d\d\d",
            "\d\d\d\d\d",
            "\d\d\d\d" 
        ]
        # serach zip in most common zip code formats
        for zip_format in zip_formats:
            zip_re = re.search(zip_format, str_address)
            if zip_re:
                break
        zip_position = zip_re.span()
        zip_code = zip_re.group()
        street = str_address[:zip_position[0] - 1]
        city = str_address[zip_position[1] + 1:]
        result = [street, zip_code, city]
        return result

    def check_pl(self):
        if self.vat:
            if self.vat[0:2] != 'PL':
                raise Warning(_('This button is only for polish VAT numbers'))
            self.get_data_from_white_list()

    def get_data_from_white_list(self):
        if self.vat[0:2] == 'PL':
            vat = self.vat[-10:]
            date = str(datetime.date.today())
            url = "https://wl-api.mf.gov.pl/api/search/nip/{}?date={}".format(vat, date)
            # url = "https://wl-test.mf.gov.pl:9091/wykaz-podatnikow/api/search/nip/{}?date={}".format(self.vat, date)
            data = requests.get(url)

            # data = requests.get(url, headers={'User-Agent': ''})
            _logger.warning('DATA: %s', data.json())
            if 'result' not in data.json():
                raise Warning(_('{}'.format(data.json()['message'])))
            result = data.json()['result']
            bank_accounts = [record.acc_number for record in self.bank_ids]
            index = 0
            for acc in bank_accounts:
                if ' ' in acc:
                    bank_accounts[index] = acc.replace(' ', '')
                index += 1
            suspicious_accounts_list = []
            checked_accounts_list = []
            for account in bank_accounts:
                if account in result['subject']['accountNumbers']:
                    checked_accounts_list.append('<br>- ' + account)
                if account not in result['subject']['accountNumbers']:
                    suspicious_accounts_list.append('<br>- ' + account)
            checked_accounts = ''.join(checked_accounts_list)
            suspicious_accounts = ''.join(suspicious_accounts_list)
            #         raise Warning(_('Bank account number: {} does not exist on the White list'.format(account)))
            self.name = result['subject']['name']
            residence_address = result['subject']['residenceAddress']
            working_address = result['subject']['workingAddress']
            str_address = residence_address if residence_address else working_address
            if ',' in str_address:
                str_address = str_address.replace(',', '')
            if str_address:
                self.street = self.split_address(str_address)[0]
                self.zip = self.split_address(str_address)[1]
                self.city = self.split_address(str_address)[2]
            bank_ids_records = []
            accounts_added_list = []
            if result['subject']:
                for acc in result['subject']['accountNumbers']:
                    if acc not in bank_accounts:
                        bank_ids_records.append((0, 0, {'acc_number': acc}))
                        accounts_added_list.append('<br>- ' + acc)
            accounts_added = ''.join(accounts_added_list)
            lists = (suspicious_accounts_list, checked_accounts_list, accounts_added_list)
            comments = (_('<br>WARNING! Bank accounts which are not on the White list: %s') % suspicious_accounts,
                        _('<br>Bank accounts checked on the White list: %s') % checked_accounts,
                        _('<br>Bank accounts added from the White List: %s') % accounts_added)
            comment = ''
            for list in lists:
                if len(list) > 0:
                    comment += comments[lists.index(list)]
            self.bank_ids = bank_ids_records
            message = _("White list request id: {} {}").format(result['requestId'], comment)
            if self.id and str(self.id).isdigit():
                self.message_post(body=message)
            else:
                self.message_post_on_create = message
            return True

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for rec in self:
            if rec.message_post_on_create:
                rec.message_post(body=rec.message_post_on_create)
                rec.message_post_on_create = False
        return res
