from odoo import models, fields, api

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
        if self.stock_move_id:
            self.stock_move_id.action_force_empty_print()
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        """
        Cancel the operation and close the wizard.
        """
        return {'type': 'ir.actions.act_window_close'}
