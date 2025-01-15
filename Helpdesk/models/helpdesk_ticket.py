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
    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'

    team_id = fields.Many2one(
        'helpdesk.team',
        string='Helpdesk Team',
        help='The team responsible for this ticket.'
    )

    assigned_user_id = fields.Many2one(
        'hr.employee',
        string='Assigned Employee',
        domain="[('id', 'in', team_id.member_ids)]",
        help='Employee assigned to this ticket.'
    )