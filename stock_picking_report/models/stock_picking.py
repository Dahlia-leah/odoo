import logging
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(string="Time Printing", default=fields.Datetime.now)

    def fetch_and_update_scale_data(self):
        """
        Fetches scale data from the external source (e.g., reversed proxy).
        Updates stock move with weight and unit.
        """
        self.ensure_one()

        try:
            # Sending GET request to the scale proxy
            url = "http://localhost:5000/read-scale"
            response = requests.get(url)

            if response.status_code == 200:
                # Parse the response data (assuming JSON format)
                data = response.json()
                weight = data.get("weight", "0.0")  # Default to 0 if weight is not found
                unit = data.get("unit", "g")  # Default to 'g' if unit is not found

                # Update stock move with the fetched data
                self.write({'external_weight': str(weight), 'external_unit': unit})
                _logger.info(f"Updated stock move with weight: {weight} and unit: {unit}")

            else:
                raise UserError(f"Failed to fetch scale data: {response.status_code}")

        except requests.exceptions.RequestException as e:
            raise UserError(f"Error connecting to the scale service: {str(e)}")

    def action_print_report(self):
        """
        Trigger the printing of the report.
        Fetch and update scale data before printing.
        """
        # Fetch and update scale data before printing the report
        self.fetch_and_update_scale_data()

        # Proceed with printing the report
        report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
        if report_action:
            return report_action.report_action(self)
        else:
            raise UserError("Report action not found.")
