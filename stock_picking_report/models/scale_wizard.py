from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)  # Logger initialization

class ScaleConnectionWizard(models.TransientModel):
    _name = 'scale.connection.wizard'
    _description = 'Scale Connection Error Wizard'

    message = fields.Text(string="Message", readonly=True, default="The scale is not connected.")
    stock_move_id = fields.Many2one('stock.move', string="Stock Move", readonly=True)

    def action_print_empty(self):
        """
        Proceed with printing empty data.
        """
        self.ensure_one()
        _logger.info("action_print_empty called for record ID: %s", self.id)

        if self.stock_move_id:
            _logger.info("Calling action_force_empty_print on stock_move_id: %s", self.stock_move_id.id)
            self.stock_move_id.action_force_empty_print()
        else:
            _logger.warning("No stock_move_id set for this wizard.")

        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        """
        Cancel the operation and close the wizard.
        """
        _logger.info("action_cancel called for record ID: %s", self.id)
        return {'type': 'ir.actions.act_window_close'}
