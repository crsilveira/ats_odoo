# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Ranking(models.Model):
    _name = 'tenis.ranking'
    _order = 'data_desafio desc'

    name = fields.Char('Jogo', required=True)
    desafiante_id = fields.Many2one(
        'res.partner', string='Desafiante', required=True)
    desafiado_id = fields.Many2one(
        'res.partner', string='Desafiado', required=True)
    rk_desafiante = fields.Integer('Ranking Desafiante')
    rk_desafiado = fields.Integer('Ranking Desafiado')
    data_agendado = fields.Datetime('Data do Agendamento')
    jogo_data = fields.Date('Jogado em ')
    data_desafio = fields.Date('Data do Desafio', default=fields.Date.today())
    set1_dfte = fields.Integer('Set 1 - Desafiante', default=0)
    set1_dfdo = fields.Integer('Set 1 - Desafiado', default=0)
    set2_dfte = fields.Integer('Set 2 - Desafiante', default=0)
    set2_dfdo = fields.Integer('Set 2 - Desafiado', default=0)
    set3_dfte = fields.Integer('Set 3 - Desafiante', default=0)
    set3_dfdo = fields.Integer('Set 3 - Desafiado', default=0)
    placar = fields.Char(compute='_compute_placar', string='Placar', store=True) \

    @api.depends('set1_dfte', 'set2_dfte','set3_dfte','set1_dfdo','set2_dfdo','set3_dfdo')
    def _compute_placar(self):
        if self.set3_dfte or self.set3_dfdo:
            self.placar = '%sx%s, %sx%s, %sx%s' %(
                str(self.set1_dfte),
                str(self.set1_dfdo),
                str(self.set2_dfte),
                str(self.set2_dfdo),
                str(self.set3_dfte),
                str(self.set3_dfdo)
            )
        else:
            self.placar = '%sx%s, %sx%s' % (
                str(self.set1_dfte),
                str(self.set1_dfdo),
                str(self.set2_dfte),
                str(self.set2_dfdo)
            )

    @api.onchange('desafiante_id')
    def onchange_desafiante_id(self):
        if self.desafiado_id and self.desafiante_id:
            self.name = '%s X %s' %(self.desafiante_id.name, self.desafiado_id.name)

    @api.onchange('desafiado_id')
    def onchange_desafiado_id(self):
        if self.desafiado_id and self.desafiante_id:
            self.name = '%s X %s' % (self.desafiante_id.name, self.desafiado_id.name)

    def _busca_ranking(self, jogador):
        import pudb;pu.db
        rg = self.env['tenis.ranqueamento'].browse([jogador])
        if 'rk' in rg:
            return rg.rk
        return False

    @api.model 
    def create(self, vals):
        import pudb;pu.db
        if 'desafiante_id' in vals:
            vals['rk_desafiante'] = self._busca_ranking(vals['desafiante_id'])
        if 'desafiado_id' in vals:
            vals['rk_desafiado'] = self._busca_ranking(vals['desafiado_id'])
        return super(Ranking, self).create(vals)