import odoorpc

# Odoo Origem
od1 = odoorpc.ODOO('localhost', port=9069)
# Check available databases
print(od1.db.list())
# Login
od1.login('16_myplace4', 'admin', 'a2t00s7')

# Odoo Destino
od2 = odoorpc.ODOO('localhost', port=8069)
# Check available databases
print(od2.db.list())
# Login
od2.login('16_odoo10a', 'admin', '123')

# Current user
user = od2.env.user
print(user.name)            # name of the user connected
print(user.company_id.name) # the name of its company

# CATEGORIAS
if 'product.category' in od2.env:
    pc2 = od2.env['product.category']

# Sem Categoria Pai
conta = 0
if 'product.category' in od1.env:
    pc1 = od1.env['product.category']
    pc1_ids = pc1.search([('parent_id','=',False)])
    for p in pc1.browse(pc1_ids):
        if p.parent_id:
            continue
        print p.name
        pc2_ids = pc2.search([('name','=',p.name)])
        if pc2_ids:
            continue
        p2 = {}
        p2['name'] = p.name
        conta += 1
        pc2.create(p2)
print 'Total de Categoria Principal : %s' %(str(conta))

#Com Categoria Pai
conta = 0
if 'product.category' in od1.env:
    pc1 = od1.env['product.category']
    pc1_ids = pc1.search([('parent_id','!=',False)])
    for p in pc1.browse(pc1_ids):
        if not p.parent_id:
            continue
        print p.name
        pc2_ids = pc2.search([('name','=',p.name)])
        if pc2_ids:
            continue
        p2 = {}
        p2['name'] = p.name
        if p.parent_id:
            pc2_ids = pc2.search([('name', '=', p.parent_id.name)])
            if pc2_ids:
                for cat in pc2.browse(pc2_ids):
                    p2['parent_id'] = cat.id
        conta += 1
        pc2.create(p2)
print 'Total de Sub-Categoria : %s' % (str(conta))

# PRODUTOS
if 'product.product' in od2.env:
    op2 = od2.env['product.product']

conta = 0
if 'product.product' in od1.env:
    p1 = od1.env['product.product']
    p_ids = p1.search([])
    for p in p1.browse(p_ids):
        pp2 = {}
        print 'Produto %s-%s' %(str(p.id),p.product_tmpl_id.name)
        pp2['name'] = p.product_tmpl_id.name
        pp2['sale_ok'] = p.sale_ok
        pp2['purchase_ok'] = p.purchase_ok
        pp2['type'] = p.type
        pp2['default_code'] = p.default_code
        pp2['barcode'] = p.barcode
        pp2['list_price'] = p.list_price
        pp2['standard_price'] = p.standard_price
        pc2_ids = pc2.search([('name','=',p.categ_id.name)])
        for cat in pc2.browse(pc2_ids):
            pp2['categ.id'] = cat.id
        """
        pp2['fiscal_type'] = p.fiscal_type
        pp2['uom_id'] = p.uom_id.id
        pp2['grupo'] = p.grupo
        pp2[''] = p.uom_po_id
        pp2[''] = p.
        pp2[''] = p.
        pp2[''] = p.
        """

        if p.fiscal_classification_id:
        if p.ncm_id:

        conta += 1
print 'Total de Produtos : %s' % (str(conta))
# Simple 'raw' query
#user_data = od2.execute('res.users', 'read', [user.id])
#print(user_data)

# Use all methods of a model
"""
if 'sale.order' in od1.env:
    Order = od1.env['sale.order']
    order_ids = Order.search([])
    for order in Order.browse(order_ids):
        print(order.name)
        products = [line.product_id.name for line in order.order_line]
        print(products)
"""
# Update data through a record
#user.name = "Brian Jones"
