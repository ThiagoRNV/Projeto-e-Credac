from asyncio import ProactorEventLoop
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from cadastro.models.empresa import Empresa
from django.views import View
from metodo_rateio.services.process_planilha import ProcessServices

class TelaParaProcessamento(View):

       def get(self, request):

              empresas = Empresa.objects.all()
              return render(request, 'planilha/upload_planilha.html', {'empresas': empresas})

class ProcessamentoXlsx(View):
       
       def post(self, request):

              planilha_custo = request.FILES.get('planilha_custo')
              empresa = request.POST.get('empresa')
              data_referencia = request.POST.get('data_referencia')
              empresa_id = get_object_or_404(Empresa, id=empresa)
              razao_social = empresa_id.razao_social

              services = ProcessServices(
                     planilha_custo, empresa, data_referencia, 
                     empresa_id, razao_social 
              ) 

              processamento = services.process_planilha()

              rc = processamento.get('razao_social')
              dr = processamento.get('data_referencia')
              pc = processamento.get('planilha_custo')
              planilha_verificacao = processamento.get('planilha_verificacao')

              if rc is False:
                     messages.error(request, 'Empresa não informada')
                     return redirect ('tela_para_processamento_planilha')

              if dr is False:
                     messages.error(request, 'Data não informada')
                     return redirect ('tela_para_processamento_planilha')

              if pc is False:
                     messages.error(request, 'Planilha não informada ')
                     return redirect ('tela_para_processamento_planilha')

              if planilha_verificacao is False:
                     messages.error(request, 'A planilha deve ser um arquivo (.xlsx)')
                     return redirect ('tela_para_processamento_planilha')


              dados_planilha = processamento.get('dados_planilha')
              values_planilha = processamento.get('values_planilha')

              if dados_planilha is False:
                     messages.error(request, 'Erro ao carregar planilha')
                     return redirect ('tela_para_processamento_planilha')

              if values_planilha is False:
                     messages.error(request, 'Erro ao extrair valores da planilha')
                     return redirect ('tela_para_processamento_planilha')

              sucess = processamento.get('sucess')

              if sucess:
                     messages.success(request, 'Planilha processada com sucesso')
                     return redirect ('tela_para_processamento_planilha')

              else:
                     messages.error(request, 'Erro ao processar planilha')
                     return redirect ('tela_para_processamento_planilha')
