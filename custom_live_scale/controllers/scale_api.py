from odoo import http
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)

class ScaleIntegrationController(http.Controller):
    @http.route('/get_live_weight', type='json', auth='public', methods=['GET'], csrf=False)
    def fetch_live_weight(self):
        """
        Calls the Flask API to get live weight data.
        """
        flask_api_url = "http://127.0.0.1:5000/read_weight"  # Flask API endpoint

        try:
            # Make a request to the local Flask API
            response = requests.get(flask_api_url, timeout=3)
            if response.status_code == 200:
                scale_data = response.json()
                _logger.info(f"Scale data: {scale_data}")
                return scale_data
            else:
                _logger.error(f"Failed to fetch data: {response.status_code}")
                return {"error": "Unable to fetch scale data"}
        except Exception as e:
            _logger.error(f"Error connecting to scale API: {e}")
            return {"error": "Connection failed"}
