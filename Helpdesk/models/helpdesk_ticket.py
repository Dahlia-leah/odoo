from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    assigned_employee_id = fields.Many2one(
        'hr.employee',
        string="Assigned Employee",
        domain="[('id', 'in', member_ids)]",
        help="Only members of the Helpdesk Team can be assigned."
    )

    member_ids = fields.Many2many(
        'hr.employee',
        related='team_id.member_ids',
        string="Team Members",
        readonly=True
    )
