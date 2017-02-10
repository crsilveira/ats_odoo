import odoorpc
import datetime

# Odoo Origem
od1 = odoorpc.ODOO('localhost', port=8069)
# Check available databases
print(od1.db.list())
# Login
od1.login('bd', 'admin', 'xxxx')

# Odoo Destino
od2 = odoorpc.ODOO('localhost', port=9069)
# Check available databases
print(od2.db.list())
# Login
od2.login('bd_novo', 'admin', 'xxxxx')

# Current user
user = od2.env.user
print(user.name)            # name of the user connected
print(user.company_id.name) # the name of its company

# Contratos
if 'account.analytic.account' in od2.env:
    pc2 = od2.env['account.analytic.account']

conta = 0
if 'account.analytic.account' in od1.env:
    pc1 = od1.env['account.analytic.account']
    pc1_ids = pc1.search([])
    for p in pc1.browse(pc1_ids):
        pc2_ids = pc2.search([('code','=',p.code)])
        if pc2_ids:
            continue
        print p.name
        p2 = {}

        #PEGRUNTAR PARA A CAMILA SE A DATA PROXIMA FATURA ESTA CORRETA

        p2['code'] = p.code
        p2['name'] = p.name
        dia_ini = p.date_start
        p2['date_start'] = '%s-%s-%s' %(dia_ini.year, dia_ini.month, dia_ini.day)
        partner = od2.env['res.partner']
        partner_ids = partner.search([('name', '=', p.partner_id.name)])
        for prt in partner.browse(partner_ids):
            p2['partner_id'] = prt.id
        if not partner_ids:
            print 'Cliente Nao LOCALIZADO: %s' %(prt.name)
            continue
        manager = od2.env['res.users']
        manager_ids = manager.search([('name', '=', p.manager_id.name)])
        for mng in manager.browse(manager_ids):
            p2['manager_id'] = mng.id
        if not manager_ids:
            print 'Gerente Nao LOCALIZADO: %s' %(p.manager_id.name)
            continue
        #p2['recurring_next_date'] = p.recurring_next_date
        p2['recurring_invoices'] = True
        c_id = pc2.create(p2)
        #p2[''] = p.
        #p2[''] = p.
        #p2[''] = p.
        #recurring_invoice_line_ids
        for ln in p.recurring_invoice_line_ids:
            linha = {}
            linha['analytic_account_id'] = c_id
            pdt = od2.env['product.product']
            pdt_ids = pdt.search([('default_code', '=', ln.product_id.default_code)])
            for pt in pdt.browse(pdt_ids):
                linha['product_id'] = pt.id
            if not pdt_ids:
                print 'Produto Nao LOCALIZADO: %s' %(ln.product_id.name)
                continue
            linha['price_unit'] = ln.price_unit
            linha['quantity'] = ln.quantity
            linha['name'] = ln.name
            linha['uom_id'] = 1
            lin = {'recurring_invoice_line_ids': [(0, 0, linha)]}
            #p2['recurring_invoice_line_ids'] = linha
            pc2.write(c_id,lin)
        conta += 1
print 'Total de Contratos : %s' %(str(conta))
