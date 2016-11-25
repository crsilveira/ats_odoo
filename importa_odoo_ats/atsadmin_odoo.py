# -*- encoding: utf-8 -*-

import fdb
import odoorpc
from datetime import datetime
from datetime import date
from datetime import timedelta

# CONEXAO ATS-ADMIN
con = fdb.connect(dsn='Servidor-PC/4050:C:\\Home\\sisadmin\\BD\\sge_nativa.fdb', user='sysdba', password='masterkey',charset='UTF8')
#con = fdb.connect(dsn='192.168.6.100:/home/publico/bd/sge_nativa.fdb', user='sysdba', password='masterkey',charset='UTF8')
# Abre conexao com o banco :
cur = con.cursor()

#CONEXAO ODOO
# Prepare the connection to the server
odoo = odoorpc.ODOO('localhost', port=48069)
# Login
odoo.login('bd', 'admin', '123')


order = odoo.env['pos.order']
hj = datetime.now()
hj = hj - timedelta(days=30)
hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')
######## IMPORTAR CLIENTES
def clientes(cliente_id):
    cliente = odoo.env['res.partner']
    if cliente_id == 0:
        cli_ids = cliente.search([('create_date', '>=', hj), ('customer','=', True)])
    else:
        cli_ids = cliente_id
    for partner_id in cliente.browse(cli_ids):
        if cliente_id == 0:
            sqlc = 'select codcliente from clientes where codcliente = %s' %(partner_id.id)
            cur.execute(sqlc)
            cli = cur.fetchall()
        else:
            cli = None
        if not len(cli):
           tipo = '0'
           if partner_id.is_company:
               tipo = '1'
           vendedor = '1'
           if partner_id.user_id.id:
               vendedor = str(partner_id.user_id.id)
           ie = ''
           if partner_id.inscr_est:
               ie = partner_id.inscr_est
           fiscal = 'J'
           if partner_id.property_account_position:
               fiscal = partner_id.property_account_position.note
           insere = 'insert into clientes (\
                        CODCLIENTE, NOMECLIENTE, RAZAOSOCIAL,\
                        TIPOFIRMA,CNPJ, INSCESTADUAL,\
                        SEGMENTO, REGIAO, LIMITECREDITO,\
                        DATACADASTRO, CODUSUARIO, STATUS, CODBANCO, CODFISCAL)\
                        values (%s, \'%s\', \'%s\',\
                        %s, \'%s\',\'%s\',\
                        %s, %s, %s,\
                        %s, %s, %s, %s, \'%s\')'\
                        %(str(partner_id.id), partner_id.name, partner_id.legal_name, \
                        tipo, partner_id.cnpj_cpf, ie,\
                        '1', '0', '0.0',\
                        'current_date', vendedor, '1', '1', fiscal)
           print(partner_id.name)
           cur.execute(insere)
           con.commit()
           fone = 'Null'
           ddd = 'Null'
           if partner_id.phone:
               fone = '''%s''' %(partner_id.phone[4:])
               ddd = '''%s''' %(partner_id.phone[1:3])
           fone1 = 'Null'
           ddd1 = 'Null'
           if partner_id.mobile:
               fone1 = '''%s''' %(partner_id.mobile[4:])
               ddd1 = partner_id.mobile[1:3]
           fone2 = 'Null'
           ddd2 = 'Null'
           if partner_id.fax:
               fone2 = partner_id.fax[4:]
               ddd2 = partner_id.fax[1:3]
           #buscar Cidade/UF/Pais
           cidade = 'Null'
           ibge = 'Null'
           uf = 'Null'
           pais = 'Null'
           if partner_id.l10n_br_city_id:
               cidade = partner_id.l10n_br_city_id.name[:39]
               ibge = '%s%s-%s' %(partner_id.l10n_br_city_id.state_id.ibge_code, \
                                  partner_id.l10n_br_city_id.ibge_code[:4], \
                                  partner_id.l10n_br_city_id.ibge_code[4:])
               uf = partner_id.l10n_br_city_id.state_id.code
               pais = partner_id.l10n_br_city_id.state_id.country_id.name
           endereco = 'Null'
           if partner_id.street:
               endereco = partner_id.street[:49]
           bairro = 'Null'
           if partner_id.district:
               bairro = partner_id.district[:29]
           complemento = 'Null'
           if partner_id.street2:
               complemento = partner_id.street2[:29]
           cep = 'Null'
           if partner_id.zip:
               cep = '%s-%s' %(partner_id.zip[:5], \
                               partner_id.zip[5:])
               cep = cep[:10]
           email = 'Null'
           if partner_id.email:
               email = partner_id.email[:255]
           obs = 'Null'
           if partner_id.comment:
               obs = partner_id.comment[:199]
           numero = 'Null'
           if partner_id.number:
               numero = partner_id.number[:5]
           inserir = 'INSERT INTO ENDERECOCLIENTE (CODENDERECO, \
                      CODCLIENTE, LOGRADOURO, BAIRRO, COMPLEMENTO,\
                      CIDADE, UF, CEP, TELEFONE, TELEFONE1, TELEFONE2,\
                      E_MAIL, TIPOEND,\
                      DADOSADICIONAIS, DDD, DDD1, DDD2,\
                      NUMERO, CD_IBGE, PAIS) VALUES ('
           inserir += str(partner_id.id)
           inserir += ',' + str(partner_id.id)
           if endereco != 'Null':
               inserir += ', \'%s\'' %(endereco)
           else:
               inserir += ', Null'
           if bairro != 'Null':
               inserir += ', \'%s\'' % (bairro)
           else:
               inserir += ', Null'
           if complemento != 'Null':
               inserir += ', \'%s\'' % (complemento)
           else:
               inserir += ', Null'
           if cidade != 'Null':
               inserir += ', \'%s\'' % (cidade)
           else:
               inserir += ', Null'
           if uf != 'Null':
               inserir += ', \'%s\'' % (uf)
           else:
               inserir += ', Null'
           if cep != 'Null':
               inserir += ', \'%s\'' % (cep)
           else:
               inserir += ', Null'
           if fone != 'Null':
               inserir += ', \'%s\'' % (fone)
           else:
               inserir += ', Null'
           if fone1 != 'Null':
               inserir += ', \'%s\'' % (fone1)
           else:
               inserir += ', Null'
           if fone2 != 'Null':
               inserir += ', \'%s\'' % (fone2)
           else:
               inserir += ', Null'
           if email != 'Null':
               inserir += ', \'%s\'' % (email)
           else:
               inserir += ', Null'
           inserir += ', 0' # tipoEnd
           if obs != 'Null':
               inserir += ', \'%s\'' % (obs)
           else:
               inserir += ', Null'
           if ddd != 'Null':
               inserir += ', \'%s\'' % (ddd)
           else:
               inserir += ', Null'
           if ddd1 != 'Null':
               inserir += ', \'%s\'' % (ddd1)
           else:
               inserir += ', Null'
           if ddd2 != 'Null':
               inserir += ', \'%s\'' % (ddd2)
           else:
               inserir += ', Null'
           if numero != 'Null':
               inserir += ', \'%s\'' % (numero)
           else:
               inserir += ', Null'
           if ibge != 'Null':
               inserir += ', \'%s\'' % (ibge)
           else:
               inserir += ', Null'
           if pais != 'Null':
               inserir += ', \'%s\');' % (pais)
           else:
               inserir += ', Null);'
           print(partner_id.street)
           cur.execute(inserir)
           con.commit()

######## IMPORTAR PRODUTOS
def produtos(prod_id):
    # vendo se a categoria está cadastrada
    grupo = odoo.env['pos.category']
    grupo_ids = grupo.search([('create_date', '>=', hj),('parent_id','!=', False)])
    for grp in grupo.browse(grupo_ids):
        sqlp = 'SELECT a.COD_CATEGORIA, a.COD_FAMILIA FROM CATEGORIAPRODUTO a where a.COD_CATEGORIA = %s' %(grp.id)
        cur.execute(sqlp)
        grps = cur.fetchall()
        if not len(grps):
            # procura a familia
            sqlp = 'SELECT a.COD_FAMILIA FROM FAMILIAPRODUTOS a where a.cod_Familia = %s' %(grp.parent_id.id)
            cur.execute(sqlp)
            frps = cur.fetchall()
            if not len(frps):
                insere = 'INSERT INTO FAMILIAPRODUTOS (DESCFAMILIA, COD_FAMILIA) VALUES (\'%s\',%s)'\
                    %(grp.parent_id.name, grp.parent_id.id)
                cur.execute(insere)
                con.commit()

            insere = 'INSERT INTO CATEGORIAPRODUTO (DESCCATEGORIA, COD_CATEGORIA, COD_FAMILIA) VALUES (\
                     \'%s\',%s, %s);' %(grp.name, grp.id, grp.parent_id.id)
            cur.execute(insere)
            con.commit()

    produto = odoo.env['product.product']
    if prod_id == 0:
        prod_ids = produto.search([('create_date', '>=', hj)])
    else:
        prod_ids = prod_id
    for product_id in produto.browse(prod_ids):
        if prod_id == 0:
            sqlp = 'select codproduto from produtos where codproduto = %s' %(product_id.id)
            cur.execute(sqlp)
            prods = cur.fetchall()
        else:
            prods = None
        if not len(prods):
            #import pudb;pu.db
            print (product_id.name)
            cat = ''
            if product_id.pos_categ_id:
                cat = product_id.pos_categ_id.name
            fam = ''
            if product_id.pos_categ_id.parent_id:
                fam = product_id.pos_categ_id.parent_id.name
            ncm = ''
            if product_id.description:
                ncm = product_id.description[:8]
            p_custo = 0.0
            if product_id.standard_price:
                p_custo = product_id.standard_price
            p_venda = 0.0
            if product_id.list_price:
                p_venda = product_id.list_price
            codp = str(product_id.id)
            if product_id.default_code:
                codp = product_id.default_code
            insere = 'INSERT INTO PRODUTOS (CODPRODUTO, UNIDADEMEDIDA, PRODUTO, PRECOMEDIO, CODPRO,\
                      TIPOPRECOVENDA, ORIGEM, NCM, VALORUNITARIOATUAL, VALOR_PRAZO'
            if fam:
                insere += ', FAMILIA'
            if cat:
                insere += ', CATEGORIA'
            insere += ') VALUES ('
            insere += str(product_id.id) + ', \'' + product_id.uom_id.name + '\''
            insere += ', \'' + product_id.name + '\''
            insere += ',' + str(p_custo) + ', ' + codp + ', \'F\', \'0\''
            insere += ',\'' + ncm + '\',' + str(p_custo) + ', ' + str(p_venda)
             #%s, \'%s\', \'%s\', %s, \'%s\',\
             #         \'%s\', \'%s\', \'%s\', %s, %s, \'%s\', \'%s\')'\
             #         %(str(product_id.id), product_id.uom_id.name, product_id.name, str(p_custo), codp, 'F', '0', \
             #         ncm , str(p_custo), str(p_venda)
             #         , fam, cat)
            if fam:
                insere += ', \'' + fam + '\''
            if cat:
                insere += ', \'' + cat + '\''
            insere += ')'
            print (codp+'-'+product_id.name)
            # print ' Cadastrando : %s - %s' % (str(row[0]), row[1])
            cur.execute(insere)
            con.commit()

clientes(0)
produtos(0)
######## IMPORTAR PEDIDOS
if 'pos.order' in odoo.env:
    order_ids = order.search([('date_order', '>=', hj)])
    for order in order.browse(order_ids):
        sql = 'select codMovimento from movimento where controle = \'%s\'' %(order.name)
        cur.execute(sql)
        rows = cur.fetchall()
        if not len(rows):
            sqlc = 'select codcliente from clientes where codcliente = %s' %(order.partner_id.id) 
            cur.execute(sqlc)
            cli = cur.fetchall()
            if not len(cli):
                clientes(order.partner_id)
            # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  CENTRO CUSTO
            ccusto = 51
            if order.session_id.config_id.id == 1:
                # Minas Gerais
                ccusto = 107
            if order.session_id.config_id.id == 4:
                # Rio de Janeiro
                ccusto = 108
            #if order.session_id.config_id.id != 1:
            #    import pudb;pu.db

            data_t = order.date_order
            data_t = str(data_t.month).zfill(2) + '/' + str(data_t.day).zfill(2) + '/' + str(data_t.year)
            data_t = datetime.strptime(data_t,'%m/%d/%Y').date()
            insere = 'INSERT INTO MOVIMENTO (CODMOVIMENTO, DATAMOVIMENTO, CODCLIENTE, '\
                'CODNATUREZA, STATUS, CODUSUARIO, CODVENDEDOR, CONTROLE, CODALMOXARIFADO) \
                VALUES (%s, \'%s\', %s, %s, %s, %s, %s, \'%s\', %s)'\
                % (order.id, str(data_t), order.partner_id.id, 3, 0, order.user_id.id \
                   ,order.user_id.id, order.name, ccusto)
            cur.execute(insere)
            con.commit()
            # procura pelos produtos, se estão cadastrados
            for linha in order.lines: 
                sqlp = 'select codproduto from produtos where codproduto = %s' %(linha.product_id.id)
                cur.execute(sqlp)
                prods = cur.fetchall()
                if not len(prods):
                    produtos(linha.product_id)
                sqld = 'select coddetalhe from movimentodetalhe where coddetalhe = %s' %(linha.id)
                cur.execute(sqld)
                dets = cur.fetchall()
                if not len(dets):
                    insere = 'INSERT INTO MOVIMENTODETALHE (CODDETALHE, CODMOVIMENTO, '\
                        'CODPRODUTO, QUANTIDADE, PRECO, DESCPRODUTO, CFOP) \
                        VALUES (%s, %s, %s, %s, %s, \'%s\', \'%s\')'\
                        % (linha.id, order.id, linha.product_id.id, linha.qty, \
                           linha.price_unit, linha.product_id.name, '5102')
                    cur.execute(insere)
                    con.commit()
            print(order.name)

