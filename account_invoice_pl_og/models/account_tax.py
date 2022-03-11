from odoo import fields, models, api, _
import logging
from copy import deepcopy
from pprint import pprint
_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit='account.tax'



    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, is_refund=False, handle_price_include=True):
        res = super(AccountTax, self).compute_all(price_unit, currency, quantity, product, partner, is_refund, handle_price_include)
        for rec in self:
            if rec.amount_type == 'group':
                tax_perc = sum(rec.children_tax_ids.mapped('amount'))
                total_excluded = res.get('total_excluded')
                total_included = res.get('total_included')
                total_right = total_excluded + (total_excluded*(tax_perc/100))
                if total_right != total_included:
                    diff = round(total_included - total_right,2)
                    if diff > 0:
                        factor = -0.01
                    else:
                        factor = 0.01
                    res['total_included'] = total_right
                    for tax in res['taxes']:
                        tax['amount'] = tax['amount'] + factor
                        diff += factor
                        if diff == 0.0:
                            break
        pprint(res)
        return res
