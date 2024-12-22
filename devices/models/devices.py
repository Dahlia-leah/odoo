from odoo import models, fields

class Device(models.Model):
    _name = 'my.devices'
    _description = 'Device Model'

    name = fields.Char('Device Name', required=True)
    type = fields.Char('Device Type')
    brand = fields.Char('Brand')
    description = fields.Text('Description')
