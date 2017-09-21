# -*- coding: utf-8 -*-
# © 2014-2015 Avanzosc
# © 2014-2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    real_cost = fields.Float("Custo Total")
    unit_real_cost = fields.Float("Custo Unitário")

    @api.multi
    def _generate_moves(self):
        #TODO
        #Pegando custo correto somente de PRODUTOS
        # adicionar custo de servicos ???!!!!       
        #import pudb;pu.db
        for production in self:
            #20/09/17 - Carlos: original linha abaixo comentada  
            stock = production._generate_finished_moves()
            #production._generate_finished_moves()
            factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
            production._generate_raw_moves(lines)
            #20/09/17 - Carlos acrescentei a busca abaixo
            # para pegar o custo do produto
            cost = 0.0
            for bom_line, line_data in lines:
                #TODO arrumar location_id para locais internos
                prods = self.env['stock.quant'].search([('product_id', '=', bom_line.product_id.id), ('location_id', '=', 15)])
                qt = line_data['qty']
                for prod in prods:
                    if prod.qty >= qt:
                        cost += (prod.inventory_value/prod.qty) * qt
                        break
                    else:
                        if qt > prod.qty:
                            qtde = prod.qty
                        else:
                            qtde = qt
                        cost += (prod.inventory_value/prod.qty) * (qtde)
                        qt -= qtde
            if cost > 0.0:
                self.real_cost = cost
                cost = cost / production.product_qty
                self.unit_real_cost = cost
                stock.write({'price_unit':cost})
            # ate aqui
            #
            # Check for all draft moves whether they are mto or not
            self._adjust_procure_method()
            self.move_raw_ids.action_confirm()
        return True
