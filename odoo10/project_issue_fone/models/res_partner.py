 #-*- coding: utf-8 -*-
import re

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    """
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        args = args or []
        if name:
            ids = self.search(cr, uid, [('pronuncia', '=', name)] + args, limit=limit, context=context or {})
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context or {})
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context or {})
        return self.name_get(cr, uid, ids, context or {})
    """

    fornece_fone = fields.Boolean(string='Fornec. Telefone ?', help="Pode fornecer telefone do cliente caso solicitado." )
    fornece_email = fields.Boolean(string='Fornec. Email ?', help="Pode fornecer email do cliente caso solicitado.")
    fornece_endereco = fields.Boolean(string='Fornec. Endereço ?', help="Pode fornecer endereço do cliente caso solicitado.")
    birthdate_n = fields.Date(string='Date de nascimento')
    motivo_ausencia = fields.Char(string='Justificativa', size=256)
    transfer_recado = fields.Char(string='Tranferencia/Recado', size=128)
    razao_empresa = fields.Char(string='Razao-Empresa', size=128)
    ramal_softphone1 = fields.Char(string='Fone Redirec.', size=60)
    ramal_softphone2 = fields.Char(string='Email Redirec.', size=60)
    email_financeiro = fields.Text(string='Email Financeiro', help="Usado para cobrança. Mais de um email separar com Virgula")
    aviso_atendimento = fields.Char(string='Aviso Atendimento', size=164)
    pronuncia = fields.Char(string='Pronuncia', size=128)
    transferencia = fields.Boolean(string='Transferência')
    recado = fields.Boolean(string='Recado')


    @api.onchange('active') 
    def active_partner(self):
        if not self.active:
            for child in self.child_ids:
                child.write({'active': False })
        return {'value' : {}, }
