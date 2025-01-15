from odoo import api, fields, models

class HelpdeskSLA(models.Model):
    _name = 'helpdesk.sla'
    _description = 'Helpdesk SLA'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        help='The company this SLA applies to.'
    )

    stage_id = fields.Many2one(
        'helpdesk.stage',
        string='Stage',
        help='The stage this SLA applies to.'
    )

    # Other fields and methods for the HelpdeskSLA model