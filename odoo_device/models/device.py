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
    json_data = fields.Text(string="Raw JSON Data")
    json_preview = fields.Text(string="JSON Preview", readonly=True)
    url = fields.Char(string="URL to fetch JSON from", required=True)

    def validate_json(self, url):
        """Validate if the URL returns valid JSON and return it."""
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error if the request fails
            return response.json()  # Return parsed JSON
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
            # Store the JSON response in the json_data and json_preview fields
            self.json_data = json.dumps(data, indent=4)
            self.json_preview = json.dumps(data, indent=4)
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
