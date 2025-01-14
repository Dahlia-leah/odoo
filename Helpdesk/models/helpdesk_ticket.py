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
        'hr.employee',  # Reference to the Employee model
        'helpdesk_ticket_employee_rel',  # Name of the relationship table
        'ticket_id',  # Column in the relationship table for this model
        'employee_id',  # Column in the relationship table for the related model
        string="Team Members",
        domain=[('active', '=', True)],  # Optional: Only show active employees
        store=True,  # Store the relationship in the database
    )
