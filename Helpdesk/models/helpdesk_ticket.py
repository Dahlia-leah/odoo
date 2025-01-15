from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    assigned_user_id = fields.Many2one(
        'res.users',
        string="Assigned To",
        domain="[('id', 'in', member_ids)]",
        help="Only members of the Helpdesk Team can be assigned."
    )

    member_ids = fields.Many2many(
        related='team_id.member_ids',
        domain="[('id', 'in', employee_id)]",
        string="Team Members",
        readonly=True
    )