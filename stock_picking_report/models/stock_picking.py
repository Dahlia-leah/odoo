import logging
import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Float(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(
        string="Time of Printing",
        default=fields.Datetime.now
    )

    def fetch_data_from_device(self):
        """
        Fetch data from the scale device via HTTP and update the stock picking record.
        """
        url = 'http://192.168.1.23:5000/balance'  # URL of the scale's API

        try:
            _logger.info(f"Fetching data from scale at {url}")
            response = requests.get(url)
            if response.status_code != 200:
                raise UserError(f"Failed to fetch data from scale, HTTP status code: {response.status_code}")

            data = response.json()  # Assuming the response is in JSON format, like {"value": "5.0", "unit": "kg"}
            weight = data.get('value')
            unit = data.get('unit')

            if not weight or not unit:
                raise UserError("Invalid data received from the scale.")

            # Update the stock picking record with fetched data
            self.write({
                'external_weight': float(weight),  # Ensure weight is converted to a float
                'external_unit': unit,
            })

            _logger.info(f"Weight data fetched: {weight} {unit}")
            return True

        except Exception as e:
            _logger.error(f"Failed to fetch weight data from scale: {e}")
            raise UserError(f"Failed to fetch weight data from scale: {e}")

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
