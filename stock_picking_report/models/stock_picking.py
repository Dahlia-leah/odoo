from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning
import requests
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    selected_device_id = fields.Many2one(
        'devices.device', string='Selected Device',
        help="The device selected for fetching weight data."
    )
    time_printing = fields.Datetime(string="Time Printing", default=fields.Datetime.now)

    def fetch_and_update_scale_data(self):
        """
        Fetches scale data from the selected device's associated connection.
        Updates stock move with weight and unit. Sends a notification if the scale or connection is not valid.
        """
        self.ensure_one()

        # Reset fields to empty initially
        self.write({'external_weight': '', 'external_unit': ''})

        if not self.selected_device_id:
            self._notify_user(_("No device selected. Please select a scale device before printing."))
            _logger.warning("No device selected for fetching scale data.")
            return

        # Fetch the corresponding connection for the selected device
        connection = self.env['devices.connection'].search([('device_id', '=', self.selected_device_id.id)], limit=1)

        if not connection or connection.status != 'valid':
            self._notify_user(_(
                f"The connection associated with device {self.selected_device_id.name} is invalid or not found. "
                f"Printing will proceed with empty scale data."
            ))
            _logger.warning(f"Invalid or missing connection for device {self.selected_device_id.name}.")
            return

        try:
            # Sending GET request to the connection's URL
            headers = {
                'User-Agent': 'PostmanRuntime/7.30.0',
                'Accept': 'application/json',
            }
            _logger.info(f"Connecting to scale service at {connection.url}")
            response = requests.get(connection.url, headers=headers, timeout=10, verify=False)

            if response.status_code == 200:
                # Parse the response data (assuming JSON format)
                data = response.json()
                weight = data.get("weight", "")  # Default to empty if weight is not found
                unit = data.get("unit", "")     # Default to empty if unit is not found

                if not weight and not unit:
                    self._notify_user(_("The scale service did not return weight or unit data. Printing will proceed with empty scale data."))
                    _logger.warning("The scale service did not return weight or unit data.")
                    return

                # Update stock move with the fetched data
                self.write({'external_weight': str(weight), 'external_unit': unit})
                _logger.info(f"Updated stock move with weight: {weight} and unit: {unit}")
            else:
                self._notify_user(_(f"Failed to fetch scale data: HTTP {response.status_code}. Printing will proceed with empty scale data."))
                _logger.error(f"Failed to fetch scale data: HTTP {response.status_code}.")

        except requests.exceptions.RequestException as e:
            self._notify_user(_(f"Error connecting to the scale service: {str(e)}. Printing will proceed with empty scale data."))
            _logger.error(f"Error connecting to the scale service: {str(e)}")

    def _notify_user(self, message):
        """
        Sends a notification to the current user using the bus notification framework.
        """
        notifications = [(self.env.user.partner_id, 'simple_notification', {'message': message, 'type': 'warning'})]
        self.env['bus.bus']._sendmany(notifications)

    def action_print_report(self):
        """
        Trigger the printing of the report.
        Fetch and update scale data before printing, but always proceed with printing.
        """

        if not self.selected_device_id or self.selected_device_id.connection_status != 'valid':
            # Open the wizard for device selection
            action = self.env.ref('stock_picking_report.device_selection_wizard_action').read()[0]
            action['context'] = {'active_id': self.id}
            raise RedirectWarning(
                _("You need to select a valid device before printing."),
                action['id'],
                _("Select Device")
            )

        # Attempt to fetch and update scale data
        self.fetch_and_update_scale_data()

        # Proceed with printing the report
        report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
        if report_action:
            return report_action.report_action(self)
        else:
            raise UserError(_("Report action not found."))