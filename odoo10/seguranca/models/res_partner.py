 #-*- coding: utf-8 -*-
import re

from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.exceptions import Warning
from openerp import tools

#import pdb


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cod_internal = fields.Char(string="Sigma")
    cod_service = fields.Char(string="Service")
    zoneamento = fields.Html(string="Zoneamento")

    @api.one
    @api.constrains('inscr_est')
    def _check_ie_duplicated(self):
        """ Check if the field inscr_est has duplicated value
        """
        """  13/11/2015 - Tem varios Cliente Duplicado
        if (not self.inscr_est or self.inscr_est == 'ISENTO'):
            return True
        partner_ids = self.search(
            ['&', ('inscr_est', '=', self.inscr_est), ('id', '!=', self.id)])

        if len(partner_ids) > 0:
            raise Warning(_(u'Já existe um parceiro cadastrado com'
                            u'esta Inscrição Estadual/RG!'))
        """
        return True

    #@api.multi
    #def write(self, vals):
    #    result = super(res_partner, self).write(vals)
    #    self.message_post(cr, uid, ids,
    #        body="has been <b>updated</b>.",
    #        subject="Record Updated",context=context)
    #    return result


