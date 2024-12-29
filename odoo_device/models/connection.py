import requests
import json
from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
                # Fetch the URL content
                response = requests.get(record.url, headers=headers, timeout=10, verify=False)
                response.raise_for_status()  # Ensure HTTP status code is 2xx

                # Validate and parse the response as JSON
                try:
                    json_data = response.json()
                except ValueError:
                    # If response is not valid JSON, remove the record
                    record.status = 'invalid'
                    record.json_data = False
                    record.unlink()
                    continue

                # Update record with valid JSON data
                record.status = 'valid'
                record.json_data = json.dumps(json_data, indent=4)

            except (requests.exceptions.RequestException, Exception):
                # Handle request or other exceptions
                record.status = 'invalid'
                record.json_data = False
                record.unlink()

    @api.model
    def refresh_connections_cron(self):
        """
        Scheduled action to refresh the status of all connections.
        Removes connections that fail validation or don't return JSON.
        """
        all_connections = self.search([])
        all_connections.check_and_refresh_url()
