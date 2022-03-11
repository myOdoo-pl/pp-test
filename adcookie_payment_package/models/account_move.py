from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    package_generated = fields.Boolean(string='Payment Package Generated', readonly=True, default=False)

    def set_package_generated(self):
        self.package_generated = True

    def get_bank_account(self):
        account = self.env['account.journal'].search(
            [('type', '=', 'bank'), ('company_id', '=', self.company_id.id), ('bank_account_id', '!=', '')])

        return account.bank_account_id
