# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Ranqueamento(models.Model):
    _name = 'tenis.ranqueamento'
    _rec_name = 'jogador_id'
    _order = 'rk'

    jogador_id = fields.Many2one(
        'res.partner', string='Jogador', required=True)
    rk = fields.Integer('Ranking')
    rk_anterior = fields.Integer('Ranking Anterior')
    ganhou_ultimo = fields.Boolean('Ganhou último Jogo')
    perdeu_ultimo = fields.Boolean('Perdeu último Jogo')
    tem_desafio = fields.Boolean('Tem Desafio')
    jogou_mes = fields.Boolean('Jogou no mes')
