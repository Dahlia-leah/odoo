import requests
from odoo import models, fields, api

class LiveScale(models.Model):
    _name = 'live.scale'
    _description = 'Live Scale Weight'

    weight = fields.Float(string="Weight", readonly=True)
    unit = fields.Char(string="Unit", readonly=True)

    @api.model
    def fetch_live_weight(self):
        """
        Fetch live weight from the API.
        Replace 'http://api.example.com' with your actual API endpoint.
        """
        try:
            url = "http://api.example.com/get_weight"  # Replace with your API
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            weight = data.get('weight', 0.0)
            unit = data.get('unit', 'kg')

            return {'weight': weight, 'unit': unit}

        except Exception as e:
            return {'weight': 0.0, 'unit': 'error'}
