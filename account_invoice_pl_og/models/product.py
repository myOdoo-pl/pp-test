from odoo import models, fields


class product_template(models.Model):
    _inherit = 'product.template'

    pkwiu = fields.Char(
        'Nr PKWiU', size=32, help="This field is intended to hold products number according to polish Classification for Products and Services")
    tax_marker = fields.Many2one('product.tax.marker', string='Tax Marker')
    split_payment_method = fields.Boolean(default=False, help="Transakcja  objęta obowiązkiem stosowania mechanizmu podzielonej płatności.  Oznaczenie  MPP  należy  stosować  do  faktur  o  kwocie  brutto wyższej niż 15 000,00 zł, które dokumentują dostawę towarów lub świadczenie usług wymienionych w załączniku nr 15 do ustawy.")

    def get_tax_marker(self):
        for prod in self:
            if prod.tax_marker:
                return prod.tax_marker
            else:
                if prod.categ_id:
                    return prod.categ_id.tax_marker


class ProductCategory(models.Model):
    _inherit = "product.category"

    tax_marker = fields.Many2one('product.tax.marker', string='Tax Marker')
