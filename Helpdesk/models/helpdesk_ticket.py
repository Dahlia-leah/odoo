from odoo import api, fields, models

class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _description = 'Helpdesk Team'

    member_ids = fields.Many2many(
        'hr.employee',
        string='Team Members',
        help='Employees that are members of this helpdesk team.'
    )
    
    