class XDeviceConnection(models.Model):
    _name = 'x.device.connection'
    _description = 'Device Connection'

    device_id = fields.Many2one('x.device', string='Device', required=True)
    url = fields.Char(string="URL to Fetch JSON From", required=True)
    connection_status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
    ], string="Connection Status", default='disconnected')

    def action_submit_url(self):
        for connection in self:
            if not connection.url:
                raise UserError("The URL cannot be empty.")
            
            data = self._fetch_json_data(connection.url)
            if data is False:
                raise UserError("The URL is invalid or the request failed.")
            elif data is None:
                raise UserError("The URL does not return valid JSON.")
            else:
                connection.connection_status = 'connected'
                _logger.info(f"Connection to device {connection.device_id.name} established successfully.")

    def _fetch_json_data(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except ValueError:
            _logger.error(f"Invalid JSON response from {url}")
            return None
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error while requesting {url}: {e}")
            return False

class XDevice(models.Model):
    _name = 'x.device'
    _description = 'Device'

    name = fields.Char(string='Device Name', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('out_of_service', 'Out of Service'),
        ('inactive', 'Inactive'),
    ], string='Status', default='inactive')

    json_data = fields.Text(string="JSON Data", readonly=True)
    url = fields.Char(string="URL to fetch JSON from", required=True)

    device_parameter_ids = fields.One2many(
        comodel_name='x.device.parameter',
        inverse_name='device_id',
        string='Device Parameters'
    )

    device_connection_ids = fields.One2many(
        comodel_name='x.device.connection',
        inverse_name='device_id',
        string='Device Connections'
    )

    def action_submit_url(self):
        if not self.url:
            raise UserError("The URL cannot be empty.")

        data = self._fetch_json_data(self.url)

        if data is False:
            raise UserError("The URL is invalid or the request failed.")
        elif data is None:
            raise UserError("The URL does not return valid JSON.")
        else:
            self.json_data = json.dumps(data, indent=4)
            self.status = 'active'

            parameters = data.get('parameters', [])
            if parameters:
                self.device_parameter_ids.unlink()

                param_values = [
                    {
                        'device_id': self.id,
                        'parameter_name': param.get('name'),
                        'parameter_value': param.get('value'),
                    }
                    for param in parameters
                ]
                if param_values:
                    self.env['x.device.parameter'].create(param_values)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "Success",
                    'message': "Device connected successfully!",
                    'type': 'success',
                    'sticky': False,
                }
            }

    def _fetch_json_data(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except ValueError:
            _logger.error(f"Invalid JSON response from {url}")
            return None
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error while requesting {url}: {e}")
            return False
