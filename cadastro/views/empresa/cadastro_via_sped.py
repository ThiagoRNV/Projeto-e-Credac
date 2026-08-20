from multiprocessing import process
from django.shortcuts import render, redirect
from django.contrib import messages
from cadastro.services.empresas.cadastro_via_sped import EmpresaViaSpedServices
from cadastro.models.empresa import Empresa
from django.views import View


class CadastrarViaSped(View):

    def get(self, request):

        return render(request, 'empresas/cadastrar_via_sped.html')
    
    def post(self, request):

        sped_file = request.FILES.get('sped_empresa')

        if not sped_file:
            messages.error(request, 'Nenhum arquivo SPED enviado.')
            return redirect('lista_empresas')

        if not sped_file.name.endswith('.txt'):
            messages.error(request, 'O arquivo SPED deve ser um arquivo .txt.')
            return redirect('lista_empresas')

        service = EmpresaViaSpedServices(sped_file)

        process_sped = service.create_job_sped()

        processamento_concluido = process_sped.get('processamento_concluido')

        razao_social = process_sped.get('razao_social')
        primeiro_nome = razao_social.split()[0]  

        if processamento_concluido:
            messages.success(request, f'Empresa {primeiro_nome} Cadastrada com sucesso!')
            return redirect('lista_empresas')
        else:
            messages.error(request, 'Erro ao cadastrar a empresa.')
            return redirect('lista_empresas')
