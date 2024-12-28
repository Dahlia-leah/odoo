from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning
import logging

_logger = logging.getLogger(__name__)
class DeviceSelectionWizard(models.TransientModel):
    _name = 'devices.device.selection.wizard'
    _description = 'Device Selection Wizard'

    selected_device_id = fields.Many2one(
        'devices.connection', string='Selected Device',
        help="The device selected for fetching weight data.",
        required=True
    )

    def action_confirm(self):
        """
        Check the connection status after device selection and retrieve the connection details.
        """
        # Fetch the corresponding connection for the selected device
        connection = self.env['devices.connection'].search([('device_id', '=', self.selected_device_id.id)], limit=1)
        
        if not connection:
            raise UserError(_("No connection found for the selected device."))

        # Check if the connection status is valid
        if connection.status != 'valid':
            message = _(
                f"The connection associated with the device {self.selected_device_id.name} is invalid. "
                "Printing will proceed with empty scale data."
            )
            # Notify the user about the invalid connection
            self.env.user.notify_warning(message)
            _logger.warning(message)
        else:
            # Connection is valid, proceed to print the report
            _logger.info(f"Connection for device {self.selected_device_id.name} is valid.")
            
            # Trigger the printing action for the stock.move
            stock_move = self.env['stock.move'].browse(self._context.get('active_id'))
            if stock_move:
                # Proceed to fetch scale data and print the report
                stock_move.fetch_and_update_scale_data()
                report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
                if report_action:
                    return report_action.report_action(stock_move)
                else:
                    raise UserError(_("Report action not found."))
        
        return True
