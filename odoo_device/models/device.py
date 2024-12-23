from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json

class Device(models.Model):
    _name = 'device'
    _description = 'Device'

    # Fields for the Device Model
    name = fields.Char(string='Device Name', required=True)
    device_type = fields.Selection([
        ('mobile', 'Mobile'),
        ('laptop', 'Laptop'),
        ('tablet', 'Tablet'),
        ('other', 'Other'),
    ], string='Device Type', default='other')
    serial_number = fields.Char(string='Serial Number')
    purchase_date = fields.Date(string='Purchase Date')
    warranty_expiry = fields.Date(string='Warranty Expiry')

    # New Field: Status of Device (Active, Out of Service, etc.)
    status = fields.Selection([
        ('active', 'Active'),
        ('out_of_service', 'Out of Service'),
        ('inactive', 'Inactive'),
    ], string='Status', default='active')

    # Field to store JSON Data fetched from the URL
    json_data = fields.Text(string="JSON Data")

    # Field to input the URL in the form
    url = fields.Char(string="URL to fetch JSON from")

    @api.model
    def action_connect(self):
        """This method will be triggered when the 'Connect' button is clicked"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'device',
            'view_mode': 'form',
            'view_id': self.env.ref('your_module.view_device_form_url_input').id,
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
        """Handles the URL input, validates the JSON, and stores it"""
        url = self.url
        data = self.validate_json(url)

        if data is False:
            raise UserError("The URL is invalid or the request failed.")
        elif data is None:
            raise UserError("The URL does not return valid JSON.")
        else:
            # Store the JSON response in the json_data field
            self.json_data = json.dumps(data)

            # Optionally, you can process the JSON data further

            # Close the modal after submission
            return {'type': 'ir.actions.act_window_close'}
