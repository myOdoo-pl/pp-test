from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)


class MultiModifier(models.TransientModel):
    _name = 'account.sensitive_data_modifier.wizard'

    move_ids = fields.Many2many('account.move')
    changed = {}

    @api.model
    def default_get(self, fields_list):
        values = super(MultiModifier, self).default_get(fields_list)
        active_move_ids = self.env['account.move'].browse(
            self.env.context.get('active_ids', []))  # Get selected records
        values['move_ids'] = [(6, 0, active_move_ids.ids)]
        return values

    def save(self):
        for move_id in self.move_ids:
            move_id.write({
                "sensitive_data": move_id.selected_in_wizard,
            })

    def switch_all(self, state):
        for move_id in self.move_ids:
            move_id.write({
                "selected_in_wizard": state,
            })
        return {
            'name': 'Sensitive Data Modifier',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def mark_all(self):
        return self.switch_all(True)

    def unmark_all(self):
        return self.switch_all(False)
