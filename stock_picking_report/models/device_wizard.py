from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning
import logging

_logger = logging.getLogger(__name__)

class DeviceSelectionWizard(models.TransientModel):
    _name = 'devices.device.selection.wizard'
    _description = 'Device Selection Wizard'

    selected_device_id = fields.Many2one(
        'devices.device', string='Selected Device',
        help="The device selected for fetching weight data.",
        required=True
    )

    def action_confirm(self):
        """
        Check if the device is connected. If not, notify the user and proceed to print.
        Also, fetch all devices connected via the devices.connection model.
        """
        if not self.selected_device_id:
            raise UserError(_("No device selected!"))
        
        # Fetch the corresponding connection for the selected device
        connection = self.env['devices.connection'].search([('device_id', '=', self.selected_device_id.id)], limit=1)

        if not connection or connection.status != 'valid':
            # Notify the user that the scale is not connected
            message = _(
                f"The connection associated with the device {self.selected_device_id.name} is invalid or not found. "
                "Printing will proceed with empty scale data."
            )
            self.env.user.notify_warning(message)
            _logger.warning(message)

        # Fetch all devices associated with valid connections
        valid_connections = self.env['devices.connection'].search([('status', '=', 'valid')])
        valid_devices = valid_connections.mapped('device_id')

        _logger.info(f"Valid devices connected: {', '.join(device.name for device in valid_devices)}")

        # Trigger the printing action for the stock.move
        stock_move = self.env['stock.move'].browse(self._context.get('active_id'))
        if stock_move:
            # Proceed to print the report regardless of the connection status
            stock_move.fetch_and_update_scale_data()
            report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
            if report_action:
                return report_action.report_action(stock_move)
            else:
                raise UserError(_("Report action not found."))

        return True
