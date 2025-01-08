from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import requests
import json

_logger = logging.getLogger(__name__)

class Connection(models.Model):
    _name = 'devices.connection'
    _description = 'Device Connection'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Connection Name', required=True, index=True, tracking=True)
    device_id = fields.Many2one('devices.device', string='Device', required=True, ondelete='cascade', tracking=True)
    connection_code = fields.Char(string='Connection Code', required=True, tracking=True)
    url = fields.Char(string='URL', compute='_compute_url', store=True, readonly=True, tracking=True)
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
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True, tracking=True)

    @api.depends('connection_code')
    def _compute_url(self):
        for record in self:
            if record.connection_code:
                record.url = f"https://{record.connection_code}.ngrok-free.app/read-scale"
            else:
                record.url = False

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

    @api.constrains('connection_code')
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
        if 'connection_code' in vals:
            self._check_json_in_url()
        return result

    def name_get(self):
        return [(record.id, f"{record.name} ({record.device_id.name})") for record in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None, **kwargs):
        # Modify args safely, without affecting search logic
        args = args or []
        domain = []
        
        if name:
            domain = ['|', ('name', operator, name), ('device_id.name', operator, name)]

        # Add user-based domain filter before performing the search
        domain += [('user_id', '=', self.env.user.id)]
        
        return super(Connection, self)._search(domain + args, limit=limit, access_rights_uid=name_get_uid, **kwargs)

    def read(self, fields=None, load='_classic_read'):
        # Check if the current user is trying to access a connection that belongs to them
        user = self.env.user
        for record in self:
            if record.user_id != user:
                raise UserError(_("You do not have access to this connection. Please enter a new scale to proceed."))
        return super(Connection, self).read(fields, load)

    @api.model
    def _search(self, domain, limit=None, access_rights_uid=None, **kwargs):
     # Add user-specific domain filter to restrict search results
      domain += [('user_id', '=', self.env.user.id)]  # Ensure user-specific filtering
    
      # Pass the domain, limit, access_rights_uid, and kwargs correctly to avoid conflicts
      return super(Connection, self)._search(domain, limit=limit, access_rights_uid=access_rights_uid, **kwargs)
