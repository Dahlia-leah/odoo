import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(
        string="Time of Printing",
        default=fields.Datetime.now
    )

    def fetch_data_from_device(self):
        """
        Fetch weight data from the IoT device using the IoT framework and update the record.
        """
        self.ensure_one()

        # Define the IoT device identifier
        device_identifier = 'DESKTOP-9C193ML'  # Update with your device's identifier
        _logger.info(f"Attempting to fetch data from IoT device with identifier: {device_identifier}")

        # Search for the IoT device
        device = self.env['iot.device'].search([
            ('identifier', '=', device_identifier),
            ('type', '=', 'scale')
        ], limit=1)

        if not device:
            _logger.warning(f"No IoT device found for identifier: {device_identifier}")
            raise UserError("IoT device not found. Please check the device configuration.")

        try:
            # Call the IoT device using its registered driver
            data = device.iot_device_call('read', {})
            _logger.info(f"Data received from IoT device: {data}")

            # Update the record with the fetched weight and unit
            self.write({
                'external_weight': data.get('value', 'N/A'),
                'external_unit': data.get('unit', 'N/A'),
            })
            _logger.info("Stock move record successfully updated with IoT data.")
        except Exception as e:
            _logger.error(f"Error while communicating with IoT device: {e}")
            self.write({'external_weight': 'N/A', 'external_unit': 'N/A'})
            raise UserError("Failed to fetch data from IoT device. Please check the connection and try again.")

    def action_print_report(self):
        """
        Fetch IoT data, update the record, and print the stock picking report.
        """
        _logger.info("Fetching IoT data before printing the report.")
        self.fetch_data_from_device()

        # Generate the report
        report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
        if report_action:
            _logger.info("Report action found. Printing the report.")
            return report_action.report_action(self)
        else:
            _logger.error("Report action not found.")
            raise UserError("Stock picking report action not found. Please contact your administrator.")
