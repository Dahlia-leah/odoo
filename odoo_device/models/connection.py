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
        readonly=True
    )

    @api.constrains('url')
    def _check_json_in_url(self):
        for record in self:
            headers = {
                'User-Agent': 'PostmanRuntime/7.30.0',  # Mimic Postman behavior
                'Accept': 'application/json',           # Request JSON response
            }
            try:
                # Fetch the URL content
                response = requests.get(record.url, headers=headers, timeout=10, verify=False)

                # Attempt to parse the response content as JSON
                try:
                    json_data = response.json()
                except ValueError as e:
                    raise ValidationError("The response is not valid JSON.")

                # Check if the JSON parsing succeeded regardless of HTTP status
                record.status = 'valid'
                record.json_data = json.dumps(json_data, indent=4)
            except requests.exceptions.RequestException as e:
                # Handle network-related issues
                record.status = 'invalid'
                raise ValidationError(f"Failed to fetch URL: {e}")
            
    @api.model
    def refresh_connections_cron(self):
        """
        Scheduled action to refresh the status of all connections.
        Removes connections that fail validation or don't return JSON.
        """
        _logger.info("Refreshing device connections...")  # Log cron execution
        all_connections = self.search([])  # Get all connection records
        all_connections.check_and_refresh_url()  # Refresh all connections with the above method
