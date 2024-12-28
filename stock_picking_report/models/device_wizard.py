from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DeviceSelectionWizard(models.TransientModel):
    _name = 'device.selection.wizard'
    _description = 'Device Selection Wizard'

    device_id = fields.Many2one(
        'devices.connection',
        string='Select Device',
        required=True,
        domain="[('device_id', '=', 1), ('status', '=', 'valid')]",
        help="Select a valid device (ID 1) to fetch weight data."
    )

    active = fields.Boolean(default=True)  # To handle archiving instead of deletion

    @api.model
    def default_get(self, fields_list):
        """
        Populate default values for the wizard.
        """
        res = super(DeviceSelectionWizard, self).default_get(fields_list)

        # Search for devices that are connected (valid) and related to the device ID 1
        connected_devices = self.env['devices.connection'].search([
            ('status', '=', 'valid'),
            ('device_id', '=', 1)  # Filter by the device ID (ID 1)
        ])

        # If no devices are found, raise an error
        if not connected_devices:
            raise UserError(_("No valid devices with ID 1 found. Please connect such a device before proceeding."))
        
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

    @api.model
    def unlink(self):
        """
        Override unlink to prevent deletion if the record is referenced elsewhere.
        Instead of deleting, we archive the record.
        """
        for record in self:
            if record.device_id:
                # You can add additional checks for dependencies or actions to clean up
                # Archive the record instead of deleting it
                record.active = False
                return True
        return super(DeviceSelectionWizard, self).unlink()
