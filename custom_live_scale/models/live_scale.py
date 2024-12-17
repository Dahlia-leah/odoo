from odoo import models, fields

class LiveScale(models.Model):
    _name = 'live.scale'
    _description = 'Live Scale Data'

    weight = fields.Float(string='Weight')
    unit = fields.Char(string='Unit')
