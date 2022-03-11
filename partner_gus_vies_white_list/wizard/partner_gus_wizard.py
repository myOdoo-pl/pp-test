# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from ..models.regon import REGONAPI
from lxml import etree
from odoo.exceptions import UserError, ValidationError
import xmltodict as xd

_logger = logging.getLogger(__name__)


class partner_gus_wizard(models.TransientModel):
    _name = "partner.gus.wizard"
    _description = "Wizard GUS"

    nip = fields.Char(string='NIP')
    krs = fields.Char(string='KRS')
    regon = fields.Char(string='REGON')

    def gus_search(self):
        
        gus_code = self.env['ir.config_parameter'].sudo().get_param('res_partner.use_gus_code') and self.env.user.company_id.gus_code
        regon_api = REGONAPI("https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc")
        try:
            regon_api.login(gus_code)
        except:
            raise ValidationError(_("Brak kodu do bazy GUS. Więcej szczegółów pod adresem https://api.stat.gov.pl/Home/RegonApi ."))

        entites = False

        if self.nip:
            entities = regon_api.search(nip=self.nip)
        elif self.krs:
            entities = regon_api.search(krs=self.krs)
        elif self.regon:
            entities = regon_api.search(regon=self.regon)
        else:
            raise ValidationError(_("Proszę wpisać NIP/KRS/REGON"))
        
        if entities:
            website = False
            email = False
            fax = False
            phone = False
            country_code = False
            country_id = False
            zip = False
            city = False
#            zip = False
            street = False
            state = False
            name = False
            nip_found = False

            if entities[0].find('DataZakonczeniaDzialalnosci'):
                date_finish =entities[0].find('DataZakonczeniaDzialalnosci').text
                if date_finish:
                    raise UserError(_('Podmiot o tym numerze NIP zakończył działalność %s')%(date_finish) )

            try:
                regon = entities[0].find('Regon').text
            except AttributeError:
                raise UserError(_("Couldn't find info in GUS."))
            nip_found = 'PL' + entities[0].find('Nip').text
            if entities[0].find('Miejscowosc'):
                city = entities[0].find('Miejscowosc').text
            if entities[0].find('KodPocztowy'):
                zip = entities[0].find('KodPocztowy').text
            if entities[0].find('Ulica'):
                street = entities[0].find('Ulica').text
            if entities[0].find('Wojewodztwo'):
                state = entities[0].find('Wojewodztwo').text
            if entities[0].find('Nazwa'):
                name = entities[0].find('Nazwa').text


            if entities[0].find('Typ').text == "F":
                detailed_report = regon_api.full_report(regon, 'PublDaneRaportDzialalnoscFizycznejCeidg')
#                _logger.warning("IN DETAILED\n"+detailed_report[0])
                if len(detailed_report):
#                    nip_found = 'PL' + str(detailed_report[0].find('fiz_nip'))
#                    _logger.warning("NIP FOUND: "+nip_found)
                    street_number = str(detailed_report[0].find('fiz_adSiedzNumerNieruchomosci'))
                    home_number = str(detailed_report[0].find('fiz_adSiedzNumerLokalu'))
                    country_code = str(detailed_report[0].find('fiz_adSiedzKraj_Symbol'))
                    if detailed_report[0].find('fiz_adresStronyinternetowej'):
                        website = detailed_report[0].find('fiz_adresStronyinternetowej').text
                    if detailed_report[0].find('fizC_adresEmail'):
                        email = detailed_report[0].find('fizC_adresEmail').text
                    if detailed_report[0].find('fizC_numerTelefonu'):
                        phone = detailed_report[0].find('fizC_numerTelefonu').text
                    if detailed_report[0].find('fizC_numerFaksu'):
                        fax = detailed_report[0].find('fizC_numerFaksu').text
                    if home_number:
                        street_number = street_number+"/"+home_number
                    if street:
                        street = street+" "+street_number
                    if not street:
                        street = "Brak dokładnego adresu w bazie GUS"

                    if not website:
                        website = False
                    if not email:
                        email = False
                    if not phone:
                        phone = False
                    if not fax:
                        fax = False

            elif entities[0].find('Typ').text == "P":
                detailed_report = regon_api.full_report(regon, 'PublDaneRaportPrawna')
                if len(detailed_report):
#                    detailed_report_dict = xd.parse(etree.tostring(detailed_report[0], pretty_print=True))
                    nip_found = 'PL' + str(detailed_report[0].find('praw_nip'))
                    street_number = str(detailed_report[0].find('praw_adSiedzNumerNieruchomosci'))
                    home_number = str(detailed_report[0].find('praw_adSiedzNumerLokalu'))
                    country_code = str(detailed_report[0].find('praw_adSiedzKraj_Symbol'))
                    if detailed_report[0].find('praw_adresStronyinternetowej'):
                        website = detailed_report[0].find('praw_adresStronyinternetowej').text
                    if detailed_report[0].find('prawC_adresEmail'):
                        email = detailed_report[0].find('prawC_adresEmail').text
                    if detailed_report[0].find('prawC_numerTelefonu'):
                        phone = detailed_report[0].find('prawC_numerTelefonu').text
                    if detailed_report[0].find('prawC_numerFaksu'):
                        fax = detailed_report[0].find('prawC_numerFaksu').text
                    if home_number:
                        if type(home_number) == str:
                            street_number = street_number+"/"+home_number
                    if street:
                        street = street+" "+street_number
                    if not street:
                        street = "Brak dokładnego adresu w bazie GUS"

                    if not website:
                        website = False
                    if not email:
                        email = False
                    if not phone:
                        phone = False
                    if not fax:
                        fax = False
        else:
            raise ValidationError(_("Nie znaleziono wyniku"))
        
        if state:
            state_id = self.env['res.country.state'].search([('name','=ilike',state)])
        else:
            state_id = False
        if state_id:
            state = state_id.id
        else:
            state = False

        if country_code:
            country = self.env['res.country'].search([('code','ilike',country_code)])
        else:
            country = False
        if country:
            country_id = country.id
        else:
            country_id = False
        partner_id = self.env['res.partner'].browse(self.env.context['active_id'])

        values = {'company_type':'company','name':name}
        
        if city and city != '':
            values['city'] = city
        if zip and zip != '':
            values['zip'] = zip
        if street and street != '':
            values['street'] = street
        if website and website != '':
            values['website'] = website
        if email and email != '':
            values['email'] = email
        if phone and phone != '':
            values['phone'] = phone
        if state and state != '':
            values['state_id'] = state
        if country_id and country_id != '':
            values['country_id'] = country_id
        if nip_found and nip_found != '':
            values['vat'] = nip_found
        
        partner_id.write(values)
        