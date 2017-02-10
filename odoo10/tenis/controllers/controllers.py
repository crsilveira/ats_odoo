# -*- coding: utf-8 -*-
from odoo import http

class Tenis(http.Controller):
    @http.route('/tenis/tenis/', auth='public', website=True)
    def index(self, **kw):
        Rankings = http.request.env['tenis.ranking']
        return http.request.render('tenis.index', {
            'ranking': Rankings.search([])
        })


    @http.route('/tenis/ranking/', auth='public', website=True)
    def rkg(self, **kw):
        Rkgs = http.request.env['tenis.ranqueamento']
        return http.request.render('tenis.rkg', {
            'ranqueamento': Rkgs.search([])
        })

