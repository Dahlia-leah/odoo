from odoo import models, fields

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    member_ids = fields.Many2many(
        'hr.employee', 
        'helpdesk_team_employee_rel', 
        'team_id', 
        'employee_id', 
        string="Team Members"
    )

    employee_member_ids = fields.Many2many(
        'hr.employee', 
        'helpdesk_team_employee_rel', 
        'team_id', 
        'employee_id', 
        string="Employees"
    )
