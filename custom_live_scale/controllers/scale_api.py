from odoo import http
from odoo.http import request

class ScaleAPI(http.Controller):

    @http.route('/scale/get_live_weight', type='json', auth='user')
    def get_live_weight(self):
        """
        API endpoint to fetch live weight data.
        """
        scale = request.env['live.scale'].sudo()
        return scale.fetch_live_weight()
