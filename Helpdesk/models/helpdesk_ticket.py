from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    assigned_user_id = fields.Many2one(
          'hr.employee',
        string="Assigned Employee",
        domain="[('id', 'in', member_ids.ids)]",
        help="Only team members can be assigned."
    )

    member_ids = fields.Many2many(
        'hr.employee',
        related='team_id.member_ids',
        string="Team Members",
        readonly=True
    )

    @api.depends('team_id')
    def _compute_team_members(self):
        for ticket in self:
            if ticket.team_id:
                analytic_lines = self.env['account.analytic.line'].search([('employee_id', '!=', False)])
                employee_ids = analytic_lines.mapped('employee_id.id')
                ticket.member_ids = [(6, 0, employee_ids)]
            else:
                ticket.member_ids = [(5,)]  # Clear the field if no team is set
