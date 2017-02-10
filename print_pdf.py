from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from febraban.fixed_files import Fixed_files
from reportlab.lib.pagesizes import A4, landscape as pagesize_landscape
import locale

#class ImprimirContaFone(object):
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
#	def resumo(self):
canvas = canvas.Canvas("form.pdf", pagesize=A4)
canvas.setLineWidth(.3)
canvas.setFont('Helvetica', 12)

ff = Fixed_files('resumo', dic=False, checklength=False)
records = open('febraban.txt').readlines()
rec_in = []
linha_cabecalho1 = 'Data       Hora            Origrm(UF)-Destino                 Numero            Duracao                             Valor '
linha_cabecalho2 = '--------------------------------------------------------------------------------------------------------------------------'
tamanho = 800
for record in records:
	if record[0] == '1':
		rec_in.append(ff.parse(record))
for n, r in enumerate(rec_in):
	#print ff.unparse(r) == records[n]
    fone = r.identificador_recurso.split()
    valor_plano = 49.91
    
    valor_p = locale.currency(valor_plano, grouping=True, symbol=None)
    if fone[0] == '12991051133':
		canvas.drawString(30,tamanho,'Detalhamento de Ligacoes e servicos do Celular %s' %(fone[0]))
		canvas.drawString(30,tamanho-15,'Mensalidade e Pacotes Promocionais')
		canvas.drawString(30,tamanho-30,'Descricao                                         Total (R$) ')
		canvas.drawString(30,tamanho-45,'Total                                                   R$ %s' %(str(valor_p)))
                canvas.drawString(30,tamanho-60,linha_cabecalho1)
                canvas.drawString(30,tamanho-70,linha_cabecalho2)
		#canvas.drawString(30,690,'Data       Hora            Origrm(UF)-Destino                 Numero            Duracao                             Valor ')
		#canvas.drawString(30,680,'--------------------------------------------------------------------------------------------------------------------------')


#	self.resumo()

ff = Fixed_files('chamadas', dic=False, checklength=False)
records = open('febraban.txt').readlines()
rec_in = []
for record in records:
    if record[0] == '3':
        rec_in.append(ff.parse(record))
	
j = tamanho
#import pudb;pu.db
for n, r in enumerate(rec_in):
    #print ff.unparse(r) == records[n]
    fone = r.numero_recurso.split()
    if fone[0] == '12991051133':
        dta = str(r.data_ligacao)
        dt = dta[6:8] + '/' + dta[4:6]
        drh = r.duracao/60
        drm = r.duracao%60
        dur = '00'
        if drh:
            dur = str(drh).zfill(2)
        if drm:
            dur = dur + ':' + str(drm).zfill(2)
        else:
            dur = dur + ':' + '00'

        dhl = str(r.horario_ligacao)
        dh = dhl[0:2] + ':' + dhl[2:4] + ':' + dhl[4:6] 
        dld = str(r.telefone_chamado)
        dd = dld[0:2] + '-' + dld[2:16] 
			
        str_t = 'Emissao : %s, Fone : %s, Mes: %s, Data : %s, Para Local: %s, ' \
                'Para Fone: %s, Duracao: %s, Horario: %s, Valor: %s' %(
            r.data_emissao,
            r.numero_recurso,
            r.mes_referencia,
            r.localidade_destino,
            dt,
            r.telefone_chamado,
            r.duracao,
            r.horario_ligacao,
            r.valor_ligacao_com_imp
        )

        print str_t

    j -= 20
    if j > 12 and fone[0] == '12991051133':
        valor = locale.currency((float(r.valor_ligacao_com_imp)/100), grouping=True, symbol=None)
        canvas.drawString(30,j,'%s' %(dt))
        canvas.drawString(70,j,'%s' %(dh))
        canvas.drawString(150,j,'%s' %(r.localidade_destino))
        canvas.drawString(300,j,'%s' %(dd))
        canvas.drawString(400,j,'%s' %(dur))
        canvas.drawString(450,j,'%s' %(r.cnl_recurso))
        canvas.drawString(550,j,'%s' %(valor))
        #canvas.drawString(400,j,'Ligacao para %s' %(r.duracao))         
    #if j < 12:
    if j < 12 and fone[0] == '12991051133':
        j = tamanho
        canvas.showPage() 
        canvas.drawString(30,tamanho,linha_cabecalho1)
        canvas.drawString(30,tamanho-10,linha_cabecalho2)

canvas.save()

"""
#canvas.drawString(30,750,'OFFICIAL COMMUNIQUE')
#canvas.drawString(30,735,'OF ACME INDUSTRIES')
#canvas.drawString(500,750,"12/12/2010")
#canvas.line(480,747,580,747)

canvas.drawString(275,725,'AMOUNT OWED:')
canvas.drawString(500,725,"$1,000.00")
canvas.line(378,723,580,723)

canvas.drawString(30,703,'RECEIVED BY:')
canvas.line(120,700,580,700)
canvas.drawString(120,703,"JOHN DOE")

canvas.save()
"""
