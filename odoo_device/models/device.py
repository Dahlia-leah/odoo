from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class Device(models.Model):
    _name = 'device'
    _description = 'Device'

    name = fields.Char(string='Device Name', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('out_of_service', 'Out of Service'),
        ('inactive', 'Inactive'),
    ], string='Status', default='inactive')
    json_data = fields.Text(string="JSON Data", readonly=True)
    url = fields.Char(string="URL to fetch JSON from", required=True)

    device_parameter_ids = fields.One2many(
        comodel_name='device.parameter',
        inverse_name='device_id',
        string='Device Parameters'
    )

    def validate_json(self, url):
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

    def action_submit_url(self):
        if not self.url:
            raise UserError("The URL cannot be empty.")

        data = self.validate_json(self.url)

        if data is False:
            raise UserError("The URL is invalid or the request failed.")
        elif data is None:
            raise UserError("The URL does not return valid JSON.")
        else:
            self.json_data = json.dumps(data, indent=4)
            self.status = 'active'

            parameters = data.get('parameters', [])
            if parameters:
                # Unlink all existing device parameters first
                self.device_parameter_ids.unlink()

                # Prepare data for batch creation
                param_values = [
                    {
                        'device_id': self.id,  # This is the correct reference to the device by ID
                        'parameter_name': param.get('name'),
                        'parameter_value': param.get('value'),
                    }
                    for param in parameters
                ]

                # Create all parameters in a single batch
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

    device_id = fields.Many2one('device', string='Device', required=True, ondelete='cascade')  # Correctly referencing the device ID
    parameter_name = fields.Char(string='Parameter Name', required=True)
    parameter_value = fields.Char(string='Parameter Value')
