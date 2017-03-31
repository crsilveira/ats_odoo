# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time

from odoo.addons.br_boleto.boleto.document import Boleto

class ContractReajuste(models.Model):
    _name = "account.analytic.reajuste"

    reajuste_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    product_id = fields.Many2one('product.product','Produto')
    user_id = fields.Many2one('res.users','Usuário')
    name = fields.Date(u'Data Reajuste')
    valor_anterior = fields.Float(u'Valor Anterior')
    indice = fields.Float(u'Indice aplicado')


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    reajuste_ids = fields.One2many('account.analytic.reajuste', 'reajuste_id', 'Historico reajuste', copy=False)
    motivo_encerramento = fields.Selection([
            ('1003', '1003-Problemas Financeiros'),
            ('1004', '1004-Encerramento Atividades'),
            ('1005', '1005-Mudou-se de endereço'),
            ('1006', '1006-Foi pra concorrência melhor preço'),
            ('1007', '1007-Foi pra concorrência descontentamento'),
            ('1544', '1544-Problemas no orçamento'),
            ('2009', '2009-Entrega do imovel'),
            ('2010', '2010-Optou por ficar com o atendimento de uma única empresa'),
            ('2012', '2012-Por não ter serviço específico'),
            ('2411', '2411-Cancelado por Inadimplência'),
            ('2641', '2641-Cadastro em duplicidade'),
            ('2642', '2642-Falecimento'),
            ], 'Motivo de Encerramento', help="Motivo pelo qual o contrato foi finalizado.")
