from odoo import models, fields

class Devices(models.Model):
    _name = 'devices'
    _description = 'Devices'

    name = fields.Char(string='Device Name', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    is_available = fields.Boolean(string='Is Available', default=True)