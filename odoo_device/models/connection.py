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
        """
        headers = {
            'User-Agent': 'PostmanRuntime/7.30.0',  # Mimic Postman behavior
            'Accept': 'application/json',           # Request JSON response
        }
        for record in self:
            try:
                # Fetch the URL content
                response = requests.get(record.url, headers=headers, timeout=10, verify=False)
                
                # Attempt to parse the response content as JSON
                try:
                    json_data = response.json()
                except ValueError:
                    # If parsing fails, consider the record invalid and delete it
                    record.status = 'invalid'
                    record.json_data = False
                    record.unlink()
                    continue

                # Update the status and JSON data
                record.status = 'valid'
                record.json_data = json.dumps(json_data, indent=4)

            except requests.exceptions.RequestException:
                # If the request fails, set the status as invalid and delete the record
                record.status = 'invalid'
                record.json_data = False
                record.unlink()

    @api.model
    def refresh_connections_cron(self):
        """
        Scheduled action to refresh the status of all connections.
        """
        self.search([]).check_and_refresh_url()
