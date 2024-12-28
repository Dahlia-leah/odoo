from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.odoo_device.models import devices_connection


class DeviceSelectionWizard(models.TransientModel):
    _name = 'devices.device.selection.wizard'
    _description = 'Device Selection Wizard'

    selected_device_id = fields.Many2one(
        'devices.connection', string='Selected Device',
        help="The device selected for fetching weight data.",
        required=True
    )

    # Add an empty device option to the selection
    def _get_device_options(self):
        devices = self.env['devices.connection'].search([('status', '=', 'valid')])
        
        # Add an empty option, which will not correspond to any device
        empty_device = self.env['devices.connection'].create({
            'name': 'No Device Selected',
            'status': 'empty',
            'device_id': False,  # No associated device
        })
        
        return [(device.id, device.name) for device in devices] + [(empty_device.id, 'No Device Selected')]

    available_devices = fields.Selection(
        _get_device_options,
        string="Select Device",
        required=True,
        help="Choose a device from the list of connected and valid devices. Optionally choose 'No Device Selected'."
    )

    def action_confirm(self):
        """
        Check the connection status after device selection and retrieve the connection details.
        """
        selected_device = self.env['devices.connection'].browse(self.selected_device_id.id)
        
        if selected_device.status == 'empty':
            # Proceed with empty scale data
            message = _("No device selected. Printing will proceed with empty scale data.")
            self.env.user.notify_warning(message)
            _logger.warning(message)
            return True
        
        if selected_device.status != 'valid':
            raise UserError(_("The connection associated with the selected device is invalid. Please choose a valid device."))
        
        # Handle valid device connection and proceed with fetching scale data
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
