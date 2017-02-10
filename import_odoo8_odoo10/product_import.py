import odoorpc

# Odoo Origem
od1 = odoorpc.ODOO('localhost', port=9069)
# Check available databases
print(od1.db.list())
# Login
od1.login('16_xxxxxx', 'admin', 'xxxxxx')

# Odoo Destino
od2 = odoorpc.ODOO('localhost', port=8069)
# Check available databases
print(od2.db.list())
# Login
od2.login('17_xxxxxx', 'admin', '123')

# Current user
user = od2.env.user
print(user.name)            # name of the user connected
print(user.company_id.name) # the name of its company
# CATEGORIAS
if 'product.category' in od2.env:
    pcat2 = od2.env['product.category']
"""
# Sem Categoria Pai
conta = 0
if 'product.category' in od1.env:
    pc1 = od1.env['product.category']
    pc1_ids = pc1.search([('parent_id','=',False)])
    for p in pc1.browse(pc1_ids):
        if p.parent_id:
            continue
        print p.name
        pcat2_ids = pcat2.search([('name','=',p.name)])
        if pcat2_ids:
            continue
        p2 = {}
        p2['name'] = p.name
        conta += 1
        pcat2.create(p2)
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
        pcat2_ids = pcat2.search([('name','=',p.name)])
        if pcat2_ids:
            continue
        p2 = {}
        p2['name'] = p.name
        if p.parent_id:
            pcat2_ids = pcat2.search([('name', '=', p.parent_id.name)])
            if pcat2_ids:
                for cat in pcat2.browse(pcat2_ids):
                    p2['parent_id'] = cat.id
        conta += 1
        pcat2.create(p2)
print 'Total de Sub-Categoria : %s' % (str(conta))

import pudb;pu.db
"""
# CATEGORIAS POS
if 'pos.category' in od2.env:
    poscat2 = od2.env['pos.category']
"""    
# Sem Categoria Pai
conta = 0
if 'pos.category' in od1.env:
    pc1 = od1.env['pos.category']
    pc1_ids = pc1.search([('parent_id','=',False)])
    for p in pc1.browse(pc1_ids):
        if p.parent_id:
            continue
        print p.name
        poscat2_ids = poscat2.search([('name','=',p.name)])
        if poscat2_ids:
            continue
        p2 = {}
        p2['name'] = p.name
        conta += 1
        poscat2.create(p2)
print 'Total POS de Categoria Principal : %s' %(str(conta))

#Com Categoria Pai
conta = 0
if 'pos.category' in od1.env:
    pc1 = od1.env['pos.category']
    pc1_ids = pc1.search([('parent_id','!=',False)])
    for p in pc1.browse(pc1_ids):
        if not p.parent_id:
            continue
        print p.name
        poscat2_ids = poscat2.search([('name','=',p.name)])
        if poscat2_ids:
            continue
        p2 = {}
        p2['name'] = p.name
        if p.parent_id:
            poscat2_ids = poscat2.search([('name', '=', p.parent_id.name)])
            if poscat2_ids:
                for cat in poscat2.browse(poscat2_ids):
                    p2['parent_id'] = cat.id
        conta += 1
        poscat2.create(p2)
print 'Total de Sub-Categoria : %s' % (str(conta))
"""
# PRODUTOS
if 'product.product' in od2.env:
    op2 = od2.env['product.product']

conta = 0
conta_erro = 0
if 'product.product' in od1.env:
    p1 = od1.env['product.product']
    #p_ids = p1.search([('name','ilike','tenis')])
    #p_ids = p1.search([], limit=10000, offset=6000)
    p_ids = p1.search([])
    #p_ids = p1.search([('default_code','like','02%')])
    #import pudb;pu.db
    for p in p1.browse(p_ids):
        pc2_ids = op2.search([('name', '=', p.name)])
        pp2 = {}
        if pc2_ids:
            #pp2['name'] = p.name
            if p.categ_id:
                pcat2_ids = pcat2.search([('name','=',p.categ_id.name)])
                for cat in pcat2.browse(pcat2_ids):
                    pp2['categ_id'] = cat.id
                    pp2['weight'] = p.weight
                    pp2['volume'] = p.volume
                    op2.write(pc2_ids,pp2) 
            print 'Editando %s' %(p.name)

            continue
        print 'Produto %s-%s' %(str(p.id),p.product_tmpl_id.name)
        pp2['name'] = p.name
        pp2['sale_ok'] = p.product_tmpl_id.sale_ok
        #pp2['purchase_ok'] = p.product_tmpl_id.purchase_ok
        pp2['type'] = p.product_tmpl_id.type
        pp2['default_code'] = p.default_code
        if p.ean13:
            pp2['barcode'] = p.product_tmpl_id.ean13
        pp2['list_price'] = p.product_tmpl_id.list_price
        pp2['standard_price'] = p.product_tmpl_id.standard_price
        if p.categ_id:
            pcat2_ids = pcat2.search([('name','=',p.categ_id.name)])
            for cat in pcat2.browse(pcat2_ids):
                pp2['categ.id'] = cat.id
        #if p.pos_categ_id:
        #    poscat2_ids = poscat2.search([('name','=',p.pos_categ_id.name)])
        #    for cat in poscat2.browse(poscat2_ids):
        #        pp2['pos_categ.id'] = cat.id
        #if p.fiscal_type:
        #    pp2['fiscal_type'] = p.fiscal_type
        if p.uom_id:
            pp2['uom_id'] = p.uom_id.id
        #if p.grupo:
        #    pp2['grupo'] = p.grupo
        #pp2[''] = p.uom_po_id
        #pp2[''] = p.
        #pp2[''] = p.
        #pp2[''] = p.
        #if p.fiscal_classification_id:
        #if p.ncm_id:
        try:
            op2.create(pp2)
        except:
            conta_erro += 1
            continue
        conta += 1
print 'Total de Produtos : %s, errados %s' % (str(conta), str(conta_erro))
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
