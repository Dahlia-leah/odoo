import requests
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
        readonly=True
    )

    @api.constrains('url')
    def _check_json_in_url(self):
        for record in self:
            try:
                # Fetch the content from the URL
                response = requests.get(record.url, timeout=10)
                response.raise_for_status()  # Raise an error for bad HTTP status codes

                # Attempt to parse the response as JSON
                json_data = response.json()
                record.status = 'valid'
                record.json_data = json.dumps(json_data, indent=4)
            except (requests.exceptions.RequestException, ValueError) as e:
                # Handle connection errors and invalid JSON
                record.status = 'invalid'
                raise ValidationError(f'The URL does not contain valid JSON data: {e}')