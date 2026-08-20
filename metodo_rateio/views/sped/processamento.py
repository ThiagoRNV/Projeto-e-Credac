# Arquivo de processamento de arquivos SPED solto ou em lote (pasta)
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from metodo_rateio.services.process_sped import ProcessamentoServices

import logging

logger = logging.getLogger(__name__)

class TelaUploadView(View):
       
    def get(self, request):
        return render(request, 'sped/upload_sped.html')

class ProcessamentoView(View):

    def post(self, request):
       
        btns = request.POST.get('btns')
        sped_file = request.FILES.get('sped_files')

        services = ProcessamentoServices(sped_file, btns)

        processamento = services.processar_bloco_k()

        failed_load = processamento.get('failed_load')

        if failed_load is False:
            messages.error(request, 'Erro ao carregar o Sped(s)')
            return redirect ('tela_para_processamento_sped')
        
        dados_sped = processamento.get('dados_sped')

        if dados_sped is False:
            messages.error(request, 'Erro ao extrair valores')
            return redirect ('tela_para_processamento_sped')

        cnpj_empresa = processamento.get('cnpj_empresa')
        
        if cnpj_empresa is False:
            logger.error('Cnpj não encontrado')
            messages.error(request, 'CNPJ não encontrado no arquivo SPED')
            return redirect ('tela_para_processamento_sped')

        empresa_obj = processamento.get('empresa_obj')

        if empresa_obj is False:
            messages.warning(request, 'Empresa não cadastrada')
            return redirect ('tela_para_processamento_sped')

        ano_processado = processamento.get('ano_processado')
        ano = processamento.get('ano')

        if ano_processado is True:
            messages.warning(request, f'O ano de {ano} já foi processado para o bloco K23X')
            return redirect('tela_para_processamento_sped')
            
        mes_processado = processamento.get('mes_processado')
        mes = processamento.get('mes')
     
        if mes_processado is True:
            messages.warning(request, f'O mês de {mes} já foi processado')
            return redirect ('tela_para_processamento_sped')

        bloco_processado = processamento.get('bloco_processado')

        if bloco_processado == 'ambos':
            messages.warning(request, f'O ano {ano} (K23X) e o mês {mes} (K25X) já foram processados')
            return redirect ('tela_para_processamento_sped')
        elif bloco_processado == '23x':
            messages.warning(request, f'O ano de {ano} já foi processado para o bloco K23X')
            return redirect ('tela_para_processamento_sped')
        elif bloco_processado == '25x':
            messages.warning(request, f'O mês de {mes} já foi processado para o bloco K25X')
            return redirect('tela_para_processamento_sped')
            
        sucess = processamento.get('sucess')
        erro = processamento.get('erro') or processamento.get('error')
        erro_inesperado = processamento.get('erro_inesperado')

        if sucess:
            messages.success(request, 'Arquivo processado com sucesso!')
            return redirect('tela_para_processamento_sped')

        if sucess is False:
            messages.error(request, 'Erro ao processar arquivo(s).')
            logger.error(f'Erro ao processar: {erro}')
            return redirect('tela_para_processamento_sped')

        if erro_inesperado:
            messages.error(request, f'Erro inesperado: {erro_inesperado}')
            return redirect('tela_para_processamento_sped')

        messages.error(request, f'Erro ao processar: {erro or "resposta inesperada do processamento"}')
        return redirect('tela_para_processamento_sped')
