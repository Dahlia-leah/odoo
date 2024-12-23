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
    url = fields.Char(string="URL to fetch JSON from")

    @api.model
    def action_connect(self):
        """This method will be triggered when the 'Connect' button is clicked"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'device',
            'view_mode': 'form',
            'view_id': self.env.ref('device.view_device_form_url_input').id,
            'target': 'new',
        }

    def validate_json(self, url):
        """Validate if the URL returns valid JSON"""
        try:
            response = requests.get(url)
            response.raise_for_status()  # If the request failed, it will raise an error
            data = response.json()  # Try to parse the response as JSON
            return data
        except ValueError:
            return None  # Not a valid JSON
        except requests.exceptions.RequestException:
            return False  # URL is not valid or request failed

    def action_submit_url(self):
        """Handles the URL input, validates the JSON, stores it, and prints it"""
        url = self.url
        data = self.validate_json(url)

        if data is False:
            raise UserError("The URL is invalid or the request failed.")
        elif data is None:
            raise UserError("The URL does not return valid JSON.")
        else:
            # Store the JSON response in the json_data field
            self.json_data = json.dumps(data, indent=4)

            # Log the JSON data
            _logger.info(f"Fetched JSON Data from URL ({url}): {self.json_data}")

            # Print the JSON data to the console (for debugging purposes)
            print(f"Fetched JSON Data from URL ({url}):\n{self.json_data}")

            # Close the modal after submission
            return {'type': 'ir.actions.act_window_close'}
