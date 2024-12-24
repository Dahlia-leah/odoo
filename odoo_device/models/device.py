from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class Device(models.Model):
    _name = 'device'
    _description = 'Device'

    # Fields for the Device Model
    name = fields.Many2one('device', string='Device Name', required=True, domain="[('status', '=', 'active')]")
    status = fields.Selection([
        ('active', 'Active'),
        ('out_of_service', 'Out of Service'),
        ('inactive', 'Inactive'),
    ], string='Status', default='active')
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
            response = requests.get(url)
            response.raise_for_status()  # Raise an error if request fails
            data = response.json()  # Try parsing response as JSON
            return data
        except ValueError:
            return None  # Invalid JSON
        except requests.exceptions.RequestException:
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


class DeviceParameter(models.Model):
    _name = 'device.parameter'
    _description = 'Device Parameter'

    # Fields for Device Parameters
    device_id = fields.Many2one('device', string='Device', required=True, ondelete='cascade')
    parameter_name = fields.Char(string='Parameter Name', required=True)
    parameter_value = fields.Char(string='Parameter Value')
