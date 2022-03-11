# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _

from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    cash_basis_pl = fields.Boolean("Cash Basis PL", related='company_id.cash_basis_pl')

class ResCompany(models.Model):
    _inherit='res.company'

    cash_basis_pl = fields.Boolean("Cash Basis PL")
