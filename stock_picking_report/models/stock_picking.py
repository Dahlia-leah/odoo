import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    external_weight = fields.Char(string='External Weight', readonly=True)
    external_unit = fields.Char(string='External Unit', readonly=True)
    time_printing = fields.Datetime(string="Time Printing", default=fields.Datetime.now)

def fetch_and_update_scale_data(self):
    """
    Fetches scale data from an external source and updates stock move records.
    """
    self.ensure_one()

    device = self.env['devices.device'].search([('device_id', '=', '1')], limit=1)
    if not device:
        raise UserError(_("Device with device_id = 1 not found."))

    connection = self.env['devices.connection'].search([('device_id', '=', device.id)], limit=1)
    if not connection or connection.status != 'valid':
        raise UserError(_("The connection associated with device_id = 1 is invalid or not found."))

    try:
        headers = {
            'User-Agent': 'PostmanRuntime/7.30.0',
            'Accept': 'application/json',
        }
        _logger.info(f"Connecting to scale service at {connection.url}")
        response = requests.get(connection.url, headers=headers, timeout=10, verify=False)

        if response.status_code == 200:
            data = response.json()
            weight = data.get("weight", "")
            unit = data.get("unit", "")

            if not weight and not unit:
                self.env.user.notify_warning(
                    message=_("The scale service did not return weight or unit data. Proceeding without updating."),
                    title=_("Scale Data Warning"),
                    sticky=False
                )
            else:
                self.write({'external_weight': str(weight), 'external_unit': unit})
                _logger.info(f"Updated stock move with weight: {weight} and unit: {unit}")
                self.env.user.notify_success(
                    message=_("Successfully updated weight and unit from scale."),
                    title=_("Scale Data Updated"),
                    sticky=False
                )

        else:
            self.env.user.notify_warning(
                message=_("Failed to fetch scale data: HTTP %s. Proceeding without updating." % response.status_code),
                title=_("Scale Data Fetch Error"),
                sticky=False
            )

    except requests.exceptions.RequestException as e:
        self.env.user.notify_warning(
            message=_("Error connecting to the scale service: %s. Proceeding without updating." % str(e)),
            title=_("Scale Connection Error"),
            sticky=False
        )

    def action_print_report(self):
        """
        Trigger the printing of the report.
        Fetch and update scale data before printing.
        """
        warning = self.fetch_and_update_scale_data()

        if warning:
            return warning

        report_action = self.env.ref('stock_picking_report.action_report_stock_picking', raise_if_not_found=False)
        if report_action:
            return report_action.report_action(self)
        else:
            raise UserError(_("Report action not found."))
