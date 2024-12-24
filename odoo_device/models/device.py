from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class XDeviceConnection(models.Model):
    _name = 'x.device.connection'
    _description = 'Device Connection'

    device_id = fields.Many2one('x.device', string='Device', required=True)
    url = fields.Char(string="URL to Fetch JSON From", required=True)

    def action_submit_url(self):
        for connection in self:
            if not connection.url:
                raise UserError("The URL cannot be empty.")
            
            data = self._fetch_json_data(connection.url)
            if data is False:
                raise UserError("The URL is invalid or the request failed.")
            elif data is None:
                raise UserError("The URL does not return valid JSON.")
            else:
                _logger.info(f"Connection to device {connection.device_id.name} established successfully.")

    def _fetch_json_data(self, url):
        """Shared method to fetch JSON data from the given URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except ValueError:
            _logger.error(f"Invalid JSON response from {url}")
            return None
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error while requesting {url}: {e}")
            return False
        
from odoo import models, fields

class XDevice(models.Model):
    _name = 'x.device'
    _description = 'Device'

    name = fields.Char(string='Device Name', required=True)
