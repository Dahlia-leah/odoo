from odoo import api, fields, models

class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _description = 'Helpdesk Team'

    member_ids = fields.Many2many(
        'hr.employee',
        string='Team Members',
        help='Employees that are members of this helpdesk team.'
    )

    description = fields.Text(
        string='Description',
        help='Description of the helpdesk team.'
    )


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    assigned_user_id = fields.Many2one(
        'hr.employee',
        string="Assigned To",
        domain="[('id', 'in', team_id.member_ids.ids)]",
        help="Only members of the Helpdesk Team can be assigned."
    )

    member_ids = fields.Many2many(
        related='team_id.member_ids',
        string="Team Members",
        readonly=True
    )
