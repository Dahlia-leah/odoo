import logging
import requests
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

    @api.model
   def fetch_data_from_device(self):
        device_identifier = 'DESKTOP-9C193ML'

        _logger.info(f"Fetching data from IoT device with identifier: {device_identifier}")
        device = self.env['iot.device'].search([
            ('identifier', '=', device_identifier),
            ('type', '=', 'scale')
        ], limit=1)

        if not device:
            raise UserError(f"No IoT device found for identifier: {device_identifier}")

        try:
            data = device.iot_device_call('read')
            _logger.info(f"Weight data received: {data}")
            self.write({
                'external_weight': data['value'],
                'external_unit': data['unit'],
            })
        except Exception as e:
            _logger.error(f"Failed to fetch weight data: {e}")
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
