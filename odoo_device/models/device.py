from odoo import models, fields

class Device(models.Model):
    _name = 'devices.device'
    _description = 'Device'

    name = fields.Char(string='Device Name', required=True)
    device_id = fields.Char(string='Device ID', required=True, unique=True)
