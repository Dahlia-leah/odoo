from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    assigned_user_id = fields.Many2one(
        'hr.employee',
        string="Assigned Employee",
        domain="[('id', 'in', member_ids)]",
        help="Only team members can be assigned."
    )

    member_ids = fields.Many2many(
        'hr.employee',
        string="Team Members",
        compute="_compute_team_members",
        store=False,  # This is computed dynamically, no need to store in DB
    )

    @api.depends('team_id')
    def _compute_team_members(self):
        for ticket in self:
            if ticket.team_id:
                # Fetch employees linked to the team (with or without users)
                analytic_lines = self.env['account.analytic.line'].search([])
                employee_ids = analytic_lines.mapped('employee_id.id')
                ticket.member_ids = [(6, 0, employee_ids)]
            else:
                ticket.member_ids = [(5,)]  # Clear field if no team is set
