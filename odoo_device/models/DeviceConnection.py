from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class DeviceConnection(models.Model):
    _name = 'device.connection'
    _description = 'Device Connection'

    device_id = fields.Many2one('device', string='Device', required=True)
    url = fields.Char(string="URL to Fetch JSON From", required=True)
    connection_status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
    ], string="Connection Status", default='disconnected')

    def action_submit_url(self):
        """Validate the URL and establish the connection."""
        for connection in self:
            if not connection.url:
                raise UserError("The URL cannot be empty.")
            
            # Validate the URL and fetch JSON data
            data = self._validate_json(connection.url)
            if data is False:
                raise UserError("The URL is invalid or the request failed.")
            elif data is None:
                raise UserError("The URL does not return valid JSON.")
            else:
                connection.connection_status = 'connected'
                # Optionally, process the data if needed
                _logger.info(f"Connection to device {connection.device_id.name} established successfully.")
    
    def _validate_json(self, url):
        """Validate and fetch JSON data from the URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Check if the response is valid
            return response.json()  # Return the parsed JSON
        except ValueError:
            _logger.error(f"Invalid JSON response from {url}")
            return None  # Invalid JSON
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error while requesting {url}: {e}")
            return False  # Request failed

