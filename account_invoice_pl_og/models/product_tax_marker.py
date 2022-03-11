from odoo import fields, models, api, _
import logging
_logger = logging.getLogger(__name__)


class ProductTaxMarker(models.Model):
    _name = 'product.tax.marker'

    name = fields.Char('Kod podatku')
    description = fields.Char('Opis')
