from collections import OrderedDict

JPK_FA_1 = OrderedDict([
('JPK', OrderedDict([
    ('attrs', {
        'xmlns': 'http://jpk.mf.gov.pl/wzor/2016/03/09/03095/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'JPK_FA',
            'attrs': {
                'kodSystemowy': 'JPK_FA (1)',
                'wersjaSchemy': '1-0',
            }
        }),
        ('WariantFormularza', {'static_value': '1'}),
        ('CelZlozenia', {'static_value': '1'}),
        ('DataWytworzeniaJPK', {'function': 'get_creation_date'}),
        ('DataOd', {'wizard': 'date_from'}),
        ('DataDo', {'wizard': 'date_to'}),
        ('DomyslnyKodWaluty', {'wizard': ['company_id', 'currency_id', 'name']}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('IdentyfikatorPodmiotu', OrderedDict([
            ('dt:NIP', {'value': ['company_data', 'numeric_vat']}),
            ('dt:PelnaNazwa', {'wizard': ['company_id', 'name']}),
            ('dt:REGON', {'wizard': ['company_id', 'regon_code']}),
        ])),
        ('AdresPodmiotu', OrderedDict([
            ('dt:KodKraju', {'wizard': ['company_id', 'country_id', 'code']}),
            ('dt:Wojewodztwo', {'wizard': ['company_id', 'state_id', 'name']}),
            ('dt:Powiat', {'wizard': ['company_id', 'county']}),
            ('dt:Gmina', {'wizard': ['company_id', 'community']}),
            ('dt:Ulica', {'wizard': ['company_id', 'street_declaration']}),
            ('dt:NrDomu', {'wizard': ['company_id', 'house_number']}),
            ('dt:NrLokalu', {'wizard': ['company_id', 'apartament_number']}),
            ('dt:Miejscowosc', {'wizard': ['company_id', 'city']}),
            ('dt:KodPocztowy', {'wizard_function': 'get_company_zip'}),
            ('dt:Poczta', {'wizard': ['company_id', 'post_office']}),
        ])),
    ])),
    ('Falktura', {
        'iterator': 'sale_dict',
        'loop': {
            'Faktura': OrderedDict([
                ('attrs', {'typ': 'G'}),
                ('P_1', {'value': ['sale_dict', 'loop_key', 'date_issue']}),
                ('P_2A', {'value': ['sale_dict', 'loop_key', 'main_reference']}),
                ('P_3A', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'name']}),
                ('P_3B', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'address']}),
                ('P_3C', {'value': ['sale_dict', 'loop_key', 'seller_data', 'name']}),
                ('P_3D', {'value': ['sale_dict', 'loop_key', 'seller_data', 'address']}),
                ('P_4A', {'value': ['sale_dict', 'loop_key', 'seller_data', 'country_code']}),
                ('P_4B', {'value': ['sale_dict', 'loop_key', 'seller_data', 'numeric_vat']}),
                ('P_5A', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'country_code']}),
                ('P_5B', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'numeric_vat']}),
                ('P_6', {'value': ['sale_dict', 'loop_key', 'date_invoice']}),
                ('P_13_1', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_19']}),
                ('P_14_1', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_20']}),
                ('P_13_2', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_17']}),
                ('P_14_2', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_18']}),
                ('P_13_3', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_15']}),
                ('P_14_3', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_16']}),
                # 'P_13_4'
                # 'P_14_4'
                # 'P_13_5'
                # 'P_14_5'
                ('P_13_6', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_13']}),
                ('P_13_7', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_10']}),
                ('P_15', {'value': ['sale_dict', 'loop_key', 'amount_total']}),
                # METODA KASOWA - należy sprawdzić czy dana faktura należy do cash_basis
                ('P_16', {'value': ['sale_dict', 'loop_key', 'cash_basis']}),
                # SAMOFAKTUROWANIE - kiedy nabywca wystawia fakturę na siebie
                ('P_17', {'static_value': 'false'}),
                # ODWROTNE OBCIĄŻENIE - podatki zoo/voo
                ('P_18', {'value': ['sale_dict', 'loop_key', 'reverse_charge']}),
                ('P_19', {'static_value': 'false'}),
                # 'P_19A'
                # 'P_19B'
                # 'P_19C'
                ('P_20', {'static_value': 'false'}),
                # 'P_20A'
                # 'P_20B'
                ('P_21', {'static_value': 'false'}),
                # 'P_21A'
                # 'P_21B'
                # 'P_21C'
                # 'P_22A'
                # 'P_22B'
                # 'P_22C'
                ('P_23', {'static_value': 'false'}),
                ('P_106E_2', {'static_value': 'false'}),
                # 'P_106E_3'
                # 'P_106E_3A'
                ('RodzajFaktury', {'value': ['sale_dict', 'loop_key', 'invoice_type']}),
                ('PrzyczynaKorekty', {'value': ['sale_dict', 'loop_key', 'refund_reason']}),
                ('NrFaKorygowanej', {'value': ['sale_dict', 'loop_key', 'refunded_inv_number']}),
                ('OkresFaKorygowanej', {'value': ['sale_dict', 'loop_key', 'refunded_period']}), #w formacie 01.2018
                ('ZALZaplata', {'value': ['sale_dict', 'loop_key', 'down_payment_value']}),
                ('ZALPodatek', {'value': ['sale_dict', 'loop_key', 'down_payment_tax']}),
            ])
        }
    }),
    ('FakturaCtrl', OrderedDict([
        ('LiczbaFaktur', {'value': ['sale_ctrl', 'lp']}),
        ('WartoscFaktur', {'value': ['sale_ctrl', 'sum_all']}),
    ])),
    ('StawkiPodatku', OrderedDict([
        ('Stawka1', {'static_value': '0.23'}),
        ('Stawka2', {'static_value': '0.08'}),
        ('Stawka3', {'static_value': '0.05'}),
        ('Stawka4', {'static_value': '0.00'}),
        ('Stawka5', {'static_value': '0.00'}),
    ])),
    ('FakturaWiersz', {
        'iterator': 'invoice_lines',
        'loop': {
            'FakturaWiersz': OrderedDict([
                ('attrs', {'typ': 'G'}),
                ('P_2B', {'value': ['invoice_lines', 'loop_key', 'invoice_reference']}),
                ('P_7', {'value': ['invoice_lines', 'loop_key', 'name']}),
                ('P_8A', {'value': ['invoice_lines', 'loop_key', 'uom']}),
                ('P_8B', {'value': ['invoice_lines', 'loop_key', 'qty']}),
                ('P_9A', {'value': ['invoice_lines', 'loop_key', 'price_unit']}),
                # CENTA JEDN BRUTTO
                ('P_9B', {'value': ['invoice_lines', 'loop_key', 'unit_gross']}),
                # KWOTY RABATÓW LUB UPUSTÓW POCHODZĄCYCH Z PRZEDPŁATY
                # jeżeli zaliczka, to procentowo podzielić, a potem znowu na kwotę
                ('P_10', {'value': ['invoice_lines', 'loop_key', 'discount']}),
                ('P_11', {'value': ['invoice_lines', 'loop_key', 'subtotal']}),
                ('P_11A', {'value': ['invoice_lines', 'loop_key', 'gross']}),
                ('P_12', {'value': ['invoice_lines', 'loop_key', 'tax_group']}),
            ])
        }
    }),
    ('FakturaWierszCtrl', OrderedDict([
        ('LiczbaWierszyFaktur', {'value': ['invoice_line_ctrl', 'lp']}),
        ('WartoscWierszyFaktur', {'value': ['invoice_line_ctrl', 'sum_invoice_line']}),
    ])),
])),
])


JPK_FA_2 = OrderedDict([
('JPK', OrderedDict([
    ('attrs', {
        'xmlns': 'http://jpk.mf.gov.pl/wzor/2019/03/21/03211/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2018/08/24/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'JPK_FA',
            'attrs': {
                'kodSystemowy': 'JPK_FA (2)',
                'wersjaSchemy': '1-0',
            }
        }),
        ('WariantFormularza', {'static_value': '2'}),
        ('CelZlozenia', {'static_value': '1'}),
        ('DataWytworzeniaJPK', {'function': 'get_creation_date'}),
        ('DataOd', {'wizard': 'date_from'}),
        ('DataDo', {'wizard': 'date_to'}),
        ('DomyslnyKodWaluty', {'wizard': ['company_id', 'currency_id', 'name']}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('IdentyfikatorPodmiotu', OrderedDict([
            ('dt:NIP', {'value': ['company_data', 'numeric_vat']}),
            ('dt:PelnaNazwa', {'wizard': ['company_id', 'name']}),
            ('dt:REGON', {'wizard': ['company_id', 'regon_code']}),
        ])),
        ('AdresPodmiotu', OrderedDict([
            ('dt:KodKraju', {'wizard': ['company_id', 'country_id', 'code']}),
            ('dt:Wojewodztwo', {'wizard': ['company_id', 'state_id', 'name']}),
            ('dt:Powiat', {'wizard': ['company_id', 'county']}),
            ('dt:Gmina', {'wizard': ['company_id', 'community']}),
            ('dt:Ulica', {'wizard': ['company_id', 'street_declaration']}),
            ('dt:NrDomu', {'wizard': ['company_id', 'house_number']}),
            ('dt:NrLokalu', {'wizard': ['company_id', 'apartament_number']}),
            ('dt:Miejscowosc', {'wizard': ['company_id', 'city']}),
            ('dt:KodPocztowy', {'wizard_function': 'get_company_zip'}),
            ('dt:Poczta', {'wizard': ['company_id', 'post_office']}),
        ])),
    ])),
    ('Falktura', {
        'iterator': 'sale_dict',
        'loop': {
            'Faktura': OrderedDict([
                ('attrs', {'typ': 'G'}),
                ('P_1', {'value': ['sale_dict', 'loop_key', 'date_issue']}),
                ('P_2A', {'value': ['sale_dict', 'loop_key', 'main_reference']}),
                ('P_3A', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'name']}),
                ('P_3B', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'address']}),
                ('P_3C', {'value': ['sale_dict', 'loop_key', 'seller_data', 'name']}),
                ('P_3D', {'value': ['sale_dict', 'loop_key', 'seller_data', 'address']}),
                ('P_4A', {'value': ['sale_dict', 'loop_key', 'seller_data', 'country_code']}),
                ('P_4B', {'value': ['sale_dict', 'loop_key', 'seller_data', 'numeric_vat']}),
                ('P_5A', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'country_code']}),
                ('P_5B', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'numeric_vat']}),
                ('P_6', {'value': ['sale_dict', 'loop_key', 'date_invoice']}),
                ('P_13_1', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_19']}),
                ('P_14_1', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_20']}),
                ('P_13_2', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_17']}),
                ('P_14_2', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_18']}),
                ('P_13_3', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_15']}),
                ('P_14_3', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_16']}),
                # 'P_13_4'
                # 'P_14_4'
                # 'P_13_5'
                # 'P_14_5'
                ('P_13_6', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_13']}),
                ('P_13_7', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_10']}),
                ('P_15', {'value': ['sale_dict', 'loop_key', 'amount_total']}),
                # METODA KASOWA - należy sprawdzić czy dana faktura należy do cash_basis
                ('P_16', {'value': ['sale_dict', 'loop_key', 'cash_basis']}),
                # SAMOFAKTUROWANIE - kiedy nabywca wystawia fakturę na siebie
                ('P_17', {'static_value': 'false'}),
                # ODWROTNE OBCIĄŻENIE - podatki zoo/voo
                ('P_18', {'value': ['sale_dict', 'loop_key', 'reverse_charge']}),
                ('P_19', {'static_value': 'false'}),
                # 'P_19A'
                # 'P_19B'
                # 'P_19C'
                ('P_20', {'static_value': 'false'}),
                # 'P_20A'
                # 'P_20B'
                ('P_21', {'static_value': 'false'}),
                # 'P_21A'
                # 'P_21B'
                # 'P_21C'
                # 'P_22A'
                # 'P_22B'
                # 'P_22C'
                ('P_23', {'static_value': 'false'}),
                ('P_106E_2', {'static_value': 'false'}),
                # 'P_106E_3'
                # 'P_106E_3A'
                ('RodzajFaktury', {'value': ['sale_dict', 'loop_key', 'invoice_type']}),
                ('PrzyczynaKorekty', {'value': ['sale_dict', 'loop_key', 'refund_reason']}),
                ('NrFaKorygowanej', {'value': ['sale_dict', 'loop_key', 'refunded_inv_number']}),
                ('OkresFaKorygowanej', {'value': ['sale_dict', 'loop_key', 'refunded_period']}), #w formacie 01.2018
                ('ZALZaplata', {'value': ['sale_dict', 'loop_key', 'down_payment_value']}),
                ('ZALPodatek', {'value': ['sale_dict', 'loop_key', 'down_payment_tax']}),
            ])
        }
    }),
    ('FakturaCtrl', OrderedDict([
        ('LiczbaFaktur', {'value': ['sale_ctrl', 'lp']}),
        ('WartoscFaktur', {'value': ['sale_ctrl', 'sum_all']}),
    ])),
    ('StawkiPodatku', OrderedDict([
        ('Stawka1', {'static_value': '0.23'}),
        ('Stawka2', {'static_value': '0.08'}),
        ('Stawka3', {'static_value': '0.05'}),
        ('Stawka4', {'static_value': '0.00'}),
        ('Stawka5', {'static_value': '0.00'}),
    ])),
    ('FakturaWiersz', {
        'iterator': 'invoice_lines',
        'loop': {
            'FakturaWiersz': OrderedDict([
                ('attrs', {'typ': 'G'}),
                ('P_2B', {'value': ['invoice_lines', 'loop_key', 'invoice_reference']}),
                ('P_7', {'value': ['invoice_lines', 'loop_key', 'name']}),
                ('P_8A', {'value': ['invoice_lines', 'loop_key', 'uom']}),
                ('P_8B', {'value': ['invoice_lines', 'loop_key', 'qty']}),
                ('P_9A', {'value': ['invoice_lines', 'loop_key', 'price_unit']}),
                # CENTA JEDN BRUTTO
                ('P_9B', {'value': ['invoice_lines', 'loop_key', 'unit_gross']}),
                # KWOTY RABATÓW LUB UPUSTÓW POCHODZĄCYCH Z PRZEDPŁATY
                # jeżeli zaliczka, to procentowo podzielić, a potem znowu na kwotę
                ('P_10', {'value': ['invoice_lines', 'loop_key', 'discount']}),
                ('P_11', {'value': ['invoice_lines', 'loop_key', 'subtotal']}),
                ('P_11A', {'value': ['invoice_lines', 'loop_key', 'gross']}),
                ('P_12', {'value': ['invoice_lines', 'loop_key', 'tax_group']}),
            ])
        }
    }),
    ('FakturaWierszCtrl', OrderedDict([
        ('LiczbaWierszyFaktur', {'value': ['invoice_line_ctrl', 'lp']}),
        ('WartoscWierszyFaktur', {'value': ['invoice_line_ctrl', 'sum_invoice_line']}),
    ])),
])),
])



JPK_FA_3 = OrderedDict([
('JPK', OrderedDict([
    ('attrs', {
        'xmlns': "http://jpk.mf.gov.pl/wzor/2019/09/27/09271/",
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2018/08/24/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'JPK_FA',
            'attrs': {
                'kodSystemowy': 'JPK_FA (3)',
                'wersjaSchemy': '1-0',
            }
        }),
        ('WariantFormularza', {'static_value': '3'}),
        ('CelZlozenia', {'static_value': '1'}),
        ('DataWytworzeniaJPK', {'function': 'get_creation_date'}),
        ('DataOd', {'wizard': 'date_from'}),
        ('DataDo', {'wizard': 'date_to'}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('IdentyfikatorPodmiotu', OrderedDict([
            ('dt:NIP', {'value': ['company_data', 'numeric_vat']}),
            ('dt:PelnaNazwa', {'wizard': ['company_id', 'name']}),
        ])),
        ('AdresPodmiotu', OrderedDict([
            ('dt:KodKraju', {'wizard': ['company_id', 'country_id', 'code']}),
            ('dt:Wojewodztwo', {'wizard': ['company_id', 'state_id', 'name']}),
            ('dt:Powiat', {'wizard': ['company_id', 'county']}),
            ('dt:Gmina', {'wizard': ['company_id', 'community']}),
            ('dt:Ulica', {'wizard': ['company_id', 'street_declaration']}),
            ('dt:NrDomu', {'wizard': ['company_id', 'house_number']}),
            ('dt:NrLokalu', {'wizard': ['company_id', 'apartament_number']}),
            ('dt:Miejscowosc', {'wizard': ['company_id', 'city']}),
            ('dt:KodPocztowy', {'wizard_function': 'get_company_zip'}),
        ])),
    ])),
    ('Faktura', {
        'iterator': 'sale_dict',
        'loop': {
            'Faktura': OrderedDict([
                ('KodWaluty', {'wizard': ['company_id', 'currency_id', 'name']}),
                ('P_1', {'value': ['sale_dict', 'loop_key', 'date_issue']}),
                ('P_2A', {'value': ['sale_dict', 'loop_key', 'main_reference']}),
                ('P_3A', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'name']}),
                ('P_3B', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'address']}),
                ('P_3C', {'value': ['sale_dict', 'loop_key', 'seller_data', 'name']}),
                ('P_3D', {'value': ['sale_dict', 'loop_key', 'seller_data', 'address']}),
                ('P_4A', {'value': ['sale_dict', 'loop_key', 'seller_data', 'country_code']}),
                ('P_4B', {'value': ['sale_dict', 'loop_key', 'seller_data', 'numeric_vat']}),
                ('P_5A', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'country_code']}),
                ('P_5B', {'value': ['sale_dict', 'loop_key', 'purchaser_data', 'numeric_vat']}),
                ('P_6', {'value': ['sale_dict', 'loop_key', 'date_invoice']}),
                ('P_13_1', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_19']}),
                ('P_14_1', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_20']}),
                # P_14_1W
                ('P_13_2', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_17']}),
                ('P_14_2', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_18']}),
                # P_14_2W
                ('P_13_3', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_15']}),
                ('P_14_3', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_16']}),
                # P_14_3W
                # P_13_4??
                # P_14_4??
                # P_14_4W
                # P_13_5
                ('P_13_6', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_13']}),
                ('P_13_7', {'value': ['sale_dict', 'loop_key', 'tax_values', 'K_10']}),
                ('P_15', {'value': ['sale_dict', 'loop_key', 'amount_total']}),
                # METODA KASOWA - należy sprawdzić czy dana faktura należy do cash_basis
                ('P_16', {'value': ['sale_dict', 'loop_key', 'cash_basis']}),
                # SAMOFAKTUROWANIE - kiedy nabywca wystawia fakturę na siebie
                ('P_17', {'static_value': 'false'}),
                # ODWROTNE OBCIĄŻENIE - podatki zoo/voo
                ('P_18', {'value': ['sale_dict', 'loop_key', 'reverse_charge']}),
                ('P_18A', {'static_value': 'false'}),
                ('P_19', {'static_value': 'false'}),
                # P_19A
                # P_19B
                # P_19C
                ('P_20', {'static_value': 'false'}),
                # P_20A
                # P_20B
                ('P_21', {'static_value': 'false'}),
                # P_21A
                # P_21B
                # P_21C
                ('P_22', {'static_value': 'false'}),
                # P_22A
                # P_22B
                # P_22C
                ('P_23', {'static_value': 'false'}),
                ('P_106E_2', {'static_value': 'false'}),
                ('P_106E_3', {'static_value': 'false'}),
                # P_106E_3A
                ('RodzajFaktury', {'value': ['sale_dict', 'loop_key', 'invoice_type']}),
                ('PrzyczynaKorekty', {'value': ['sale_dict', 'loop_key', 'refund_reason']}),
                ('NrFaKorygowanej', {'value': ['sale_dict', 'loop_key', 'refunded_inv_number']}),
                ('OkresFaKorygowanej', {'value': ['sale_dict', 'loop_key', 'refunded_period']}), #w formacie 01.2018
                # ('NrFaZaliczkowej', {'value': ['sale_dict', 'loop_key', '????????']}),
            ])
        }
    }),
    ('FakturaCtrl', OrderedDict([
        ('LiczbaFaktur', {'value': ['sale_ctrl', 'lp']}),
        ('WartoscFaktur', {'value': ['sale_ctrl', 'sum_all']}),
    ])),
    ('FakturaWiersz', {
        'iterator': 'invoice_lines',
        'loop': {
            'FakturaWiersz': OrderedDict([
                ('P_2B', {'value': ['invoice_lines', 'loop_key', 'invoice_reference']}),
                ('P_7', {'value': ['invoice_lines', 'loop_key', 'name']}),
                ('P_8A', {'value': ['invoice_lines', 'loop_key', 'uom']}),
                ('P_8B', {'value': ['invoice_lines', 'loop_key', 'qty']}),
                ('P_9A', {'value': ['invoice_lines', 'loop_key', 'price_unit']}),
                # CENA JEDN BRUTTO
                ('P_9B', {'value': ['invoice_lines', 'loop_key', 'unit_gross']}),
                # KWOTY RABATÓW LUB UPUSTÓW POCHODZĄCYCH Z PRZEDPŁATY
                # jeżeli zaliczka, to procentowo podzielić, a potem znowu na kwotę
                ('P_10', {'value': ['invoice_lines', 'loop_key', 'discount']}),
                ('P_11', {'value': ['invoice_lines', 'loop_key', 'subtotal']}),
                ('P_11A', {'value': ['invoice_lines', 'loop_key', 'gross']}),
                ('P_12', {'value': ['invoice_lines', 'loop_key', 'tax_group']}),
            ])
        }
    }),
    ('FakturaWierszCtrl', OrderedDict([
        ('LiczbaWierszyFaktur', {'value': ['invoice_line_ctrl', 'lp']}),
        ('WartoscWierszyFaktur', {'value': ['invoice_line_ctrl', 'sum_invoice_line']}),
    ])),
    ('Zamowienie', {
        'iterator': 'order_downpayment',
        'loop': {
            'Zamowienie': OrderedDict([
                ('P_2AZ', {'value': ['order_downpayment', 'loop_key', 'main_reference']}),
                ('WartoscZamowienia', {'value': ['order_downpayment', 'loop_key', 'order_total']}),
                ('ZamowienieWiersz', {
                    'iterator': 'order_line',
                    'loop_2': {
                        'ZamowienieWiersz': OrderedDict([
                            ('P_7Z', {'value': ['order_line', 'loop_key', 'product']}),
                            ('P_8AZ', {'value': ['order_line', 'loop_key', 'uom']}),
                            ('P_8BZ', {'value': ['order_line', 'loop_key', 'qty']}),
                            ('P_9AZ', {'value': ['order_line', 'loop_key', 'price_unit']}),
                            ('P_11NettoZ', {'value': ['order_line', 'loop_key', 'price_subtotal']}),
                            ('P_11VatZ', {'value': ['order_line', 'loop_key', 'tax']}),
                            ('P_12Z', {'value': ['order_line', 'loop_key', 'tax_group']}),
                        ])
                        }
                    })
    ])}}),

    ('ZamowienieCtrl', OrderedDict([
        ('LiczbaZamowien', {'value': ['order_ctrl', 'lp']}),
        ('WartoscZamowien', {'value': ['order_ctrl', 'order_sum']}),
        ]))
])),
])



JPK_KR = OrderedDict([
('JPK', OrderedDict([
    ('attrs', {
        'xmlns': 'http://jpk.mf.gov.pl/wzor/2016/03/09/03091/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'JPK_KR',
            'attrs': {
                'kodSystemowy': 'JPK_KR (1)',
                'wersjaSchemy': '1-0',
            }
        }),
        ('WariantFormularza', {'static_value': '1'}),
        ('CelZlozenia', {'static_value': '1'}),
        ('DataWytworzeniaJPK', {'function': 'get_creation_date'}),
        ('DataOd', {'wizard': 'date_from'}),
        ('DataDo', {'wizard': 'date_to'}),
        ('DomyslnyKodWaluty', {'wizard': ['company_id', 'currency_id', 'name']}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('IdentyfikatorPodmiotu', OrderedDict([
            ('dt:NIP', {'value': ['company_data', 'numeric_vat']}),
            ('dt:PelnaNazwa', {'wizard': ['company_id', 'name']}),
            ('dt:REGON', {'wizard': ['company_id', 'regon_code']}),
        ])),
        ('AdresPodmiotu', OrderedDict([
            ('dt:KodKraju', {'wizard': ['company_id', 'country_id', 'code']}),
            ('dt:Wojewodztwo', {'wizard': ['company_id', 'state_id', 'name']}),
            ('dt:Powiat', {'wizard': ['company_id', 'county']}),
            ('dt:Gmina', {'wizard': ['company_id', 'community']}),
            ('dt:Ulica', {'wizard': ['company_id', 'street_declaration']}),
            ('dt:NrDomu', {'wizard': ['company_id', 'house_number']}),
            ('dt:NrLokalu', {'wizard': ['company_id', 'apartament_number']}),
            ('dt:Miejscowosc', {'wizard': ['company_id', 'city']}),
            ('dt:KodPocztowy', {'wizard_function': 'get_company_zip'}),
            ('dt:Poczta', {'wizard': ['company_id', 'post_office']}),
        ])),
    ])),
    ('ZOIS', {
        'iterator': 'acc_dict',
        'loop': {
            'ZOiS': OrderedDict([
                ('attrs', {'typ': 'G'}),
                ('KodKonta', {'value': ['acc_dict', 'loop_key', 'code']}),
                ('OpisKonta', {'value': ['acc_dict', 'loop_key', 'name']}),
                ('TypKonta', {'value': ['acc_dict', 'loop_key', 'type']}),
                ('KodZespolu', {'value': ['acc_dict', 'loop_key', 'group_code']}),
                ('OpisZespolu', {'value': ['acc_dict', 'loop_key', 'group_name']}),
                ('KodKategorii', {'value': ['acc_dict', 'loop_key', 'category_code']}),
                ('OpisKategorii', {'value': ['acc_dict', 'loop_key', 'category_name']}),
                ('KodPodkategorii', {'value': ['acc_dict', 'loop_key', 'subcategory_code']}),
                ('BilansOtwarciaWinien', {'value': ['acc_dict', 'loop_key', 'ob_debit']}),
                ('BilansOtwarciaMa', {'value': ['acc_dict', 'loop_key', 'ob_credit']}),
                ('ObrotyWinien', {'value': ['acc_dict', 'loop_key', 'month_debit']}),
                ('ObrotyMa', {'value': ['acc_dict', 'loop_key', 'month_credit']}),
                ('ObrotyWinienNarast', {'value': ['acc_dict', 'loop_key', 'year_debit']}),
                ('ObrotyMaNarast', {'value': ['acc_dict', 'loop_key', 'year_credit']}),
                ('SaldoWinien', {'value': ['acc_dict', 'loop_key', 'balance_debit']}),
                ('SaldoMa', {'value': ['acc_dict', 'loop_key', 'balance_credit']}),

            ])
        }
    }),
    ('DZIENNIK',{
        'iterator':'journal_dict',
        'loop':{
            'Dziennik': OrderedDict([
                ('attrs',{'typ':'G'}),
                ('LpZapisuDziennika', {'value': ['journal_dict', 'loop_key', 'lp']}),
                ('NrZapisuDziennika', {'value': ['journal_dict', 'loop_key', 'nr_zapisu']}),
                ('OpisDziennika', {'value': ['journal_dict', 'loop_key', 'description']}),
                ('NrDowoduKsiegowego', {'value': ['journal_dict', 'loop_key', 'ref']}),
                ('RodzajDowodu', {'value': ['journal_dict', 'loop_key', 'type']}),
                ('DataOperacji', {'value': ['journal_dict', 'loop_key', 'operation_date']}),
                ('DataDowodu', {'value': ['journal_dict', 'loop_key', 'document_date']}),
                ('DataKsiegowania', {'value': ['journal_dict', 'loop_key', 'inv_date']}),
                ('KodOperatora', {'value': ['journal_dict', 'loop_key', 'operator_code']}),
                ('OpisOperacji', {'value': ['journal_dict', 'loop_key', 'operation_descr']}),
                ('DziennikKwotaOperacji', {'value': ['journal_dict', 'loop_key', 'amount']}),
            ])
        }
    }),
    ('DziennikCtrl', OrderedDict([
        ('LiczbaWierszyDziennika', {'value': ['journal_ctrl', 'lj']}),
        ('SumaKwotOperacji', {'value': ['journal_ctrl', 'sum_amount_journal']}),
    ])),
    ('KONTOZapis', {
        'iterator': 'acc_ml_dict',
        'loop': {
            'KontoZapis': OrderedDict([
                ('attrs', {'typ': 'G'}),
                ('LpZapisu', {'value': ['acc_ml_dict', 'loop_key', 'lp']}),
                ('NrZapisu', {'value': ['acc_ml_dict', 'loop_key', 'nr_zapisu']}),
                ('KodKontaWinien', {'value': ['acc_ml_dict', 'loop_key', 'account_debit']}),
                ('KwotaWinien', {'value': ['acc_ml_dict', 'loop_key', 'debit']}),
                ('KwotaWinienWaluta', {'value': ['acc_ml_dict', 'loop_key', 'amount_currency_debit']}),
                ('KodWalutyWinien', {'value': ['acc_ml_dict', 'loop_key', 'currency_code_debit']}),
                ('OpisZapisuWinien', {'value': ['acc_ml_dict', 'loop_key', 'desc_debit']}),
                ('KodKontaMa', {'value': ['acc_ml_dict', 'loop_key', 'account_credit']}),
                ('KwotaMa', {'value': ['acc_ml_dict', 'loop_key', 'credit']}),
                ('KwotaMaWaluta', {'value': ['acc_ml_dict', 'loop_key', 'amount_currency_credit']}),
                ('KodWalutyMa', {'value': ['acc_ml_dict', 'loop_key', 'currency_code_credit']}),
                ('OpisZapisuMa', {'value': ['acc_ml_dict', 'loop_key', 'desc_credit']}),
            ])
        }
    }),
    ('KontoZapisCtrl', OrderedDict([
        ('LiczbaWierszyKontoZapisj', {'value': ['acc_ml_ctrl', 'lp']}),
        ('SumaWinien', {'value': ['acc_ml_ctrl', 'sum_debit']}),
        ('SumaMa', {'value': ['acc_ml_ctrl', 'sum_credit']}),
    ])),
])),
])

JPK_WB = OrderedDict([
('JPK', OrderedDict([
    ('attrs', {
        'xmlns': 'http://jpk.mf.gov.pl/wzor/2016/03/09/03092/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'JPK_WB',
            'attrs': {
                'kodSystemowy': 'JPK_WB (1)',
                'wersjaSchemy': '1-0',
            }
        }),
        ('WariantFormularza', {'static_value': '1'}),
        ('CelZlozenia', {'static_value': '1'}),
        ('DataWytworzeniaJPK', {'function': 'get_creation_date'}),
        ('DataOd', {'wizard': 'date_from'}),
        ('DataDo', {'wizard': 'date_to'}),
        ('DomyslnyKodWaluty', {'wizard': ['company_id', 'currency_id', 'name']}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('IdentyfikatorPodmiotu', OrderedDict([
            ('dt:NIP', {'value': ['company_data', 'numeric_vat']}),
            ('dt:PelnaNazwa', {'wizard': ['company_id', 'name']}),
            ('dt:REGON', {'wizard': ['company_id', 'regon_code']}),
        ])),
        ('AdresPodmiotu', OrderedDict([
            ('dt:KodKraju', {'wizard': ['company_id', 'country_id', 'code']}),
            ('dt:Wojewodztwo', {'wizard': ['company_id', 'state_id', 'name']}),
            ('dt:Powiat', {'wizard': ['company_id', 'county']}),
            ('dt:Gmina', {'wizard': ['company_id', 'community']}),
            ('dt:Ulica', {'wizard': ['company_id', 'street_declaration']}),
            ('dt:NrDomu', {'wizard': ['company_id', 'house_number']}),
            ('dt:NrLokalu', {'wizard': ['company_id', 'apartament_number']}),
            ('dt:Miejscowosc', {'wizard': ['company_id', 'city']}),
            ('dt:KodPocztowy', {'wizard_function': 'get_company_zip'}),
            ('dt:Poczta', {'wizard': ['company_id', 'post_office']}),
        ])),
    ])),
    ('NumerRachunku', {'value': ['acc_number']}),
    ('Salda', OrderedDict([
        ('SaldoPoczatkowe', {'value': ['balance', 'balance_start']}),
        ('SaldoKoncowe', {'value': ['balance', 'balance_end']}),
    ])),
    ('WYCIAGWiersz', {
        'iterator': 'balance_ln',
        'loop': {
            'WyciagWiersz': OrderedDict([
                ('attrs', {'typ': 'G'}),
                ('NumerWiersza', {'value': ['balance_ln', 'loop_key', 'lp']}),
                ('DataOperacji', {'value': ['balance_ln', 'loop_key', 'date']}),
                ('NazwaPodmiotu', {'value': ['balance_ln', 'loop_key', 'name']}),
                ('OpisOperacji', {'value': ['balance_ln', 'loop_key', 'op_desc']}),
                ('KwotaOperacji', {'value': ['balance_ln', 'loop_key', 'amount']}),
                ('SaldoOperacji', {'value': ['balance_ln', 'loop_key', 'balance']}),
            ])
        }
    }),
    ('WyciagCtrl', OrderedDict([
        ('LiczbaWierszy', {'value': ['balance_ln_ctrl', 'lp']}),
        ('SumaObciazen', {'value': ['balance_ln_ctrl', 'charge_sum']}),
        ('SumaUznan', {'value': ['balance_ln_ctrl', 'credit_sum']}),
    ])),
]))
])

JPK_VAT_3 = OrderedDict([
('JPK', OrderedDict([
    ('attrs', {
        'xmlns': 'http://jpk.mf.gov.pl/wzor/2017/11/13/1113/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'JPK_VAT',
            'attrs': {
                'kodSystemowy': 'JPK_VAT (3)',
                'wersjaSchemy': '1-1',
            }
        }),
        ('WariantFormularza', {'static_value': '3'}),
        ('CelZlozenia', {'wizard': 'correction_number'}),
        ('DataWytworzeniaJPK', {'function': 'get_creation_date'}),
        ('DataOd', {'wizard': 'date_from'}),
        ('DataDo', {'wizard': 'date_to'}),
        ('NazwaSystemu', {'static_value': 'Odoo'}),
    ])),
    ('Podmiot1', OrderedDict([
        ('NIP',  {'value': ['company_data', 'numeric_vat']}),
        ('PelnaNazwa', {'wizard': ['company_id', 'name']}),
    ])),
    ('SPRZEDAZWIERSZ', {
        'iterator': 'sale_dict',
        'loop': {
            'SprzedazWiersz': OrderedDict([
                ('LpSprzedazy', {'value': 'loop_index'}),
                ('NrKontrahenta', {'value': ['sale_dict', 'loop_key', 'partner_data', 'vat']}),
                ('NazwaKontrahenta', {'value': ['sale_dict', 'loop_key', 'partner_data', 'name']}),
                ('AdresKontrahenta', {'value': ['sale_dict', 'loop_key', 'partner_data', 'address']}),
                ('DowodSprzedazy', {'value': ['sale_dict', 'loop_key', 'main_reference']}),
                ('DataWystawienia', {'value': ['sale_dict', 'loop_key', 'date_issue']}),
                ('DataSprzedazy', {'value': ['sale_dict', 'loop_key', 'sale_date']}),
                ('PODATKI', {'value_loop': ['sale_dict', 'loop_key', 'tax_values']})

            ])
        }
    }),
    ('SprzedazCtrl', OrderedDict([
        ('skip_empty', ['sale_ctrl']),
        ('LiczbaWierszySprzedazy', {'value': ['sale_ctrl', 'lp']}),
        ('PodatekNalezny', {'value': ['sale_ctrl', 'sum_taxes']}),
    ])),
    ('ZAKUPWIERSZ', {
        'iterator': 'purchase_dict',
        'loop': {
            'ZakupWiersz': OrderedDict([
                ('LpZakupu', {'value': 'loop_index'}),
                ('NrDostawcy', {'value': ['purchase_dict', 'loop_key', 'vat']}),
                ('NazwaDostawcy', {'value': ['purchase_dict', 'loop_key', 'partner_name']}),
                ('AdresDostawcy', {'value': ['purchase_dict', 'loop_key', 'address']}),
                ('DowodZakupu', {'value': ['purchase_dict', 'loop_key', 'main_reference']}),
                ('DataZakupu', {'value': ['purchase_dict', 'loop_key', 'purchase_date']}),
                ('PODATKI', {'value_loop': ['purchase_dict', 'loop_key', 'tax_values']}),
            ]),
        }
    }),
    ('ZakupCtrl', OrderedDict([
        ('skip_empty', ['purchase_ctrl']),
        ('LiczbaWierszyZakupow', {'value': ['purchase_ctrl', 'lp']}),
        ('PodatekNaliczony', {'value': ['purchase_ctrl', 'sum_taxes']})
    ]))
]))
])

JPK_VAT_7_18 = OrderedDict([
('Deklaracja', OrderedDict([
    ('attrs', {
        'xmlns': 'http://crd.gov.pl/wzor/2018/08/27/5658/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'VAT-7',
            'attrs': {
                'kodSystemowy': 'VAT-7 (18)',
                'kodPodatku': 'VAT',
                'rodzajZobowiazania': 'Z',
                'wersjaSchemy': '1-1E',
            }
        }),
        ('WariantFormularza', {'static_value': '18'}),
        ('CelZlozenia', {
            'static_value': '1',
            'attrs': {'poz': 'P_7'}
        }),
        ('Rok', {'value': ['company_data', 'year']}),
        ('Miesiac', {'value': ['company_data', 'month']}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('attrs', {'rola': 'Podatnik'}),
        ('OsobaNiefizyczna', OrderedDict([
            ('NIP', {'value': ['company_data', 'numeric_vat']}),
            ('PelnaNazwa', {'value': ['company_data', 'name']}),
            #('PelnaNazwa', {'value': ['company_data', 'name'], 'wizard': ['company_id', 'regon_code'] }),
            #('REGON', {'wizard': ['company_id', 'regon_code']}),
        ])),
    ])),
    ('PozycjeSzczegolowe', {
        'POZYCJESZCZEGOLOWE': {
            'value_loop': ['taxes_sum_dict'],
            'force_int': True,
            'no_order': True
        }
    }),
    ('Pouczenia', {'static_value': '1'}),

]))
])


JPK_VAT_7_19 = OrderedDict([
('Deklaracja', OrderedDict([
    ('attrs', {
        'xmlns': 'http://crd.gov.pl/wzor/2019/02/11/7013/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2018/08/24/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'VAT-7',
            'attrs': {
                'kodSystemowy': 'VAT-7 (19)',
                'kodPodatku': 'VAT',
                'rodzajZobowiazania': 'Z',
                'wersjaSchemy': '1-0E',
            }
        }),
        ('WariantFormularza', {'static_value': '19'}),
        ('CelZlozenia', {
            'static_value': '1',
            'attrs': {'poz': 'P_7'}
        }),
        ('Rok', {'value': ['company_data', 'year']}),
        ('Miesiac', {'value': ['company_data', 'month']}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('attrs', {'rola': 'Podatnik'}),
        ('OsobaNiefizyczna', OrderedDict([
            ('NIP', {'value': ['company_data', 'numeric_vat']}),
            ('PelnaNazwa', {'value': ['company_data', 'name']}),
            #('PelnaNazwa', {'value': ['company_data', 'name'], 'wizard': ['company_id', 'regon_code'] }),
            #('REGON', {'wizard': ['company_id', 'regon_code']}),
        ])),
    ])),
    ('PozycjeSzczegolowe', {
        'POZYCJESZCZEGOLOWE': {
            'value_loop': ['taxes_sum_dict'],
            'force_int': True,
            'no_order': True
        }
    }),
    ('Pouczenia', {'static_value': '1'}),
]))
])

JPK_VAT_7_20 = OrderedDict([
('Deklaracja', OrderedDict([
    ('attrs', {
        'xmlns': 'http://crd.gov.pl/wzor/2019/11/08/8836/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2018/08/24/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'VAT-7',
            'attrs': {
                'kodSystemowy': 'VAT-7 (20)',
                'kodPodatku': 'VAT',
                'rodzajZobowiazania': 'Z',
                'wersjaSchemy': '1-0E',
            }
        }),
        ('WariantFormularza', {'static_value': '20'}),
        ('CelZlozenia', {
            'static_value': '1',
            'attrs': {'poz': 'P_7'}
        }),
        ('Rok', {'value': ['company_data', 'year']}),
        ('Miesiac', {'value': ['company_data', 'month']}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('attrs', {'rola': 'Podatnik'}),
        ('OsobaNiefizyczna', OrderedDict([
            ('NIP', {'value': ['company_data', 'numeric_vat']}),
            ('PelnaNazwa', {'value': ['company_data', 'name']}),
            #('PelnaNazwa', {'value': ['company_data', 'name'], 'wizard': ['company_id', 'regon_code'] }),
            #('REGON', {'wizard': ['company_id', 'regon_code']}),
        ])),
    ])),
    ('PozycjeSzczegolowe', {
        'POZYCJESZCZEGOLOWE': {
            'value_loop': ['taxes_sum_dict'],
            'force_int': True,
            'no_order': True
        }
    }),
    ('Pouczenia', {'static_value': '1'}),
]))
])


JPK_VAT_7K_12 = OrderedDict([
('Deklaracja', OrderedDict([
    ('attrs', {
        'xmlns': 'http://crd.gov.pl/wzor/2018/08/28/5663/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'VAT-7K',
            'attrs': {
                'kodSystemowy': 'VAT-7K (12)',
                'kodPodatku': 'VAT',
                'rodzajZobowiazania': 'Z',
                'wersjaSchemy': '1-2E',
            }
        }),
        ('WariantFormularza', {'static_value': '12'}),
        ('CelZlozenia', {
            'static_value': '1',
            'attrs': {'poz': 'P_7'}
        }),
        ('Rok', {'value': ['company_data', 'year']}),
        ('Kwartal', {'value': ['company_data', 'quarter']}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('attrs', {'rola': 'Podatnik'}),
        ('OsobaNiefizyczna', OrderedDict([
            ('NIP', {'value': ['company_data', 'numeric_vat']}),
            ('PelnaNazwa', {'value': ['company_data', 'name']}),
            #('REGON', {'wizard': ['company_id', 'regon_code']}),
        ])),
    ])),
    ('PozycjeSzczegolowe', {
        'POZYCJESZCZEGOLOWE': {
            'value_loop': ['taxes_sum_dict'],
            'force_int': True,
            'no_order': True
        }
    }),
    ('Pouczenia', {'static_value': '1'}),
]))
])


JPK_VAT_7K_13 = OrderedDict([
('Deklaracja', OrderedDict([
    ('attrs', {
        'xmlns': 'http://crd.gov.pl/wzor/2019/02/11/7012/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2018/08/24/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'VAT-7K',
            'attrs': {
                'kodSystemowy': 'VAT-7K (13)',
                'kodPodatku': 'VAT',
                'rodzajZobowiazania': 'Z',
                'wersjaSchemy': '1-0E',
            }
        }),
        ('WariantFormularza', {'static_value': '13'}),
        ('CelZlozenia', {
            'static_value': '1',
            'attrs': {'poz': 'P_7'}
        }),
        ('Rok', {'value': ['company_data', 'year']}),
        ('Kwartal', {'value': ['company_data', 'quarter']}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('attrs', {'rola': 'Podatnik'}),
        ('OsobaNiefizyczna', OrderedDict([
            ('NIP', {'value': ['company_data', 'numeric_vat']}),
            ('PelnaNazwa', {'value': ['company_data', 'name']}),
            #('REGON', {'wizard': ['company_id', 'regon_code']}),
        ])),
    ])),
    ('PozycjeSzczegolowe', {
        'POZYCJESZCZEGOLOWE': {
            'value_loop': ['taxes_sum_dict'],
            'force_int': True,
            'no_order': True
        }
    }),
    ('Pouczenia', {'static_value': '1'}),
]))
])

JPK_VAT_7K_14 = OrderedDict([
('Deklaracja', OrderedDict([
    ('attrs', {
        'xmlns': 'http://crd.gov.pl/wzor/2019/11/08/8838/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2018/08/24/eD/DefinicjeTypy/',
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'VAT-7K',
            'attrs': {
                'kodSystemowy': 'VAT-7K (14)',
                'kodPodatku': 'VAT',
                'rodzajZobowiazania': 'Z',
                'wersjaSchemy': '1-0E',
            }
        }),
        ('WariantFormularza', {'static_value': '14'}),
        ('CelZlozenia', {
            'static_value': '1',
            'attrs': {'poz': 'P_7'}
        }),
        ('Rok', {'value': ['company_data', 'year']}),
        ('Kwartal', {'value': ['company_data', 'quarter']}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('attrs', {'rola': 'Podatnik'}),
        ('OsobaNiefizyczna', OrderedDict([
            ('NIP', {'value': ['company_data', 'numeric_vat']}),
            ('PelnaNazwa', {'value': ['company_data', 'name']}),
            #('REGON', {'wizard': ['company_id', 'regon_code']}),
        ])),
    ])),
    ('PozycjeSzczegolowe', {
        'POZYCJESZCZEGOLOWE': {
            'value_loop': ['taxes_sum_dict'],
            'force_int': True,
            'no_order': True
        }
    }),
    ('Pouczenia', {'static_value': '1'}),
]))
])

JPK_UE_4 = OrderedDict([
('Deklaracja', OrderedDict([
    ('attrs', {
        'xmlns': 'http://crd.gov.pl/wzor/2017/01/11/3846/',
        'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/'
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'VAT-UE',
            'attrs': {
                'kodSystemowy': 'VAT-UE (4)',
                'wersjaSchemy': '1-0E',
            }
        }),
        ('WariantFormularza', {'static_value': '4'}),
        ('Rok', {'value': ['company_data', 'year']}),
        ('Miesiac', {'value': ['company_data', 'month']}),
        ('CelZlozenia', {'static_value': '1'}),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('attrs', {'rola': 'Podatnik'}),
        ('dt:OsobaNiefizyczna', OrderedDict([
            ('dt:NIP', {'value': ['company_data', 'numeric_vat']}),
            ('dt:PelnaNazwa', {'value': ['company_data', 'name']}),
            ('dt:REGON', {'value': ['company_data', 'regon_code']}),
        ])),
    ])),
    ('PozycjeSzczegolowe', OrderedDict([
        ('GRUPA1', {
            'iterator': ['ue_dict', 'UE_C'],
            'loop': {
                'Grupa1': OrderedDict([
                    ('P_Da', {'value': ['ue_dict', 'UE_C', 'loop_key', 'country_code']}),
                    ('P_Db', {'value': ['ue_dict', 'UE_C', 'loop_key', 'vat']}),
                    ('P_Dc', {'value': ['ue_dict', 'UE_C', 'loop_key', 'INT_amount']}),
                    ('P_Dd', {'static_value': '1'})
                ])
            }
        }),
        ('GRUPA2', {
            'iterator': ['ue_dict', 'UE_D'],
            'loop': {
                'Grupa2': OrderedDict([
                    ('P_Na', {'value': ['ue_dict', 'UE_D', 'loop_key', 'country_code']}),
                    ('P_Nb', {'value': ['ue_dict', 'UE_D', 'loop_key', 'vat']}),
                    ('P_Nc', {'value': ['ue_dict', 'UE_D', 'loop_key', 'INT_amount']}),
                    ('P_Nd', {'static_value': '1'}),
                ])
            }
        }),
        ('GRUPA3', {
            'iterator': ['ue_dict', 'UE_E'],
            'loop': {
                'Grupa3': OrderedDict([
                    ('P_Ua', {'value': ['ue_dict', 'UE_E', 'loop_key', 'country_code']}),
                    ('P_Ub', {'value': ['ue_dict', 'UE_E', 'loop_key', 'vat']}),
                    ('P_Uc', {'value': ['ue_dict', 'UE_E', 'loop_key', 'INT_amount']}),
                ])
            }
        }),
    ])),
    ('Pouczenie', {'static_value': '1'})
]))
])

JPK_V7M = OrderedDict([
('JPK', OrderedDict([
    ('attrs', {
        'xmlns': 'http://crd.gov.pl/wzor/2020/05/08/9393/',
        'xmlns:etd':"http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2020/03/11/eD/DefinicjeTypy/",
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'JPK_VAT',
            'attrs': {
                'kodSystemowy': 'JPK_V7M (1)',
                'wersjaSchemy': '1-2E',
            }
        }),
        ('WariantFormularza', {'static_value': '1'}),
        ('DataWytworzeniaJPK', {'function': 'get_creation_date'}),
        ('NazwaSystemu', {'static_value': 'Odoo'}),
        ('CelZlozenia', {
            'wizard': 'correction_number',
            'attrs': {'poz': 'P_7'}
        }),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
        ('Rok', {'value': ['company_data', 'year']}),
        ('Miesiac', {'value': ['company_data', 'month']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('attrs', {'rola': 'Podatnik'}),
        ('OsobaFizyczna', OrderedDict([
            ('etd:NIP', {'value': ['company_data', 'numeric_vat']}),
            ('etd:ImiePierwsze', {'value': ['company_data', 'first_name']}),
            ('etd:Nazwisko', {'value': ['company_data', 'surname']}),
            ('etd:DataUrodzenia', {'value': ['company_data', 'birth_date']}),
            ('Email', {'value': ['company_data', 'email']}),
        ])),
        ('OsobaNiefizyczna', OrderedDict([
            ('NIP', {'value': ['company_data', 'numeric_vat']}),
            ('PelnaNazwa', {'value': ['company_data', 'name']}),
            ('Email', {'value': ['company_data', 'email']}),
        ])),
    ])),
    ('Deklaracja', OrderedDict([
            ('Naglowek', OrderedDict([
                ('KodFormularzaDekl', {
                    'static_value': 'VAT-7',
                    'attrs': {
                        'kodSystemowy': 'VAT-7 (21)',
                        'kodPodatku': 'VAT',
                        'rodzajZobowiazania': 'Z',
                        'wersjaSchemy': '1-2E',
                    }}),
                ('WariantFormularzaDekl', {'static_value': '21'}),
                ])),
            ('PozycjeSzczegolowe', {
                'POZYCJESZCZEGOLOWE': {
                    'value_loop': ['taxes_sum_dict'],
                    'force_int': True,
                    'no_order': True
                }
            }),
            ('Pouczenia', {'static_value': '1'}),
        ])),
    ('Ewidencja', OrderedDict([
        ('SPRZEDAZWIERSZ', {
            'iterator': 'sale_dict',
            'loop': {
                'SprzedazWiersz': OrderedDict([
                    ('LpSprzedazy', {'value': 'loop_index'}),
                    ('KodKrajuNadaniaTIN', {'value': ['sale_dict', 'loop_key', 'partner_data', 'country_code']}),
                    ('NrKontrahenta', {'value': ['sale_dict', 'loop_key', 'partner_data', 'numeric_vat']}),
                    ('NazwaKontrahenta', {'value': ['sale_dict', 'loop_key', 'partner_data', 'name']}),
                    ('DowodSprzedazy', {'value': ['sale_dict', 'loop_key', 'main_reference']}),
                    ('DataWystawienia', {'value': ['sale_dict', 'loop_key', 'date_issue']}),
                    ('DataSprzedazy', {'value': ['sale_dict', 'loop_key', 'sale_date']}),
                    ('TypDokumentu', {'value': ['sale_dict', 'loop_key', 'doc_type_vdek']}),
                    ('ZNACZNIKI', {'value_loop': ['sale_dict', 'loop_key', 'product_tax_markers'], 'force_int': True, 'no_order': True }),
                    ('ZNACZNIKI_PROCEDUR', {'value_loop': ['sale_dict', 'loop_key', 'procedures_markers'], 'force_int': True, 'no_order': True}),
                    ('PODATKI', {'value_loop': ['sale_dict', 'loop_key', 'tax_values']}),
                ])
            }
        }),
        ('SprzedazCtrl', OrderedDict([
            ('skip_empty', ['sale_ctrl']),
            ('LiczbaWierszySprzedazy', {'value': ['sale_ctrl', 'lp']}),
            ('PodatekNalezny', {'value': ['sale_ctrl', 'sum_taxes']}),
        ])),
        ('ZAKUPWIERSZ', {
            'iterator': 'purchase_dict',
            'loop': {
                'ZakupWiersz': OrderedDict([
                    ('LpZakupu', {'value': 'loop_index'}),
                    ('KodKrajuNadaniaTIN', {'value': ['purchase_dict', 'loop_key', 'country_code']}),
                    ('NrDostawcy', {'value': ['purchase_dict', 'loop_key', 'numeric_vat']}),
                    ('NazwaDostawcy', {'value': ['purchase_dict', 'loop_key', 'partner_name']}),
                    ('DowodZakupu', {'value': ['purchase_dict', 'loop_key', 'main_reference']}),
                    ('DataZakupu', {'value': ['purchase_dict', 'loop_key', 'purchase_date']}),
                    ('DataWplywu', {'value': ['purchase_dict', 'loop_key', 'date_recived']}),
                    ('DokumentZakupu', {'value': ['purchase_dict', 'loop_key', 'purchase_doc_vdek']}),
                    ('ZNACZNIKI_PROCEDUR', {'value_loop': ['purchase_dict', 'loop_key', 'procedures_markers'], 'force_int': True, 'no_order': True}),
                    ('PODATKI', {'value_loop': ['purchase_dict', 'loop_key', 'tax_values']}),
                ]),
            }
        }),
        ('ZakupCtrl', OrderedDict([
            ('skip_empty', ['purchase_ctrl']),
            ('LiczbaWierszyZakupow', {'value': ['purchase_ctrl', 'lp']}),
            ('PodatekNaliczony', {'value': ['purchase_ctrl', 'sum_taxes']})
        ]))
        ]))
        ,
])),
])



JPK_V7K = OrderedDict([
('JPK', OrderedDict([
    ('attrs', {
        'xmlns': 'http://crd.gov.pl/wzor/2020/05/08/9394/',
        'xmlns:etd' : "http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2020/03/11/eD/DefinicjeTypy/",
    }),
    ('Naglowek', OrderedDict([
        ('KodFormularza', {
            'static_value': 'JPK_VAT',
            'attrs': {
                'kodSystemowy': 'JPK_V7K (1)',
                'wersjaSchemy': '1-2E',
            }
        }),
        ('WariantFormularza', {'static_value': '1'}),
        ('DataWytworzeniaJPK', {'function': 'get_creation_date'}),
        ('NazwaSystemu', {'static_value': 'Odoo'}),
        ('CelZlozenia', {
            'wizard': 'correction_number',
            'attrs': {'poz': 'P_7'}
        }),
        ('KodUrzedu', {'wizard': ['company_id', 'tax_office', 'us_code']}),
        ('Rok', {'value': ['company_data', 'year']}),
        ('Miesiac', {'value': ['company_data', 'month']}),
    ])),
    ('Podmiot1', OrderedDict([
        ('attrs', {'rola': 'Podatnik'}),
        ('OsobaFizyczna', OrderedDict([
            ('etd:NIP', {'value': ['company_data', 'numeric_vat']}),
            ('etd:ImiePierwsze', {'value': ['company_data', 'first_name']}),
            ('etd:Nazwisko', {'value': ['company_data', 'surname']}),
            ('etd:DataUrodzenia', {'value': ['company_data', 'birth_date']}),
            ('Email', {'value': ['company_data', 'email']}),
        ])),
        ('OsobaNiefizyczna', OrderedDict([
            ('NIP', {'value': ['company_data', 'numeric_vat']}),
            ('PelnaNazwa', {'value': ['company_data', 'name']}),
            ('Email', {'value': ['company_data', 'email']}),
        ])),
    ])),
    ('Deklaracja', OrderedDict([
            ('Naglowek', OrderedDict([
                ('KodFormularzaDekl', {
                    'static_value': 'VAT-7K',
                    'attrs': {
                        'kodSystemowy': 'VAT-7K (15)',
                        'kodPodatku': 'VAT',
                        'rodzajZobowiazania': 'Z',
                        'wersjaSchemy': '1-2E',
                    }}),
                ('WariantFormularzaDekl', {'static_value': '15'}),
                ('Kwartal', {'value': ['company_data', 'quarter']}),
                ])),
            ('PozycjeSzczegolowe', {
                'POZYCJESZCZEGOLOWE': {
                    'value_loop': ['taxes_sum_dict'],
                    'force_int': True,
                    'no_order': True
                }
            }),
            ('Pouczenia', {'static_value': '1'}),
        ])),
    ('Ewidencja', OrderedDict([
        ('SPRZEDAZWIERSZ', {
            'iterator': 'sale_dict',
            'loop': {
                'SprzedazWiersz': OrderedDict([
                    ('LpSprzedazy', {'value': 'loop_index'}),
                    ('KodKrajuNadaniaTIN', {'value': ['sale_dict', 'loop_key', 'partner_data', 'country_code']}),
                    ('NrKontrahenta', {'value': ['sale_dict', 'loop_key', 'partner_data', 'numeric_vat']}),
                    ('NazwaKontrahenta', {'value': ['sale_dict', 'loop_key', 'partner_data', 'name']}),
                    ('DowodSprzedazy', {'value': ['sale_dict', 'loop_key', 'main_reference']}),
                    ('DataWystawienia', {'value': ['sale_dict', 'loop_key', 'date_issue']}),
                    ('DataSprzedazy', {'value': ['sale_dict', 'loop_key', 'sale_date']}),
                    ('TypDokumentu', {'value': ['sale_dict', 'loop_key', 'doc_type_vdek']}),
                    ('ZNACZNIKI', {'value_loop': ['sale_dict', 'loop_key', 'product_tax_markers'], 'force_int': True, 'no_order': True }),
                    ('ZNACZNIKI_PROCEDUR', {'value_loop': ['sale_dict', 'loop_key', 'procedures_markers'], 'force_int': True, 'no_order': True}),
                    ('PODATKI', {'value_loop': ['sale_dict', 'loop_key', 'tax_values']}),

                ])
            }
        }),
        ('SprzedazCtrl', OrderedDict([
            ('skip_empty', ['sale_ctrl']),
            ('LiczbaWierszySprzedazy', {'value': ['sale_ctrl', 'lp']}),
            ('PodatekNalezny', {'value': ['sale_ctrl', 'sum_taxes']}),
        ])),
        ('ZAKUPWIERSZ', {
            'iterator': 'purchase_dict',
            'loop': {
                'ZakupWiersz': OrderedDict([
                    ('LpZakupu', {'value': 'loop_index'}),
                    ('KodKrajuNadaniaTIN', {'value': ['purchase_dict', 'loop_key', 'country_code']}),
                    ('NrDostawcy', {'value': ['purchase_dict', 'loop_key', 'numeric_vat']}),
                    ('NazwaDostawcy', {'value': ['purchase_dict', 'loop_key', 'partner_name']}),
                    ('DowodZakupu', {'value': ['purchase_dict', 'loop_key', 'main_reference']}),
                    ('DataZakupu', {'value': ['purchase_dict', 'loop_key', 'purchase_date']}),
                    ('DataWplywu', {'value': ['purchase_dict', 'loop_key', 'date_recived']}),
                    ('DokumentZakupu', {'value': ['purchase_dict', 'loop_key', 'purchase_doc_vdek']}),
                    ('ZNACZNIKI_PROCEDUR', {'value_loop': ['purchase_dict', 'loop_key', 'procedures_markers'], 'force_int': True, 'no_order': True}),
                    ('PODATKI', {'value_loop': ['purchase_dict', 'loop_key', 'tax_values']}),
                ]),
            }
        }),
        ('ZakupCtrl', OrderedDict([
            ('skip_empty', ['purchase_ctrl']),
            ('LiczbaWierszyZakupow', {'value': ['purchase_ctrl', 'lp']}),
            ('PodatekNaliczony', {'value': ['purchase_ctrl', 'sum_taxes']})
        ]))
        ]))
        ,
])),
])
