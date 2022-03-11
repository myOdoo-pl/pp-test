from odoo import api, fields, models
import logging

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    custom_name = fields.Char(name="Custom name", required=True, default="Custom name")
    so_name = fields.Char(name="SO name")  # Field to store sale's order name before overriding with custom name.

    @api.model
    def create(self, vals):
        # This method sets so_name with default name value, overrides name if custom_name is provided.
        res = super(SaleOrder, self).create(vals)
        res.so_name = vals['name']
        if vals['custom_name']:
            if not (vals['custom_name'] == 'Custom name'):
                res.name = f"{res.so_name} - {vals['custom_name']}"
        return res

    def write(self, vals):
        # This method overrides sales.order name, related projects names and analytic account's name.
        if not self.so_name:  # Already created orders case.
            name = f"S{self.id:05d}"  # Sets so_name to default order's name: S00000
            vals['so_name'] = name
        else:
            name = self.so_name
        if "custom_name" in vals.keys():
            if vals['custom_name']:
                """
                Add custom name to so_name instead of name to avoid recurrence in name.
                Example of recurrence:
                1 edit. name = name + custom_name
                2 edit. name = (name + custom_name) + custom_name etc.  
                """
                vals['name'] = f"{name} - {vals['custom_name']}"
            else:
                vals['name'] = name

            if self.project_ids:
                self.project_ids.name = vals['name']
                if self.project_ids.analytic_account_id:
                    self.project_ids.analytic_account_id.name = vals['name']
        res = super(SaleOrder, self).write(vals)
        return res
