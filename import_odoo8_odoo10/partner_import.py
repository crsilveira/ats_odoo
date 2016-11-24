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

P2 = od2.env['res.partner']
odoo_cliente = odoo.env['res.partner']
odoo_city = odoo.env['l10n_br_base.city']
odoo_pagto = odoo.env['account.payment.term']
odoo_localpagto = odoo.env['payment.mode']

if 'res.partner' in od1.env:
   pc2 = {}
    cli_odoo['company_id'] = 3
    cli_odoo['ref'] = str(row[0])
    cli_odoo['name'] = cliente
    cli_odoo['titular'] = True
    cli_odoo['grupo'] = row[4]
    cli_odoo['inscricao'] = row[5]
    cli_odoo['comment'] = obs
    cli_odoo['street'] = endereco
    cli_odoo['street2'] = complemento
    cli_odoo['zip'] = str(row[13])
    cli_odoo['l10n_br_city_id'] = city.id
    cli_odoo['state_id'] = city.state_id.id
    cli_odoo['district'] = str(bairr)
    cli_odoo['phone'] = str(fone)
    cli_odoo['mobile'] = str(row[17])
    cli_odoo['naturalidade'] = str(row[20])
    cli_odoo['property_payment_term'] = pagto
    cli_odoo['customer_payment_mode'] = localpagto
    cli_odoo['property_account_position'] = 1
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
