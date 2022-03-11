# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class AccountFiscalPosition(models.Model):
    _inherit='account.fiscal.position'

    default_journal_id = fields.Many2one('account.journal', 'Default Journal')

class AccountMove(models.Model):
    _inherit='account.move'

    def _get_default_journal(self):
        journal_id = super(AccountMove, self)._get_default_journal()
        if self.fiscal_position_id and self.fiscal_position_id.default_journal_id:
            journal_id = self.fiscal_position_id.default_journal_id
        return journal_id

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        check_company=True, domain=False,
        default=_get_default_journal)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position', readonly=True, states={'draft': [('readonly', False)]})


    @api.onchange('fiscal_position_id')
    def onchange_fiscal_position(self):
        journal_id = self.journal_id
        if self.fiscal_position_id and self.fiscal_position_id.default_journal_id:
            journal_id = self.fiscal_position_id.default_journal_id
        else:
            journal_id = self._get_default_journal()
        self.journal_id = journal_id


    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        if move.fiscal_position_id and move.fiscal_position_id.default_journal_id:
            move.journal_id = move.fiscal_position_id.default_journal_id
        return move
