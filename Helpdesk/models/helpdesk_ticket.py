from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    member_ids = fields.Many2many(
        'hr.employee',
        string="Team Members",
        related='team_id.member_ids',
        readonly=True,
        store=True,
        help="Team Members assigned to this Helpdesk Team.",
    )

    assigned_user_id = fields.Many2one(
        'hr.employee',
        string="Assigned To",
        domain="[('id', 'in', member_ids)]",
        help="Only employees who are part of the Helpdesk Team can be assigned."
    )

    
class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    member_ids = fields.Many2many(
        'hr.employee',
        string="Team Members",
        help="Employees who are part of this Helpdesk Team."
    )
