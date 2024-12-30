from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(string="Time Printing", default=fields.Datetime.now)

    mrp_product_id = fields.Many2one(
        comodel_name='product.product',
        string="MRP Product",
       # compute="_compute_mrp_product_id",
        store=True,
    )
    batch_number = fields.Char(
        string="Batch Number",
       # compute="_compute_batch_number",
        store=True,
    )
    exp_date = fields.Date(
        string="Expiration Date",
       # compute="_compute_exp_date",
        store=True,
    )

    selected_device_id = fields.Many2one(
        'devices.connection',
        string='Select Device',
        domain=[('status', '=', 'valid')],
        required=True,
        help="Select the scale device to fetch weight and unit data."
    )

   # @api.depends('picking_id')
   # def _compute_mrp_product_id(self):
   #     for move in self:
    #        move.mrp_product_id = move.picking_id.mrp_product_id

   # @api.depends('picking_id')
    #def _compute_batch_number(self):
    #    for move in self:
     #       lot = move.picking_id.lot_ids[:1] if move.picking_id else False
      #      move.batch_number = lot.display_name if lot else ''

    #@api.depends('move_line_ids.lot_id.expiration_date')
    #def _compute_exp_date(self):
     #   for move in self:
            # Fetch expiration date from stock.move.line's lot_id
     #       expiration_dates = move.move_line_ids.mapped('lot_id.expiration_date')
       #     move.exp_date = expiration_dates[0] if expiration_dates else False



    def fetch_and_update_scale_data(self):
        """
        Fetches scale data from the selected device's associated connection.
        Updates stock move with weight and unit. Sends a notification if the scale or connection is not valid.
        """
        self.ensure_one()

        # Reset fields to empty initially
        self.write({'external_weight': '', 'external_unit': ''})

        if not self.selected_device_id:
            return self._open_scale_error_wizard(_("No device selected. Please select a scale device before printing."))

        # Log selected device information
        _logger.debug(f"Selected device: {self.selected_device_id.name} (ID: {self.selected_device_id.id})")

        # Fetch the URL from the selected device
        connection = self.selected_device_id
        if not connection or not connection.url:
            return self._open_scale_error_wizard(_("The selected device does not have a valid URL."))

        _logger.debug(f"Device URL: {connection.url}")

        try:
            # Send GET request to the device's URL
            headers = {
                'User-Agent': 'PostmanRuntime/7.30.0',
                'Accept': 'application/json',
            }
            _logger.info(f"Connecting to scale service at {connection.url}")
            response = requests.get(connection.url, headers=headers, timeout=10, verify=False)

            if response.status_code == 200:
                # Parse the response data (assuming JSON format)
                data = response.json()
                weight = data.get("weight", "")
                unit = data.get("unit", "")

                if not weight and not unit:
                    return self._open_scale_error_wizard(_("The scale service did not return weight or unit data."))

                # Update stock move with fetched data
                self.write({'external_weight': str(weight), 'external_unit': unit})
                _logger.info(f"Updated stock move with weight: {weight} and unit: {unit}")
            else:
                return self._open_scale_error_wizard(_(f"Failed to fetch scale data: HTTP {response.status_code}."))

        except requests.exceptions.RequestException as e:
            return self._open_scale_error_wizard(_(f"Error connecting to the scale service: {str(e)}."))

    def _open_scale_error_wizard(self, message):
      """
      Opens the wizard for handling scale connection errors.
      Clears the current selected device to prompt the user to reselect.
      """
      self.write({'selected_device_id': False})  # Clear the current device selection
      return {
          'type': 'ir.actions.act_window',
          'res_model': 'scale.connection.wizard',
          'view_mode': 'form',
          'target': 'new',
          'context': {
              'default_message': message,
              'default_stock_move_id': self.id,
          },
      }


    def action_print_report(self):
        """
        Trigger the printing of the report.
        Fetch and update scale data before printing, but always proceed with printing.
        """
        if not self.selected_device_id:
            # If no device is selected, open the wizard to select a device
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'device.selection.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_selected_device_id': self.selected_device_id.id if self.selected_device_id else False,
                    'active_id': self.id,  # Pass the current stock move ID to the wizard
                }
            }

        # If a device is already selected, fetch data and print
        fetch_result = self.fetch_and_update_scale_data()
        if fetch_result:
            return fetch_result

        # Proceed with printing the report
        report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
        if report_action:
            return report_action.report_action(self)
        else:
            raise UserError(_("Report action not found."))
        
    def action_force_empty_print(self):
        """
        Force printing with empty data.
        """
        self.write({'external_weight': '', 'external_unit': ''})
        # Trigger the report printing with empty data
        report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
        if report_action:
            return report_action.report_action(self)
        else:
            raise UserError(_("Report action not found."))

