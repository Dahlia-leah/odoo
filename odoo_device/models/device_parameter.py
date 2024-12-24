from odoo import models, fields

class DeviceParameter(models.Model):
    _name = 'device.parameter'
    _description = 'Device Parameter'

    device_id = fields.Many2one('device', string='Device', required=True, ondelete='cascade')
    parameter_name = fields.Char(string='Parameter Name', required=True, size=128)
    parameter_value = fields.Char(string='Parameter Value', size=256)

    _sql_constraints = [
        ('device_parameter_unique', 
         'unique(device_id, parameter_name)', 
         'A device can only have one parameter with a specific name.')
    ]
