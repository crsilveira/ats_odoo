# -*- coding: utf-8 -*-

import odoorpc
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# Odoo Origem
od1 = odoorpc.ODOO('localhost', port=9069)
# Check available databases
print(od1.db.list())
# Login
od1.login('16_xxx', 'admin', 'xxxxxx')

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

u2 = od2.env['res.users']
u1 = od1.env['res.users']
conta = 0
if 'res.users' in od1.env:
    uc2 = {}
    uc1_ids = u1.search([])
    for uc1 in u1.browse(uc1_ids):
        uc2_ids = u2.search([('login', '=', uc1.login)])
        if uc2_ids:
           continue
        conta += 1
        print uc1.name
        uc2['name'] = uc1.name
        uc2['login'] = uc1.login
        uc2['customer'] = False
        u2.create(uc2)


p2 = od2.env['res.partner']
p1 = od1.env['res.partner']
c2 = od2.env['res.company']
conta = 0
if 'res.partner' in od1.env:
    pc1_ids = p1.search([], limit=50)
    for pc1 in p1.browse(pc1_ids):
        pc2_ids = p2.search([('name', '=', pc1.name.strip())], limit=50)
        pc2 = {}
        """
        if pc2_ids:
            if pc1.property_product_pricelist.id == 3:
                pc2['property_product_pricelist'] = 2
            if pc1.property_product_pricelist.id == 5:
                pc2['property_product_pricelist'] = 3
            if pc1.property_product_pricelist.id == 1:
                pc2['property_product_pricelist'] = 1
            pc2['property_account_position_id'] = 1
            p2.write(pc2_ids,pc2) 
            print 'editando .. %s' %(pc1.name)
            continue
        """
        conta += 1
        print pc1.name
        if pc1.parent_id:
            parent_ids = p2.search([('name', '=', pc1.parent_id.name.strip())])
            if parent_ids:
                pc2['parent_id'] = parent_ids[0]
            else:
                continue
        if pc1.company_id:
            c2_id = c2.search([('name', '=', pc1.company_id.name)])
            if c2_id:
                pc2['company_id'] = c2_id[0]
        tipo_emp = 'person'
        if pc1.is_company:
           tipo_emp = 'company'
           pc2['is_company'] = True
        pc2['company_type'] = tipo_emp
        if pc1.ref:
            pc2['ref'] = pc1.ref
        pc2['name'] = u'%s' %(pc1.name.strip())
        if pc1.comment:
            pc2['comment'] = u'%s' %(pc1.comment.strip())
        if pc1.street:
            pc2['street'] = u'%s' %(pc1.street.strip())
        if pc1.street2:
            pc2['street2'] = u'%s' %(pc1.street2.strip())
        pc2['zip'] = pc1.zip
        if pc1.l10n_br_city_id:
            state = od2.env['res.country.state']
            state_id = state.search([
                ('ibge_code','=',pc1.l10n_br_city_id.state_id.ibge_code)
            ])
            city = od2.env['res.state.city']
            city_ids = city.search([
                ('ibge_code', '=', pc1.l10n_br_city_id.ibge_code),
                ('state_id', '=',state_id[0])
            ])
            for cty in city.browse(city_ids):
                pc2['city_id'] = cty.id
                pc2['state_id'] = cty.state_id.id
                pc2['country_id'] = cty.state_id.country_id.id
        if pc1.district:
            pc2['district'] = u'%s' %(pc1.district.strip())
        if pc1.phone:
            pc2['phone'] = pc1.phone.strip()
        if pc1.mobile:
            pc2['mobile'] = pc1.mobile.strip()

        #ver lista de precos
        #if pc1.property_product_pricelist.id == 1:
        #    pc2['property_product_pricelist'] = 1

        #pc2['property_payment_term'] = pc1.property_payment_term
        ##cli_odoo['customer_payment_mode'] = localpagto
        #pc2['property_account_position_id'] = 1
        if pc1.user_id:
            user = od2.env['res.users']
            user_ids = user.search([('name', '=', pc1.user_id.name)])
            for usr in user.browse(user_ids):
                pc2['user_id'] = usr.id
        pc2['customer'] = False
        if pc1.customer:
            pc2['customer'] = True
        if pc1.supplier:
            pc2['supplier'] = True
        if pc1.inscr_est:
            pc2['inscr_est'] = pc1.inscr_est.strip()
        if pc1.cnpj_cpf:
            pc2['cnpj_cpf'] = pc1.cnpj_cpf.strip()
        if pc1.email:
            pc2['email'] = pc1.email
        pc2['number'] = pc1.number
        if pc1.legal_name:
            pc2['legal_name'] = u'%s' %(pc1.legal_name.strip())
        p2.create(pc2)

print 'Total de Contratos : %s' %(str(conta))
