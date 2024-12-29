import requests
import json
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)  # Initialize logger

class Connection(models.Model):
    _name = 'devices.connection'
    _description = 'Device Connection'

    name = fields.Char(string='Connection Name', required=True)
    device_id = fields.Many2one('devices.device', string='Device', required=True)
    url = fields.Char(string='Connection URL', required=True)
    json_data = fields.Text(string='JSON Data', readonly=True)
    status = fields.Selection(
        [('valid', 'Valid'), ('invalid', 'Invalid')],
        string='Status',
        readonly=True,
        default='invalid'
    )

    def check_and_refresh_url(self):
        """
        Checks the connection URL and updates its status and JSON data.
        Removes records if the response is not valid JSON.
        """
        headers = {
            'User-Agent': 'PostmanRuntime/7.30.0',  # Mimic Postman behavior
            'Accept': 'application/json',           # Request JSON response
        }
        for record in self:
            try:
                _logger.info(f"Checking URL for {record.name}: {record.url}")  # Log URL check
                response = requests.get(record.url, headers=headers, timeout=10, verify=False)
                response.raise_for_status()  # Ensure HTTP status code is 2xx

                try:
                    json_data = response.json()
                except ValueError:
                    _logger.warning(f"Invalid JSON from {record.url}")  # Log invalid JSON
                    record.status = 'invalid'
                    record.json_data = False
                    record.unlink()  # Delete invalid record
                    continue

                record.status = 'valid'
                record.json_data = json.dumps(json_data, indent=4)
                _logger.info(f"Valid JSON received for {record.name}")  # Log valid JSON

            except requests.exceptions.RequestException as e:
                _logger.error(f"Request failed for {record.name} ({record.url}): {str(e)}")  # Log request failure
                record.status = 'invalid'
                record.json_data = False
                record.unlink()  # Delete invalid record

  