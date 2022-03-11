from odoo import api, fields, models

from datetime import date


class HrExtendedReport(models.Model):
    _name = 'hr_extended_report'
    _description = 'HR Extended Report'

    @api.depends('group', 'month', 'year', 'employee_id', 'department_id', 'overhead')
    def _get_timesheet_recordset(self):
        """Compute method for collecting all timesheets for report."""
        # Create temporary timesheet list and iterate through every model record.
        timesheet_list = list()
        for record in self:
            record.total = 0

            if record.group == 'employee':
                timesheet_ids = self.env['account.analytic.line'].search([('employee_id', '=', record.employee_id.id)])

                # Add all timesheets within selected date to temporary list.
                for timesheet in timesheet_ids:
                    if timesheet.date.month == int(record.month) and timesheet.date.year == record.year:
                        timesheet_list.append(timesheet.id)
                        record.total += timesheet.timesheet_value

                # Get monthly wage of employee from his contract, and subtract it from total timesheets value.
                contract_id = self.env['hr.contract'].search([('employee_id', '=', record.employee_id.id)])
                record.total -= contract_id.wage

                # Subtract overhead from total value, if checked.
                if record.overhead:
                    record.total -= contract_id.overhead

            elif record.group == 'department':
                employee_ids = self.env['hr.employee'].search([('department_id', '=', record.department_id.id)])

                # Get every timesheet of every employee in department.
                for employee in employee_ids:
                    timesheet_ids = self.env['account.analytic.line'].search([('employee_id', '=', employee.id)])

                    for timesheet in timesheet_ids:
                        if timesheet.date.month == int(record.month) and timesheet.date.year == record.year:
                            timesheet_list.append(timesheet.id)
                            record.total += timesheet.timesheet_value

                    contract_id = self.env['hr.contract'].search([('employee_id', '=', employee.id)])
                    record.total -= contract_id.wage

                    # Subtract overhead from total value, if checked.
                    if record.overhead:
                        record.total -= contract_id.overhead

            # Return timesheets.
            record.timesheet_ids = [(6, 0, timesheet_list)]

    name = fields.Char(string='Name', required='True', help='Name of this report record.')
    group = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department')
    ], string='Group By', default='employee', required=True, help='Select grouping for created report.')
    month = fields.Selection([
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'),
    ], string='Month', default='1', required=True, help='Select month of timesheets for report.')
    year = fields.Integer(string='Year', required=True, default=lambda x: date.today().year,
                          help='Select year of timesheets for report.')
    employee_id = fields.Many2one('hr.employee', string='Employee', help='Select employee for report.')
    department_id = fields.Many2one('hr.department', string='Department', help='Select department for report.')
    overhead = fields.Boolean(string='Overhead', default=False,
                              help='Checkbox for determine if overhead should be included.')
    comment = fields.Text(string='Comments', help='Comment field for additional information regarding this collection.')
    timesheet_ids = fields.One2many('account.analytic.line', 'hr_report_id', string='Timesheets',
                                    compute='_get_timesheet_recordset', help='Collected timesheets for this report.')
    total = fields.Float(string='Total Value', readonly=True, help='Total value of collected timesheets.')
