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


class Device(models.Model):
    _name = 'device'
    _description = 'Device'

    status = fields.Selection([
        ('active', 'Active'),
        ('out_of_service', 'Out of Service'),
        ('inactive', 'Inactive'),
    ], string='Status', default='inactive')

    json_data = fields.Text(string="JSON Data", readonly=True)
    url = fields.Char(string="URL to fetch JSON from", required=True)

    # One2many relationship to device parameters
    device_parameter_ids = fields.One2many(
        comodel_name='device.parameter',
        inverse_name='device_id',
        string='Device Parameters'
    )

    # One2many relationship to device connections
    device_connection_ids = fields.One2many(
        comodel_name='device.connection',
        inverse_name='device_id',
        string='Device Connections'
    )

    def validate_json(self, url):
        """Validate the JSON fetched from the provided URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raises an error for non-2xx responses
            return response.json()  # Return parsed JSON
        except ValueError:
            _logger.error(f"Invalid JSON response from {url}")
            return None  # Invalid JSON
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error while requesting {url}: {e}")
            return False  # Request failed

    def action_submit_url(self):
        """Fetch the JSON from the URL and process the device parameters."""
        if not self.url:
            raise UserError("The URL cannot be empty.")

        data = self.validate_json(self.url)

        if data is False:
            raise UserError("The URL is invalid or the request failed.")
        elif data is None:
            raise UserError("The URL does not return valid JSON.")
        else:
            self.json_data = json.dumps(data, indent=4)  # Store formatted JSON in the field
            self.status = 'active'  # Update the status of the device to 'active'

            # Extract the 'parameters' from the JSON data
            parameters = data.get('parameters', [])
            if parameters:
                # Unlink all existing device parameters first to avoid duplicates
                self.device_parameter_ids.unlink()

                # Prepare data for batch creation of device parameters
                param_values = [
                    {
                        'device_id': self.id,  # Correctly reference the current device by ID
                        'parameter_name': param.get('name'),
                        'parameter_value': param.get('value'),
                    }
                    for param in parameters
                ]

                # Create all parameters in a single batch if there are any values
                if param_values:
                    self.env['device.parameter'].create(param_values)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "Success",
                    'message': "Device connected successfully!",
                    'type': 'success',
                    'sticky': False,
                }
            }

        
class DeviceParameter(models.Model):
    _name = 'device.parameter'
    _description = 'Device Parameter'

    device_id = fields.Many2one('device', string='Device', required=True, ondelete='cascade')
    parameter_name = fields.Char(string='Parameter Name', required=True)
    parameter_value = fields.Char(string='Parameter Value')
