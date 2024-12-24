from odoo import models, fields


class DeviceParameter(models.Model):
    _name = 'device.parameter'
    _description = 'Device Parameter'

    device_id = fields.Many2one('device', string='Device', required=True, ondelete='cascade')
    parameter_name = fields.Char(string='Parameter Name', required=True)
    parameter_value = fields.Char(string='Parameter Value')
