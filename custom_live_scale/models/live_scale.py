import requests
from odoo import models, fields, api

class LiveScale(models.Model):
    _name = 'live.scale'
    _description = 'Live Scale Data'

    weight = fields.Float(string='Weight')
    unit = fields.Char(string='Unit')

    @api.model
    def fetch_scale_data(self):
        """Fetch live data from the scale API"""
        try:
            # Adjust the Flask API URL (assuming Flask API is running on localhost:5000)
            api_url = 'http://localhost:5000/get_weight'
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                self.weight = data.get('weight', 0.0)
                self.unit = data.get('unit', 'kg')
            else:
                self.weight = 0.0
                self.unit = 'kg'
        except requests.exceptions.RequestException as e:
            # Handle connection errors
            self.weight = 0.0
            self.unit = 'kg'
            _logger.error(f"Error fetching scale data: {e}")

        return True
