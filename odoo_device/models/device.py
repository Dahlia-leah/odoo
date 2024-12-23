from odoo import models, fields

class Device(models.Model):
    _name = 'device'
    _description = 'Device'

    name = fields.Char(string='Device Name', required=True)
    device_type = fields.Selection([
        ('mobile', 'Mobile'),
        ('laptop', 'Laptop'),
        ('tablet', 'Tablet'),
        ('other', 'Other'),
    ], string='Device Type', default='other')
    serial_number = fields.Char(string='Serial Number')
    purchase_date = fields.Date(string='Purchase Date')
    warranty_expiry = fields.Date(string='Warranty Expiry')
