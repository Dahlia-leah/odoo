from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)  # Logger initialization

class ScaleConnectionWizard(models.TransientModel):
    _name = 'scale.connection.wizard'
    _description = 'Scale Connection Error Wizard'

    message = fields.Text(string="Message", readonly=True, default="The scale is not connected.")

    def action_print_empty(self):
        """
        Proceed with printing empty data.
        """
        
        self.action_force_empty_print()
        

    def action_cancel(self):
        """
        Cancel the operation and close the wizard.
        """
        _logger.info("action_cancel called for record ID: %s", self.id)
        return {'type': 'ir.actions.act_window_close'}
