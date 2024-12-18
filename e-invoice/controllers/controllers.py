# -*- coding: utf-8 -*-
from odoo import http

class Einvoice(http.Controller):

    @http.route('/e-invoice', auth='public')
    def index(self):
        print('')
        return "Hello, world"

