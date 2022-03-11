from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.depends('unit_amount', 'hour_unit_price')
    def _compute_timesheet_value(self):
        """Compute total value of timesheet."""
        for timesheet in self:
            timesheet.timesheet_value = timesheet.unit_amount * timesheet.hour_unit_price

    hour_unit_price = fields.Float(string='Hour Value', related='so_line.price_unit', help='Price for single hour.')
    timesheet_value = fields.Monetary(string='Timesheet Value', compute='_compute_timesheet_value', store=True,
                                      help='Timesheet value based on worked hours.')
    hr_report_id = fields.Many2one('hr_extended_report', string='HR Report', help='Connected HR report.')
