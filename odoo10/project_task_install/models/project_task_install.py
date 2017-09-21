# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class ProjectTaskInstall(models.Model):
    _name = 'project.task.install'
    _description = 'Tarefas de Instalaao'
    _inherits = {'project.task': 'task_id'}
    _date_name = "date_start"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_post_access = 'read'
    _order = "priority desc, sequence, date_start, name, id"

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id

    @api.multi
    @api.depends('total_hours','material_ids.price_unit', 'material_ids.quantity')
    def _compute_total(self):
        total = 0.0
        for line in self.material_ids:
            total += line.price_unit*line.quantity
        self.total_hours = total

    @api.model
    def default_get(self, field_list):
        """ Set 'date_assign' if user_id is set. """
        result = super(ProjectTaskInstall, self).default_get(field_list)
        if 'user_id' in result:
            result['date_assign'] = fields.Datetime.now()
        return result

    def _get_default_partner(self):
        if 'default_project_id' in self.env.context:
            default_project_id = self.env['project.project'].browse(self.env.context['default_project_id'])
            return default_project_id.exists().partner_id

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            self.partner_id = self.project_id.partner_id
            self.stage_id = self.stage_find(self.project_id.id, [('fold', '=', False)])
        else:
            self.partner_id = False
            self.stage_id = False


    int_msg = fields.Char(string="Mensagem interna")
    task_id = fields.Many2one('project.task', 'Project Task', required=True, ondelete="cascade", index=True, auto_join=True)
    code = fields.Char(
        string='Número OS', required=True, default="/", readonly=True)
    aux_line = fields.One2many('project.task.install.aux', 'task_id', 'Work done')
    material_ids = fields.One2many('project.task.install.materials', 'task_id', 'Materiais usados')
    vendor_id = fields.Many2one('res.users',string="Vendedor")
    ref = fields.Char(string="Referência do contrato")
    status_bar = fields.Selection([('waiting','Esperando liberação da entrega'),('approved','Liberado para entrega')],string="Status")
    amount_total = fields.Float(compute='_compute_total', digits=dp.get_precision('Account'), readonly=True, store=True)
    reviewer_id = fields.Many2one('res.users',
        string='Reviewer',
        index=True, track_visibility='always')

    _defaults = {
        'user_id': None,
    }

    _sql_constraints = [
        ('project_task_unique_code', 'UNIQUE (code)',
        'O Código da OS precisa ser único!')
    ]

    def release_for_delivery(self):
        picking = self.env['stock.picking'].search([('origin','=',self.ref)])
        if picking.request_statusbar == 'waiting':
            picking.request_statusbar = 'confirmed'
            self.status_bar = 'approved'
        return

    def create_sale_order(self):
        if self.ref:
            sale_obj = self.env['sale.order']
            ref_sale = self.env['sale.order'].search([('name','=',self.ref)])
            if ref_sale:
                id_qty = []
                for l in self.material_ids:
                    if l.product_id.id not in ref_sale.order_line.product_id.ids:
                        id_qty.append((l.product_id.id,l.quantity,l.price_unit))
                        continue
                    else:
                        for line in ref_sale.order_line:
                            if l.product_id.id == line.product_id.id:
                                if l.quantity > line.product_uom_qty:
                                    sum = l.quantity - line.product_uom_qty
                                    id_qty.append((l.product_id.id,sum,l.price_unit,l.product_id.uom_id.id))
                                    continue
                                else:
                                    continue
                if len(id_qty):
                    ol = []
                    for l in id_qty:
                        ol.append(
                            (0,0,{
                                'product_id':l[0],
                                'product_uom_qty':l[1],
                                'price_unit':l[2],
                                'product_uom':l[3]
                            }))
                    vals = {}
                    vals['order_line'] = ol
                    vals['partner_id'] = self.partner_id.id
                    sale_obj.create(vals)
                    return

        else:
            sale_obj = self.env['sale.order']
            ol = []
            vals = {}
            vals['partner_id'] = self.partner_id.id
            for line in self.material_ids:
               ol.append((0,0,{
                   'product_id' : line.product_id.id,
                   'product_uom_qty': line.quantity,
                   'price_unit' : line.price_unit,
                   'product_uom' : line.product_id.uom_id.id
               }))
            vals['order_line'] = ol
            sale_obj.create(vals)
            return

    @api.onchange('partner_id')
    def busca_projetos(self):
        value = {}
        if self.partner_id:
            project = self.env['project.project'].search([('partner_id', '=', self.partner_id.id)])
            for proj in project:
                value['project_id'] = proj.id
        return value

    #def onchange_remaining(self, cr, uid, ids, remaining=0.0, planned=0.0):
    #    if remaining and not planned:
    #        return {'value': {'planned_hours': remaining}}
    #    return {}

    #def onchange_planned(self, cr, uid, ids, planned=0.0, effective=0.0):
    #    return {'value': {'remaining_hours': planned - effective}}

    def next_stage(self):
        stage_id = int(self.stage_id.id) + 1
        self.stage_id = self.env['project.task.type'].browse(stage_id)

    def previous_stage(self):
        stage_id = int(self.stage_id.id) - 1
        self.stage_id = self.env['project.task.type'].browse(stage_id)

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('project.task.install')
            if not vals['code']:
                raise UserError(_("Crie a Sequência('project.task.install') de Numeração para a OS."))
            vals['name'] = vals['code']
        if not vals.get('stage_id'):
            vals['stage_id'] = 6
        return super(ProjectTaskInstall, self).create(vals)

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].next_by_code('project.task.install')
        return super(ProjectTaskInstall, self).copy(default)

class ProjectTaskInstallAux(models.Model):
    _name = 'project.task.install.aux'
    _description = 'Os Auxiliar'

    user_id = fields.Many2one('res.users', 'Auxiliar', index=True)
    task_id = fields.Many2one('project.task.install', 'Task', ondelete='cascade', required=True, index=True)

class ProjectTaskInstallMaterials(models.Model):
    _name = 'project.task.install.materials'
    _description = 'Materiais Instalação'

    @api.depends('price_unit', 'quantity')
    def _compute_subtotal(self):
        #for record in self:
        self.price_subtotal = self.price_unit * self.quantity

    @api.depends('product_id')
    def _compute_stock(self):
        self.stock = self.product_id.qty_available

    task_id = fields.Many2one('project.task.install', 'Task', ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Float('Quantity')
    price_unit = fields.Float('Unit Price', required=True, digits= dp.get_precision('Product Price'))
    price_subtotal = fields.Float(compute='_compute_subtotal',readonly=True, store=True)
    discount = fields.Float('Discount (%)', digits= dp.get_precision('Discount'))
    stock = fields.Float(readonly=True, compute='_compute_stock', store=True)

    defaults = {
        'discount': 0.0,
        'quantity': 1,
        'price_unit': 0.0,
    }
