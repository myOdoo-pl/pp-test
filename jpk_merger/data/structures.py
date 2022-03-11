from collections import OrderedDict

JPK_FA_BILLS = OrderedDict([
    ('JPK', OrderedDict([
        ('attrs', {
            'xmlns': "http://jpk.mf.gov.pl/wzor/2019/09/27/09271/",
            'xmlns:dt': 'http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2018/08/24/eD/DefinicjeTypy/',
        }),
        ('Naglowek', OrderedDict([
            ('KodFormularza', {
                'static_value': 'JPK_FA BILLS',
                'attrs': {
                    'kodSystemowy': 'JPK_FA BILLS',
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

        # TODO: MODYFIKACJA
        ('Faktura', {
            'iterator': 'purchase_dict',
            'loop': {
                'Faktura': OrderedDict([
                    ('KodWaluty', {'wizard': ['company_id', 'currency_id', 'name']}),
                    ('P_1', {'value': ['purchase_dict', 'loop_key', 'date_issue']}),
                    ('P_2A', {'value': ['purchase_dict', 'loop_key', 'main_reference']}),
                    ('P_3A', {'value': ['purchase_dict', 'loop_key', 'purchaser_data', 'name']}),
                    ('P_3B', {'value': ['purchase_dict', 'loop_key', 'purchaser_data', 'address']}),
                    ('P_3C', {'value': ['purchase_dict', 'loop_key', 'seller_data', 'name']}),
                    ('P_3D', {'value': ['purchase_dict', 'loop_key', 'seller_data', 'address']}),
                    ('P_4A', {'value': ['purchase_dict', 'loop_key', 'seller_data', 'country_code']}),
                    ('P_4B', {'value': ['purchase_dict', 'loop_key', 'seller_data', 'numeric_vat']}),
                    ('P_5A', {'value': ['purchase_dict', 'loop_key', 'purchaser_data', 'country_code']}),
                    ('P_5B', {'value': ['purchase_dict', 'loop_key', 'purchaser_data', 'numeric_vat']}),
                    ('P_6', {'value': ['purchase_dict', 'loop_key', 'date_invoice']}),
                    ('P_13_1', {'value': ['purchase_dict', 'loop_key', 'tax_values', 'K_19']}),
                    ('P_14_1', {'value': ['purchase_dict', 'loop_key', 'tax_values', 'K_20']}),
                    ('P_13_2', {'value': ['purchase_dict', 'loop_key', 'tax_values', 'K_17']}),
                    ('P_14_2', {'value': ['purchase_dict', 'loop_key', 'tax_values', 'K_18']}),
                    ('P_13_3', {'value': ['purchase_dict', 'loop_key', 'tax_values', 'K_15']}),
                    ('P_14_3', {'value': ['purchase_dict', 'loop_key', 'tax_values', 'K_16']}),
                    ('P_13_6', {'value': ['purchase_dict', 'loop_key', 'tax_values', 'K_13']}),
                    ('P_13_7', {'value': ['purchase_dict', 'loop_key', 'tax_values', 'K_10']}),
                    ('P_15', {'value': ['purchase_dict', 'loop_key', 'amount_total']}),
                    ('P_16', {'value': ['purchase_dict', 'loop_key', 'cash_basis']}),
                    ('P_17', {'static_value': 'false'}),
                    ('P_18', {'value': ['purchase_dict', 'loop_key', 'reverse_charge']}),
                    ('P_18A', {'static_value': 'false'}),
                    ('P_19', {'static_value': 'false'}),
                    ('P_20', {'static_value': 'false'}),
                    ('P_21', {'static_value': 'false'}),
                    ('P_22', {'static_value': 'false'}),
                    ('P_23', {'static_value': 'false'}),
                    ('P_106E_2', {'static_value': 'false'}),
                    ('P_106E_3', {'static_value': 'false'}),
                    ('RodzajFaktury', {'value': ['purchase_dict', 'loop_key', 'invoice_type']}),
                    ('PrzyczynaKorekty', {'value': ['purchase_dict', 'loop_key', 'refund_reason']}),
                    ('NrFaKorygowanej', {'value': ['purchase_dict', 'loop_key', 'refunded_inv_number']}),
                    ('OkresFaKorygowanej', {'value': ['purchase_dict', 'loop_key', 'refunded_period']}),
                ])
            }
        }),
        ('FakturaCtrl', OrderedDict([
            ('LiczbaFaktur', {'value': ['purchase_dict', 'po_lp']}),
            ('WartoscFaktur', {'value': ['purchase_dict', 'po_sum_all']}),
        ])),
        ('FakturaWiersz', {
            'iterator': 'purchase_invoice_lines',
            'loop': {
                'FakturaWiersz': OrderedDict([
                    ('P_2B', {'value': ['purchase_invoice_lines', 'loop_key', 'invoice_reference']}),
                    ('P_7', {'value': ['purchase_invoice_lines', 'loop_key', 'name']}),
                    ('P_8A', {'value': ['purchase_invoice_lines', 'loop_key', 'uom']}),
                    ('P_8B', {'value': ['purchase_invoice_lines', 'loop_key', 'qty']}),
                    ('P_9A', {'value': ['purchase_invoice_lines', 'loop_key', 'price_unit']}),
                    ('P_9B', {'value': ['purchase_invoice_lines', 'loop_key', 'unit_gross']}),
                    ('P_10', {'value': ['purchase_invoice_lines', 'loop_key', 'discount']}),
                    ('P_11', {'value': ['purchase_invoice_lines', 'loop_key', 'subtotal']}),
                    ('P_11A', {'value': ['purchase_invoice_lines', 'loop_key', 'gross']}),
                    ('P_12', {'value': ['purchase_invoice_lines', 'loop_key', 'tax_group']}),
                ])
            }
        }),
        ('FakturaWierszCtrl', OrderedDict([
            ('LiczbaWierszyFaktur', {'value': ['purchase_invoice_line_ctrl', 'po_lp']}),
            ('WartoscWierszyFaktur', {'value': ['purchase_invoice_line_ctrl', 'po_sum_invoice_line']}),
        ])),
        # TODO: KONIEC MODYFIKACJI

        ('Zamowienie', {
            'iterator': 'purchase_order_downpayment',
            'loop': {
                'Zamowienie': OrderedDict([
                    ('P_2AZ', {'value': ['purchase_order_downpayment', 'loop_key', 'main_reference']}),
                    ('WartoscZamowienia', {'value': ['purchase_order_downpayment', 'loop_key', 'order_total']}),
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
            ('LiczbaZamowien', {'value': ['purchase_order_ctrl', 'lp']}),
            ('WartoscZamowien', {'value': ['purchase_order_ctrl', 'purchase_order_sum']}),
        ]))
    ])),
])
