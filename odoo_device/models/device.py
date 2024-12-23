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
    name = fields.Char(string='Device Name', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('out_of_service', 'Out of Service'),
        ('inactive', 'Inactive'),
    ], string='Status', default='active')
    json_data = fields.Text(string="JSON Data")
    url = fields.Char(string="URL to fetch JSON from", required=True)

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

    def action_connect(self):
        """This method will open the form to input the URL."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'device',
            'view_mode': 'form',
            'target': 'new',  # Opens as a modal window
        }

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
            self.status = 'active'

            # Log the JSON data
            _logger.info(f"Fetched JSON Data from URL ({self.url}): {self.json_data}")

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

    def action_remove_device(self):
        """Allows removing a device record."""
        self.ensure_one()  # Ensure only one record is being processed
        device_name = self.name
        self.unlink()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Device Removed",
                'message': f"The device '{device_name}' has been removed successfully.",
                'type': 'success',
                'sticky': False,
            }
        }
