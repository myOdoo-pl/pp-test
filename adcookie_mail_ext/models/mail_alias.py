from odoo import _, api, fields, models


class Alias(models.Model):
    _inherit = 'mail.alias'

    @api.model
    def create(self, vals):
        """ Creates an email.alias record according to the values provided in ``vals``,
            with 2 alterations: the ``alias_name`` value may be cleaned  by replacing
            certain unsafe characters, and the ``alias_model_id`` value will set to the
            model ID of the ``model_name`` context value, if provided. Also, it raises
            UserError if given alias name is already assigned.
        """
        if vals.get('alias_name'):
            input_alias_name = self._clean_and_check_unique(vals.get('alias_name'))
            vals['alias_name'] = input_alias_name + "-01"
        return super(Alias, self).create(vals)

    def write(self, vals):
        """"Raises UserError if given alias name is already assigned"""
        if vals.get('alias_name') and self.ids:
            input_alias_name = self._clean_and_check_unique(vals.get('alias_name'))
            vals['alias_name'] = input_alias_name + "-01"
        return super(Alias, self).write(vals)
