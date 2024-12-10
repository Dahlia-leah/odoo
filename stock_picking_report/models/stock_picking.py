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
        Fetch weight data using the IoT device and update the stock move record.
        """
        self.ensure_one()
        device_identifier = 'DESKTOP-9C193ML'  # Replace with your IoT device identifier

        # Search for the IoT device in Odoo
        device = self.env['iot.device'].search([
            ('identifier', '=', device_identifier),
            ('type', '=', 'scale')
        ], limit=1)

        if not device:
            raise UserError("No IoT device found for the configured identifier.")

        try:
            _logger.info(f"Fetching weight data from IoT device {device_identifier}...")
            # Use IoT framework to call the device driver
            data = device.iot_device_call('read', {})
            _logger.info(f"Weight data received: {data}")

            # Update the record with the fetched weight data
            self.write({
                'external_weight': data.get('value', 'N/A'),
                'external_unit': data.get('unit', 'N/A')
            })
        except Exception as e:
            _logger.error(f"Error fetching weight data from IoT device: {e}")
            self.write({'external_weight': 'N/A', 'external_unit': 'N/A'})
            raise UserError("Failed to fetch weight data from the IoT device.")

    def action_print_report(self):
        """
        Fetch data from the IoT device, update the record, and print the report.
        """
        # Fetch weight data before printing the report
        self.fetch_data_from_device()

        # Proceed with printing the report
        report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
        if report_action:
            return report_action.report_action(self)
        else:
            raise UserError("Report action not found.")
