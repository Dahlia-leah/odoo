from odoo import models, fields, api, exceptions

class Device(models.Model):
    _name = 'devices.device'
    _description = 'Device'

    name = fields.Char(string='Device Name', required=True, default='Scale')
    device_id = fields.Char(string='Device ID', required=True, default='1', unique=True)

    @api.model
    def create(self, vals):
        raise exceptions.UserError("You cannot create new Device records.")

    def unlink(self):
        raise exceptions.UserError("You cannot delete Device records.")
