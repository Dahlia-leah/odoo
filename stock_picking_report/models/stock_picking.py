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
        iot_device = self.env['iot.device'].search([('type', '=', 'scale')], limit=1)
        if not iot_device:
            raise UserError(_("No scale device found. Please configure the scale in the IoT app."))

        try:
            data = iot_device.device_proxy.get_data()
            self.external_weight = data.get('value')
            self.external_unit = data.get('unit')
            _logger.info("Fetched weight: %s %s", self.external_weight, self.external_unit)
        except Exception as e:
            _logger.error("Error fetching data from IoT scale: %s", e)
            raise UserError(_("Failed to fetch data from the scale. Please check the connection."))

    def action_print_report(self):
        """
        Fetch weight data and trigger the stock picking report generation.
        """
        self.fetch_data_from_device()
        return self.env.ref('stock_picking_report.action_report_stock_picking').report_action(self)
