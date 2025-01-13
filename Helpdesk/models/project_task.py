from odoo import fields, models

class ProjectTask(models.Model):
    _inherit = "project.task"

    helpdesk_ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string="Related Helpdesk Ticket",
        help="The ticket associated with this task."
    )
