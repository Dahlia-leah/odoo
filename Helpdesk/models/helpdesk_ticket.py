from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # Define the team members field as a many2many relation to the hr.employee model
    member_ids = fields.Many2many(
        'hr.employee', 
        string='Team Members', 
        domain=[('is_active', '=', True)],  # Only active employees can be part of the team
    )

    # Override the assigned user field to restrict to team members
    assigned_employee_id = fields.Many2one(
        'hr.employee', 
        string='Assigned Team Member',
        domain="[('id', 'in', member_ids)]",  # Limit assignment to team members only
        track_visibility='onchange',
    )


