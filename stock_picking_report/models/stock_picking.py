from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(string="Time Printing", default=fields.Datetime.now)

    selected_device_id = fields.Many2one(
        'devices.connection',
        string='Select Device',
        domain=[('status', '=', 'valid')],
        required=True,
        help="Select the scale device to fetch weight and unit data."
    )

    def fetch_and_update_scale_data(self):
        """
        Fetches scale data from the selected device's associated connection.
        Updates stock move with weight and unit. Sends a notification if the scale or connection is not valid.
        """
        self.ensure_one()

        # Reset fields to empty initially
        self.write({'external_weight': '', 'external_unit': ''})

        if not self.selected_device_id:
            self._open_scale_error_wizard(_("No device selected. Please select a scale device before printing."))

        # Log selected device information
        _logger.debug(f"Selected device: {self.selected_device_id.name} (ID: {self.selected_device_id.id})")

        # Fetch the URL from the selected device
        connection = self.selected_device_id
        if not connection or not connection.url:
            self._open_scale_error_wizard(_("The selected device does not have a valid URL."))

        _logger.debug(f"Device URL: {connection.url}")

        try:
            # Send GET request to the device's URL
            headers = {
                'User-Agent': 'PostmanRuntime/7.30.0',
                'Accept': 'application/json',
            }
            _logger.info(f"Connecting to scale service at {connection.url}")
            response = requests.get(connection.url, headers=headers, timeout=10, verify=False)

            if response.status_code == 200:
                # Parse the response data (assuming JSON format)
                data = response.json()
                weight = data.get("weight", "")
                unit = data.get("unit", "")

                if not weight and not unit:
                    self._open_scale_error_wizard(_("The scale service did not return weight or unit data."))

                # Update stock move with fetched data
                self.write({'external_weight': str(weight), 'external_unit': unit})
                _logger.info(f"Updated stock move with weight: {weight} and unit: {unit}")
            else:
                self._open_scale_error_wizard(_(f"Failed to fetch scale data: HTTP {response.status_code}."))

        except requests.exceptions.RequestException as e:
            self._open_scale_error_wizard(_(f"Error connecting to the scale service: {str(e)}."))

    def _open_scale_error_wizard(self, message):
       """
       Opens the wizard for handling scale connection errors.
      """
       return {
          'type': 'ir.actions.act_window',
          'res_model': 'scale.connection.wizard',
          'view_mode': 'form',
          'target': 'new',
          'context': {
              'default_message': message,
              'default_stock_move_id': self.id,
           },
       }


    def action_print_report(self):
        """
        Trigger the printing of the report.
        Fetch and update scale data before printing, but always proceed with printing.
        """
        if not self.selected_device_id:
            raise UserError(_("No device selected. Please select a scale device before printing."))

        # Fetch and update scale data
        self.fetch_and_update_scale_data()

        # Proceed with printing the report
        report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
        if report_action:
            return report_action.report_action(self)
        else:
            raise UserError(_("Report action not found."))
