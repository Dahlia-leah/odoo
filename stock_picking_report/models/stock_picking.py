from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

# Set up logger
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(string="Time Printing", default=fields.Datetime.now)

    def fetch_data_from_device(self, *args, **kwargs):
        """
        Fetch weight data from the connected IoT device and update the stock move.
        """
        for record in self:
            _logger.info("Fetching data for record: %s", record.id)

            # Find the IoT device (e.g., a scale)
            device = self.env['iot.device'].search([
                ('identifier', '=', 'scale_com5')
            ], limit=1)

            if not device:
                raise UserError(_("No scale device found. Check IoT configuration."))

            # Fetch driver and data
            try:
                driver = device.get_driver()
                data = driver.read_weight()
            except Exception as e:
                _logger.error("Error fetching weight data: %s", str(e))
                raise UserError(_("Failed to connect to the scale device."))

            if not data or 'weight' not in data or 'unit' not in data:
                raise UserError(_("Failed to retrieve valid weight data."))

            # Update the record
            record.write({
                'external_weight': data['weight'],
                'external_unit': data['unit']
            })

        return True

    def action_print_report(self):
        """
        Fetch weight data and trigger the stock picking report.
        """
        self.fetch_data_from_device()
        return self.env.ref('stock_picking_report.action_report_stock_picking').report_action(self)
