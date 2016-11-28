 # -*- coding: utf-8 -*-

import odoorpc

# Odoo Origem
#od1 = odoorpc.ODOO('localhost', port=9069)

# Check available databases
print(od1.db.list())
# Login
#od1.login('db', 'admin', '123')


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

u2 = od2.env['res.users']
u1 = od1.env['res.users']
conta = 0
if 'res.users' in od1.env:
    uc2 = {}
    uc1_ids = u1.search([])
    for uc1 in u1.browse(uc1_ids):
        uc2_ids = u2.search([('name', '=', uc1.name)])
        if uc2_ids:
           continue
        conta += 1
        print uc1.name
        uc2['name'] = uc1.name
        uc2['login'] = uc1.login
        u2.create(uc2)


p2 = od2.env['res.partner']
p1 = od1.env['res.partner']
conta = 0
if 'res.partner' in od1.env:
    pc1_ids = p1.search([])
    for pc1 in p1.browse(pc1_ids):
        pc2_ids = p2.search([('name', '=', pc1.name)])
        if pc2_ids:
           continue
        pc2 = {}
        conta += 1
        print pc1.name
        #pc2['company_id'] =
        tipo_emp = 'person'
        if pc1.is_company:
           tipo_emp = 'company'
        pc2['company_type'] = tipo_emp
        pc2['ref'] = pc1.ref
        pc2['name'] = pc1.name
        if pc1.comment:
            pc2['comment'] = pc1.comment
        pc2['street'] = pc1.street
        if pc1.street2:
            pc2['street2'] = pc1.street2
        pc2['zip'] = pc1.zip
        if pc1.l10n_br_city_id:
            city = od2.env['res.state.city']
            city_ids = city.search([('ibge_code', '=', pc1.l10n_br_city_id.ibge_code)])
            for cty in city.browse(city_ids):
                pc2['city_id'] = cty.id
                pc2['state_id'] = cty.state_id.id
                pc2['country_id'] = cty.state_id.country_id.id
        if pc1.district:
            pc2['district'] = pc1.district
        if pc1.phone:
            pc2['phone'] = pc1.phone
        if pc1.mobile:
            pc2['mobile'] = pc1.mobile
        #pc2['property_payment_term'] = pc1.property_payment_term
        ##cli_odoo['customer_payment_mode'] = localpagto
        #cli_odoo['property_account_position'] = 1
        if pc1.user_id:
            user = od2.env['res.users']
            user_ids = user.search([('name', '=', pc1.name)])
            for usr in user.browse(user_ids):
                pc2['user_id'] = usr.id
        pc2['customer'] = pc1.customer
        pc2['supplier'] = pc1.supplier
        if pc1.inscr_est:
            pc2['inscr_est'] = pc1.inscr_est
        if pc1.cnpj_cpf:
            pc2['cnpj_cpf'] = pc1.cnpj_cpf
        if pc1.email:
            pc2['email'] = pc1.email
        pc2['number'] = pc1.number
        pc2['legal_name'] = pc1.legal_name
        p2.create(pc2)

print 'Total de Contratos : %s' %(str(conta))