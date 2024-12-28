from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DeviceSelectionWizard(models.TransientModel):
    _name = 'device.selection.wizard'
    _description = 'Device Selection Wizard'

    device_id = fields.Many2one(
        'devices.device',
        string='Select Device',
        required=True,
        domain="[('status', '=', 'valid')]",  # Filters devices with valid status
        help="Select a device to fetch weight data."
    )

    @api.model
    def default_get(self, fields_list):
        """
        Populate default values for the wizard.
        """
        res = super(DeviceSelectionWizard, self).default_get(fields_list)
        connected_devices = self.env['devices.device'].search([('status', '=', 'valid')])
        if not connected_devices:
            raise UserError(_("No connected devices found. Please connect a device before proceeding."))
        return res

    def confirm_selection(self):
        """
        Confirm the device selection and save it to the active stock move.
        """
        # Fetch the active stock move record from the context
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise UserError(_("No active record found to link the device to."))

        stock_move = self.env['stock.move'].browse(active_id)
        if not stock_move.exists():
            raise UserError(_("The selected stock move does not exist."))

        # Check if `selected_device_id` field exists on the stock move model
        if not hasattr(stock_move, 'selected_device_id'):
            raise UserError(_("The stock move does not support device selection."))

        # Set the selected device on the stock move
        stock_move.selected_device_id = self.device_id

        # Check if `action_print_report` method exists
        if not hasattr(stock_move, 'action_print_report'):
            raise UserError(_("The stock move does not have a method to print the report."))

        # Call the method to print the report
        stock_move.action_print_report()
