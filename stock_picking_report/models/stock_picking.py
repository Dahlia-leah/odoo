import requests  # Add this import
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(string="Time Printing", default=fields.Datetime.now)
    
    def fetch_data_from_iot_box(self):
        """
        Attempt to fetch weight data from the IoT Box using the IP address stored in the iot.box model.
        If the model is not found, fallback to a default IP address.
        """
        try:
            # Try to get the iot.box model
            iot_box = self.env['iot.box'].search([], limit=1)  # Adjust the search criteria as needed
            if iot_box:
                ip = iot_box.ip_url  #  the field is named 'ip'
                url = f"http://{ip}:5000/balance"  # Construct the URL using the IP address
                _logger.info(f"Fetching data from IoT Box at {url}...")
                response = requests.get(url, timeout=5)
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()
                _logger.info(f"Data received from IoT Box: {data}")
                return {
                    'weight': data.get('value', 'N/A'),
                    'unit': data.get('unit', 'N/A')
                }
            else:
                # Fallback if no IoT Box is found (use a default IP address)
                _logger.warning("No IoT Box found. Using default IP address.")
                default_ip = "192.168.1.108"  # Example fallback IP address
                url = f"http://{default_ip}:5000/balance"
                _logger.info(f"Fetching data from fallback IoT Box at {url}...")
                response = requests.get(url, timeout=5)
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()
                _logger.info(f"Data received from fallback IoT Box: {data}")
                return {
                    'weight': data.get('value', 'N/A'),
                    'unit': data.get('unit', 'N/A')
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


   # def fetch_data_from_device(self):
   #     """
   #     Fetch weight data from IoT device via the configured interface.
   #     """
   #     # Retrieve the scale device from the IoT configuration
   #     iot_device = self.env['iot.device'].search([('type', '=', 'scale')], limit=1)
   #     if not iot_device:
   #         raise UserError(_("No scale device found. Please configure the scale in the IoT app."))
   #
   #     try:
   #         # Fetch data from the scale device
   #         data = iot_device.device_proxy.get_data()
   #         self.external_weight = data.get('value', '0.0')  # Default to '0.0' if no weight is fetched
   #         self.external_unit = data.get('unit', 'g')  # Default to 'g' (grams) if no unit is found
   #         
   #         # Log the fetched weight and unit, adding extra information for debugging
   #         _logger.info("Fetched weight: %s %s from device %s", self.external_weight, self.external_unit, iot_device.name)
   #         
   #         # You can also check if the fetched weight is valid or not (e.g., numerical check)
   #         if not self.external_weight.replace('.', '', 1).isdigit():
   #             raise UserError(_("Invalid weight value received from the scale. Please check the device."))

   #     except Exception as e:
   #         _logger.error("Error fetching data from IoT scale: %s", str(e))
   #         raise UserError(_("Failed to fetch data from the scale. Please check the connection or configuration."))



    #def action_print_report(self):
    #    """
    #   Fetch weight data and trigger the stock picking report generation.
    #    """
     #   # Fetch the data from the IoT scale before proceeding
    #    self.fetch_data_from_device()

        # Ensure the action is returning the correct report for stock picking
   #     return self.env.ref('stock_picking_report.action_report_stock_picking').report_action(self)
#

