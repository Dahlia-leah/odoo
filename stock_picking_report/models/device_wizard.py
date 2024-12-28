from odoo import models, fields, api, _

class DeviceSelectionWizard(models.TransientModel):
    _name = 'device.selection.wizard'
    _description = 'Device Selection Wizard'

    device_id = fields.Many2one(
        'devices.device', string='Select Device', required=True,
        domain="[('connection_status', '=', 'connected')]",
        help="Select a device to fetch weight data."
    )

    @api.model
    def default_get(self, fields_list):
        """
        Populate default values for the wizard.
        """
        res = super(DeviceSelectionWizard, self).default_get(fields_list)
        connected_devices = self.env['devices.device'].search([('connection_status', '=', 'connected')])
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
            stock_move.selected_device_id = self.device_id
            stock_move.action_print_report()
