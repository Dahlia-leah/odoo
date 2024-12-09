import logging
from odoo import models, fields, api
from odoo.exceptions import UserError
import time

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(
        string="Time of Printing",
        default=fields.Datetime.now
    )
    scale_device_id = fields.Many2one(
        'iot.device',
        string='Scale Device',
        domain=[('type', '=', 'scale')]
    )

    def fetch_data_from_iot_box(self):
        """Fetch weight data using IoT box"""
        self.ensure_one()
        try:
            # Get IoT device from the record or search for default
            iot_device = self.scale_device_id or self.env['iot.device'].search([
                ('type', '=', 'scale'),
                ('identifier', '=', 'scale_1'),
                ('manufacturer', '=', 'Adam')
            ], limit=1)
            
            if not iot_device:
                raise UserError("No scale device configured. Please configure a scale in IoT settings.")
                
            # Request weight reading
            result = iot_device.action({
                'action': 'read_weight'
            })
            
            if not result:
                raise UserError("Failed to read weight from scale.")
            
            # Get the latest data
            return {
                'weight': float(iot_device.last_value or 0.0),
                'unit': iot_device.last_unit or 'kg'
            }
            
        except Exception as e:
            _logger.error(f"Error fetching data from IoT Box: {str(e)}")
            raise UserError(f"Error reading scale: {str(e)}")

    def fetch_and_update_scale_data(self):
        """Fetch and update scale data with proper error handling"""
        self.ensure_one()
        
        try:
            scale_data = self.fetch_data_from_iot_box()
            if scale_data:
                self.write({
                    'external_weight': scale_data['weight'],
                    'external_unit': scale_data['unit'],
                    'time_printing': fields.Datetime.now()
                })
                return True
        except UserError as e:
            raise
        except Exception as e:
            _logger.error(f"Unexpected error updating scale data: {str(e)}")
            raise UserError("Failed to update scale data. Please try again.")

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
