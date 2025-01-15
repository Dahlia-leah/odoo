from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # Define the team members field as a many2many relation to the hr.employee model
    team_member_ids = fields.Many2many(
        'hr.employee', 
        string='Team Members', 
        domain=[('is_active', '=', True)],  # Only active employees can be part of the team
    )

    # Override the assigned user field to restrict to team members
    assigned_employee_id = fields.Many2one(
        'hr.employee', 
        string='Assigned Team Member',
        domain="[('id', 'in', team_member_ids)]",  # Limit assignment to team members only
        track_visibility='onchange',
    )

    # Optionally, we can create a function to ensure that a task can only be assigned to a team member
    @api.constrains('assigned_employee_id')
    def _check_assigned_employee(self):
        for record in self:
            if record.assigned_employee_id not in record.team_member_ids:
                raise ValidationError("The assigned employee must be part of the team.")
