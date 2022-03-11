from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    package_generated = fields.Boolean(string='Payment Package Generated', readonly=True, default=False)

    def set_package_generated(self):
        self.package_generated = True

