from odoo import models, fields

class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _description = 'Helpdesk Team'

    name = fields.Char(string='Team Name', required=True)
    member_ids = fields.Many2many('res.users', string='Team Members')

