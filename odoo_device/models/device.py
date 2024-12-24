from odoo import models, fields

class Device(models.Model):
    _name = 'x.device'
    _description = 'Device'

    name = fields.Char(string="Device Name", required=True)

class DeviceConnection(models.Model):
    _name = 'x.device.connection'
    _description = 'Device Connection'

    device_id = fields.Many2one('x.device', string="Device", required=True)
    url = fields.Char(string="URL to Fetch JSON From", required=True)
