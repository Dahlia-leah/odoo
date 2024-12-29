from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class Connection(models.Model):
    _name = 'devices.connection'
    _description = 'Device Connection'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Connection Name', required=True, index=True, tracking=True)
    device_id = fields.Many2one('devices.device', string='Device', required=True, ondelete='cascade', tracking=True)
    url = fields.Char(string='Connection URL', required=True, tracking=True)
    json_data = fields.Text(string='JSON Data', readonly=True)
    status = fields.Selection(
        [('valid', 'Valid'), ('invalid', 'Invalid')],
        string='Status',
        readonly=True,
        default='invalid',
        tracking=True
    )
    active = fields.Boolean(default=True, string="Active", tracking=True)

    _sql_constraints = [
        ('unique_device_connection', 'UNIQUE(device_id)', 'Each device can only have one connection!')
    ]

    @api.constrains('url')
    def _check_json_in_url(self):
        for record in self:
            headers = {
                'User-Agent': 'PostmanRuntime/7.30.0',
                'Accept': 'application/json',
            }
            try:
                _logger.info(f"Attempting to fetch JSON from URL: {record.url}")
                response = requests.get(record.url, headers=headers, timeout=10, verify=False)
                response.raise_for_status()
                try:
                    json_data = response.json()
                    record.status = 'valid'
                    record.json_data = json.dumps(json_data, indent=4)
                    _logger.info(f"Successfully fetched and validated JSON for connection: {record.name}")
                except ValueError as e:
                    record.status = 'invalid'
                    raise ValidationError(_("The response is not valid JSON: %s") % str(e))
            except requests.exceptions.RequestException as e:
                record.status = 'invalid'
                _logger.error(f"Failed to fetch URL for connection {record.name}: {str(e)}")
                raise ValidationError(_("Failed to fetch URL: %s") % str(e))

    def delete_connection(self):
        self.ensure_one()
        if self.env['stock.move'].search_count([('selected_device_id', '=', self.id)]) > 0:
            raise ValidationError(_("Cannot delete this connection because it is being used in stock moves. Please archive it instead."))
        _logger.info(f"Deleting connection: {self.name}")
        return self.unlink()

    def archive_connection(self):
        self.ensure_one()
        self.active = False
        _logger.info(f"Archived connection: {self.name}")
        return True

    @api.model
    def create(self, vals):
        record = super(Connection, self).create(vals)
        record._check_json_in_url()
        return record

    def write(self, vals):
        result = super(Connection, self).write(vals)
        if 'url' in vals:
            self._check_json_in_url()
        return result

    def name_get(self):
        return [(record.id, f"{record.name} ({record.device_id.name})") for record in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('device_id.name', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

