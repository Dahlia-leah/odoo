from odoo import http
from odoo.http import request
import requests

class ScaleAPIController(http.Controller):

    @http.route('/get_weight', type='json', auth='public', methods=['GET'])
    def get_weight(self, **kwargs):
        """
        Endpoint to fetch weight from the scale API.
        The scale API is running locally (http://localhost:5000/get_weight).
        """
        try:
            # Fetch the weight data from the external API
            response = requests.get("http://localhost:5000/get_weight", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'weight': data.get('weight', 0.0),
                    'unit': data.get('unit', 'kg'),
                }
            return {'error': 'Failed to fetch data from scale API'}
        except Exception as e:
            return {'error': f"Error: {str(e)}"}
