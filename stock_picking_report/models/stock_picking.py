import logging
import serial
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
        """
        Fetch data from the scale via COM port (e.g., COM5) and update the stock picking record.
        """
        com_port = 'COM5'  # Change this to your actual COM port
        baud_rate = 9600    # Adjust the baud rate according to your device
        timeout = 5         # Timeout in seconds for the serial communication

        try:
            # Initialize the serial connection
            ser = serial.Serial(com_port, baud_rate, timeout=timeout)
            
            # Read the data from the scale (assuming the scale sends data in a known format)
            data = ser.readline().decode('utf-8').strip()  # Read a line and decode it to string
            
            # For example, the scale sends data in the format: "5.0 kg"
            weight, unit = data.split()  # Split the data into weight and unit
            
            if not weight or not unit:
                raise UserError("Invalid data received from the scale.")
            
            # Update the stock picking record with the fetched data
            self.write({
                'external_weight': weight,
                'external_unit': unit,
            })

            _logger.info(f"Weight data fetched from COM5: {weight} {unit}")
            return True

        except serial.SerialException as e:
            _logger.error(f"Error communicating with scale on {com_port}: {e}")
            raise UserError(f"Failed to fetch data from scale: {e}")

        except Exception as e:
            _logger.error(f"Failed to fetch weight data: {e}")
            raise UserError(f"Failed to fetch weight data: {e}")

    def action_print_report(self):
        """
        Fetch data from the scale, update the record, and print the report.
        """
        # Fetch weight data before printing the report
        self.fetch_data_from_device()

        # Proceed with printing the report
        report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
        if report_action:
            return report_action.report_action(self)
        else:
            raise UserError("Report action not found.")
