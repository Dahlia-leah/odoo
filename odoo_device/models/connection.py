from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import json

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
    active = fields.Boolean(default=True)  # For archiving instead of deletion

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

    def delete_connection(self):
        """Delete connection only if it's not referenced in stock moves."""
        self.ensure_one()  # Ensure this method is called on a single record
        # Check if the connection is being used in any stock move
        stock_moves = self.env['stock.move'].search([('device_id', '=', self.device_id.id)])
        if stock_moves:
            # Raise an error if the connection is being referenced
            raise ValidationError("Cannot delete this connection because it is being used in stock moves. Please archive it instead.")
        else:
            # Proceed with deletion if no references are found
            self.unlink()

    def archive_connection(self):
        """Archive the connection by setting 'active' to False."""
        self.ensure_one()  # Ensure this method is called on a single record
        self.active = False

