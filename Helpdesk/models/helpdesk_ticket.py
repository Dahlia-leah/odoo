from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    assigned_user_id = fields.Many2one(
        'res.users',
        string="Assigned Employee",
        domain="[('id', 'in', member_ids)]",
        help="Only team members can be assigned."
    )

    member_ids = fields.Many2many(
        'hr.employee',
        compute="_compute_team_members",
        string="Team Members",
        store=False,
    )

    @api.depends('team_id')
    def _compute_team_members(self):
        for ticket in self:
            if ticket.team_id:
                # Fetch employees from account.analytic.line regardless of user association
                analytic_lines = self.env['account.analytic.line'].search([])
                employee_ids = analytic_lines.mapped('employee_id.id')
                ticket.member_ids = [(6, 0, employee_ids)]
            else:
                ticket.member_ids = [(5,)]  # Clear if no team is set

    def _domain_assigned_user_id(self):
        # Dynamically generate a domain for the assigned_user_id field
        analytic_lines = self.env['account.analytic.line'].search([])
        employee_ids = analytic_lines.mapped('employee_id.id')
        return [('id', 'in', employee_ids)]
