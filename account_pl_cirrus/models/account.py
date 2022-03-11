# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from pprint import pprint
import logging
import re

_logger = logging.getLogger(__name__)




class TaxTagPl(models.Model):
    _name = 'tax.tag.pl'


    name = fields.Char(string='Tag Name', required=True)

    @api.model
    def _set_tags_from_name(self):
        tax_tag_pl = self.env['tax.tag.pl']
        accounts = self.env['account.tax'].search([])
        for account in accounts:
            find_tag = re.findall(r"({.*?})", account.name)
            if find_tag:
                tag = find_tag[0][1:-1]
                _logger.warning('Create tax tag: '+str(tag))
                new_tag = tax_tag_pl.create({'name' : tag})
                account.write({'tag_id': new_tag.id})


class AccountTax(models.Model):
    _inherit = 'account.tax'


    tag_id = fields.Many2one('tax.tag.pl', string='Tax tag')
