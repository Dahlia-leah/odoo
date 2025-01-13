from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Related Helpdesk Ticket')

