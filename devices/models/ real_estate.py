# real_estate/models/real_estate.py
from odoo import models, fields

class RealEstateProperty(models.Model):
    _name = 'real.estate.property'
    _description = 'Real Estate Property'

    name = fields.Char(string='Title', required=True)
    description = fields.Text()
    offer_ids = fields.One2many('real.estate.offer', 'property_id', string='Offers')
    other_info = fields.Text(string='Other Info')