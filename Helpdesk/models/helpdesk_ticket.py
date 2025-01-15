from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'

    assigned_user_id = fields.Many2one(
        'res.users',
        string="Assigned To",
        domain="[('id', 'in', member_ids)]",
        help="Only members of the Helpdesk Team can be assigned."
    )

    team_id = fields.Many2one(
        'helpdesk.team',
        string='Helpdesk Team',
        help='The team responsible for this ticket.'
    )

    member_ids = fields.Many2many(
        related='team_id.member_ids',
        domain="[('id', 'in', employee_id)]",
        string="Team Members",
        readonly=True
    )

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