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
    def unlink(self):
        for record in self:
            # Check if there are any stock moves referencing the device
            stock_moves = self.env['stock.move'].search([('device_id', '=', record.device_id.id)])
            if stock_moves:
                # If stock moves exist, raise an error or archive instead of deleting
                raise ValidationError("Cannot delete this connection because it is being used in stock moves. Please archive it instead.")
            else:
                # Proceed with the deletion if no references are found
                return super(Connection, record).unlink()
