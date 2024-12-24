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
        readonly=True
    )

    @api.constrains('url')
    def _check_json_in_url(self):
        for record in self:
            try:
                # Simulate validating the URL's content (assume local server simulation)
                json_data = json.loads(record.url)  # Replace with actual URL fetching logic
                record.status = 'valid'
                record.json_data = json.dumps(json_data, indent=4)
            except (json.JSONDecodeError, TypeError):
                record.status = 'invalid'
                raise ValidationError('The URL does not contain valid JSON data.')