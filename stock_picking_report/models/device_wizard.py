from odoo import models, fields

class DeviceSelectionWizard(models.TransientModel):
    _name = 'device.selection.wizard'
    _description = 'Device Selection Wizard'

    device_id = fields.Many2one(
        'devices.device', string='Select Device', required=True,
        help="Select a device to fetch weight data."
    )

    def confirm_selection(self):
        """
        Confirm the device selection and trigger the report action.
        """
        active_id = self.env.context.get('active_id')
        stock_move = self.env['stock.move'].browse(active_id)
        if stock_move:
            stock_move.selected_device_id = self.device_id
            stock_move.action_print_report()
