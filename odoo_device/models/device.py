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
                self.device_parameter_ids.unlink()
                for param in parameters:
                    self.device_parameter_ids.create({
                        'device_id': self.id,
                        'parameter_name': param.get('name'),
                        'parameter_value': param.get('value'),
                    })

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