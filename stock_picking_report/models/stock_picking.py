from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)

@api.model
def fetch_data_from_device(self, **kwargs):
    """
    Fetch weight data from the Adam Scale connected via the IoT Box.
    """
    # Locate the scale device
    device = self.env['iot.device'].search([
        ('identifier', '=', 'scale_com5')
    ], limit=1)

    if not device:
        raise UserError("No scale device found. Ensure the IoT Box is configured correctly.")

    # Get the driver for the device
    driver = device.get_driver()

    # Read weight data
    data = driver.read_weight()
    if not data:
        raise UserError("Failed to fetch weight data from the scale.")

    # Update the record
    self.write({
        'external_weight': data['weight'],
        'external_unit': data['unit']
    })
    _logger.info(f"Fetched weight: {data['weight']} {data['unit']}")
    return True


    def action_print_report(self):
        """
        Fetch weight data and trigger the stock picking report.
        """
        self.fetch_data_from_device()
        return self.env.ref('stock_picking_report.action_report_stock_picking').report_action(self)
