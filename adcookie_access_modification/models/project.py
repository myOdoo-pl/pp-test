from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = "project.project"

    # # Set analytic account created from project as non-sensitive by default
    # @api.model
    # def _create_analytic_account_from_values(self, values):
    #     analytic_account = self.env['account.analytic.account'].create({
    #         'name': values.get('name', _('Unknown Analytic Account')),
    #         'company_id': values.get('company_id') or self.env.company.id,
    #         'partner_id': values.get('partner_id'),
    #         'active': True,
    #         'sensitive_data': False,
    #     })
    #     return analytic_account
    #
    # # Set analytic account created from project as non-sensitive by default
    # def _create_analytic_account(self):
    #     for project in self:
    #         analytic_account = self.env['account.analytic.account'].create({
    #             'name': project.name,
    #             'company_id': project.company_id.id,
    #             'partner_id': project.partner_id.id,
    #             'active': True,
    #             'sensitive_data': False,
    #         })
    #         project.write({'analytic_account_id': analytic_account.id})
