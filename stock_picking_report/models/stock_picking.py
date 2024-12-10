import requests
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError
import time

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(
        string="Time of Printing",
        default=fields.Datetime.now
    )
    #expiration_time = fields.Integer(
    #    string="Expiration Time",
    #    related='product_id.product_tmpl_id.expiration_time',
    #    readonly=True,
    #    help="Expiration time of the product as specified in the product template."
    #)

    def fetch_data_from_iot_box(self):
        """
        Attempt to fetch weight data from the IoT Box using the IP address stored in the iot.box model.
        If the model is not found, fallback to a default IP address.
        """
        try:
            url = f"http://192.168.1.23:5000/balance"  # Construct the URL using the IP address
            _logger.info(f"Fetching data from IoT Box at {url}...")
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            _logger.info(f"Data received from IoT Box: {data}")

            # Correcting the key for 'unit' to 'unite' based on the received data
            return {
                'weight': data.get('value', 'N/A'),
                'unit': data.get('unite', 'N/A')  # Corrected from 'unit' to 'unite'
            }

        except requests.exceptions.RequestException as e:
            # Catch specific exception related to network or HTTP issues
            _logger.error(f"Request error while fetching data from IoT Box: {e}")
            self.write({'external_weight': 'N/A', 'external_unit': 'N/A'})
            return None
        except Exception as e:
            # Catch all other exceptions
            _logger.error(f"Unexpected error while fetching data from IoT Box: {e}")
            self.write({'external_weight': 'N/A', 'external_unit': 'N/A'})
            return None

    def fetch_and_update_scale_data(self):
        """
        Fetch data from the IoT Box and update the record.
        Log a warning and proceed without halting execution if fetching fails.
        """
        self.ensure_one()

        # Fetch data from the IoT Box
        scale_data = self.fetch_data_from_iot_box()
        if scale_data:
            weight = scale_data.get('weight', 'N/A')
            unit = scale_data.get('unit', 'N/A')
            self.write({'external_weight': weight, 'external_unit': unit})
            _logger.info(f"Updated fields with weight: {weight} and unit: {unit}")
        else:
            _logger.warning("Failed to fetch data from the IoT Box. Proceeding without weight data.")
            self.write({'external_weight': 'N/A', 'external_unit': 'N/A'})

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
