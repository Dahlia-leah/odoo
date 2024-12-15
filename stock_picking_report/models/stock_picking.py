from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(string="Time Printing", default=fields.Datetime.now)

    def fetch_data_from_device(self):
        """
        Fetch weight data from IoT device via the configured interface.
        """
        # Retrieve the scale device from the IoT configuration
        iot_device = self.env['iot.device'].search([('type', '=', 'scale')], limit=1)
        if not iot_device:
            raise UserError(_("No scale device found. Please configure the scale in the IoT app."))

        try:
            # Fetch data from the scale device
            data = iot_device.device_proxy.get_data()
            self.external_weight = data.get('value', '0.0')  # Default to '0.0' if no weight is fetched
            self.external_unit = data.get('unit', 'g')  # Default to 'g' (grams) if no unit is found
            
            # Log the fetched weight and unit, adding extra information for debugging
            _logger.info("Fetched weight: %s %s from device %s", self.external_weight, self.external_unit, iot_device.name)
            
            # You can also check if the fetched weight is valid or not (e.g., numerical check)
            if not self.external_weight.replace('.', '', 1).isdigit():
                raise UserError(_("Invalid weight value received from the scale. Please check the device."))

        except Exception as e:
            _logger.error("Error fetching data from IoT scale: %s", str(e))
            raise UserError(_("Failed to fetch data from the scale. Please check the connection or configuration."))

    def action_print_report(self):
        """
        Fetch weight data and trigger the stock picking report generation.
        """
        # Fetch the data from the IoT scale before proceeding
        self.fetch_data_from_device()

        # Ensure the action is returning the correct report for stock picking
        return self.env.ref('stock_picking_report.action_report_stock_picking').report_action(self)
