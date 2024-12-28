from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DeviceSelectionWizard(models.TransientModel):
    _name = 'device.selection.wizard'
    _description = 'Device Selection Wizard'

    device_id = fields.Many2one(
        'devices.device', 
        string='Select Device', 
        required=True,
        domain="[('status', '=', 'valid')]",  # Updated field from 'connection_status' to 'status'
        help="Select a device to fetch weight data."
    )

    @api.model
    def default_get(self, fields_list):
        """
        Populate default values for the wizard.
        """
        res = super(DeviceSelectionWizard, self).default_get(fields_list)
        connected_devices = self.env['devices.device'].search([('status', '=', 'valid')])  # Updated field
        if not connected_devices:
            raise UserError(_("No connected devices found. Please connect a device before proceeding."))
        return res

    def confirm_selection(self):
        """
        Confirm the device selection and save it to the active stock move.
        """
        active_id = self.env.context.get('active_id')
        stock_move = self.env['stock.move'].browse(active_id)
        if stock_move:
            # Ensure the stock.move model has the selected_device_id field
            if hasattr(stock_move, 'selected_device_id'):
                stock_move.selected_device_id = self.device_id
            else:
                raise UserError(_("The selected stock move does not support device selection."))

            # Ensure that action_print_report exists for stock.move model
            if hasattr(stock_move, 'action_print_report'):
                stock_move.action_print_report()
            else:
                raise UserError(_("The action_print_report method is not available on this stock move."))
