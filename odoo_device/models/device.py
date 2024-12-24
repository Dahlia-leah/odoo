from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class Device(models.Model):
    _name = 'device'
    _description = 'Device'

    # Fields for device information
    name = fields.Char(string='Device Name', required=True)  # Char field, no foreign key here
    status = fields.Selection([
        ('active', 'Active'),
        ('out_of_service', 'Out of Service'),
        ('inactive', 'Inactive'),
    ], string='Status', default='inactive')
    json_data = fields.Text(string="JSON Data", readonly=True)
    url = fields.Char(string="URL to fetch JSON from", required=True)

    # One2many relationship to manage parameters
    device_parameter_ids = fields.One2many(
        comodel_name='device.parameter',
        inverse_name='device_id',
        string='Device Parameters'
    )

    def validate_json(self, url):
        """Validate if the URL returns valid JSON"""
        try:
            response = requests.get(url, timeout=10)  # Added timeout for better error handling
            response.raise_for_status()  # Raise an error if request fails
            data = response.json()  # Try parsing response as JSON
            return data
        except ValueError:
            _logger.error(f"Invalid JSON response from {url}")
            return None  # Invalid JSON
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error while requesting {url}: {e}")
            return False  # Invalid URL or request failed

    def action_submit_url(self):
        """Handles the URL input, validates the JSON, stores it, or raises an error."""
        if not self.url:
            raise UserError("The URL cannot be empty.")

        data = self.validate_json(self.url)

        if data is False:
            raise UserError("The URL is invalid or the request failed.")
        elif data is None:
            raise UserError("The URL does not return valid JSON.")
        else:
            # Store the JSON response in the json_data field
            self.json_data = json.dumps(data, indent=4)
            self.status = 'active'  # Update the status to active when JSON is fetched

            # Log the JSON data
            _logger.info(f"Fetched JSON Data from URL ({self.url}): {self.json_data}")

            # Optionally, update device parameters from JSON data
            parameters = data.get('parameters', [])
            if parameters:
                self.device_parameter_ids.unlink()  # Clear existing parameters
                for param in parameters:
                    self.device_parameter_ids.create({
                        'device_id': self.id,
                        'parameter_name': param.get('name'),
                        'parameter_value': param.get('value'),
                    })

            # Success message
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
