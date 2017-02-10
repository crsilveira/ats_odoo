from fixed_files import Fixed_files

ff = Fixed_files('record', dic=False, checklength=False)
records = open('febraban.txt').readlines()
rec_in = []
for record in records:
    if record[0] == '0':
        rec_in.append(ff.parse(record))

for n, r in enumerate(rec_in):
    #print ff.unparse(r) == records[n]
    print r.data_emissao
    print r.data_vencimento
    print r.mes_referencia

#rec_in[0]


ff = Fixed_files('resumo', dic=False, checklength=False)
records = open('febraban.txt').readlines()
rec_in = []
for record in records:
    if record[0] == '1':
        rec_in.append(ff.parse(record))

for n, r in enumerate(rec_in):
    #print ff.unparse(r) == records[n]
    print r.data_emissao
    print r.identificador_recurso
    print r.mes_referencia
    print r.numero_recurso

#rec_in[0]

ff = Fixed_files('chamadas', dic=False, checklength=False)
records = open('febraban.txt').readlines()
rec_in = []
for record in records:
    if record[0] == '3':
        rec_in.append(ff.parse(record))

for n, r in enumerate(rec_in):
    #print ff.unparse(r) == records[n]
    str = 'Emissao : %s, Fone : %s, Mes: %s, Data : %s, Para Local: %s, ' \
          'Para Fone: %s, Duracao: %s, Horario: %s, Valor: %s' %(
        r.data_emissao,
        r.numero_recurso,
        r.mes_referencia,
        r.data_ligacao,
        r.localidade_destino,
        r.telefone_chamado,
        r.duracao,
        r.horario_ligacao,
        r.valor_ligacao_com_imp
    )

    print str


#rec_in[0]
