from odoo import api, fields, models
import logging

logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    custom_name = fields.Char(name="Custom name", required=True, default='Custom name')
    po_name = fields.Char(name="SO name")  # Field to store sale's order name before overriding with custom name.

    @api.model
    def create(self, vals):
        # This method sets po_name with default name value, overrides name if custom_name is provided.
        res = super(PurchaseOrder, self).create(vals)
        res.po_name = vals['name']
        if vals['custom_name']:
            if not (vals['custom_name'] == 'Custom name'):
                res.name = f"{res.po_name} - {vals['custom_name']}"
        return res

    def write(self, vals):
        # This method overrides sales.order name, related projects names and analytic account's name.
        if not self.po_name:  # Already created orders case.
            name = f"P{self.id:05d}"  # Sets po_name to default order's name: P00000
            vals['po_name'] = name
        else:
            name = self.po_name
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

        res = super(PurchaseOrder, self).write(vals)
        return res
