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
        Fetch weight data using the IoT device.
        """
        self.ensure_one()  # Ensure only one record is being processed at a time
        device_identifier = 'DESKTOP-9C193ML'

        _logger.info(f"Fetching data from IoT device with identifier: {device_identifier}")
        # Search for the IoT device
        device = self.env['iot.device'].search([
            ('identifier', '=', device_identifier),
            ('type', '=', 'scale')
        ], limit=1)

        if not device:
            _logger.warning(f"No IoT device found for identifier: {device_identifier}")
            raise UserError(f"No IoT device found for identifier: {device_identifier}")

        try:
            # Call the IoT device's driver to fetch weight data
            data = device.iot_device_call('read', {})
            _logger.info(f"Weight data received: {data}")

            # Validate and update the fields
            if 'value' in data and 'unit' in data:
                self.write({
                    'external_weight': data['value'],
                    'external_unit': data['unit'],
                })
            else:
                raise ValueError("Invalid data format received from IoT device.")
        except Exception as e:
            _logger.error(f"Error while fetching weight data: {e}")
            raise UserError("Failed to fetch weight data from IoT device.")

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
