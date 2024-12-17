from odoo import http
from odoo.http import request

class ScaleAPIController(http.Controller):

    @http.route('/live_scale', type='json', auth='public', methods=['GET'], website=True)
    def live_scale_data(self, **kwargs):
        """Expose scale data as an API endpoint"""
        scale_model = request.env['live.scale'].sudo()
        scale_model.fetch_scale_data()
        return {
            'weight': scale_model.weight,
            'unit': scale_model.unit
        }
