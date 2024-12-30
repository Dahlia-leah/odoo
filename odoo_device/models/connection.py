from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class Connection(models.Model):
    _name = 'devices.connection'
    _description = 'Device Connection'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Connection Name', required=True, index=True, tracking=True)
    device_id = fields.Many2one('devices.device', string='Device', required=True, ondelete='cascade', tracking=True)
    url = fields.Char(string='Connection code', required=True, tracking=True)
    json_data = fields.Text(string='JSON Data', readonly=True)
    status = fields.Selection(
        [('valid', 'Valid'), ('invalid', 'Invalid')],
        string='Status',
        readonly=True,
        default='invalid',
        tracking=True
    )
    active = fields.Boolean(default=True, string="Active", tracking=True)
    last_checked = fields.Datetime(string="Last Checked", readonly=True)
       
    @api.model
    def create(self, vals):
        if 'url' in vals:
            partial_url = vals['url']
            # Append the fixed part of the URL
            vals['url'] = f'https://{partial_url}.ngrok-free.app/read-scale'
        return super(odoo_device, self).create(vals)

    def write(self, vals):
        if 'url' in vals:
            partial_url = vals['url']
            # Append the fixed part of the URL
            vals['url'] = f'https://{partial_url}.ngrok-free.app/read-scale'
        return super(odoo_device, self).write(vals)
    
    def _check_json_in_url(self):
        self.ensure_one()
        headers = {
            'User-Agent': 'PostmanRuntime/7.30.0',
            'Accept': 'application/json',
        }
        try:
            _logger.info(f"Attempting to fetch JSON from URL: {self.url}")
            response = requests.get(self.url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            try:
                json_data = response.json()
                self.write({
                    'status': 'valid',
                    'json_data': json.dumps(json_data, indent=4),
                    'last_checked': fields.Datetime.now(),
                })
                _logger.info(f"Successfully fetched and validated JSON for connection: {self.name}")
            except ValueError as e:
                self.write({
                    'status': 'invalid',
                    'last_checked': fields.Datetime.now(),
                })
                _logger.error(f"Invalid JSON for connection {self.name}: {str(e)}")
        except requests.exceptions.RequestException as e:
            self.write({
                'status': 'invalid',
                'last_checked': fields.Datetime.now(),
            })
            _logger.error(f"Failed to fetch URL for connection {self.name}: {str(e)}")

    @api.model
    def _cron_check_connections(self):
        connections = self.search([('active', '=', True)])
        for connection in connections:
            connection._check_json_in_url()

    @api.constrains('url')
    def _check_url_constraint(self):
        for record in self:
            record._check_json_in_url()

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
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None, **kwargs):
       # Remove the 'order' argument if it exists
       if 'order' in kwargs:
           del kwargs['order']
    
       args = args or []
       domain = []
    
       if name:
           domain = ['|', ('name', operator, name), ('device_id.name', operator, name)]
    
       # Perform the search with the domain and other arguments
       return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
