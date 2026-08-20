from django.contrib import messages
from cadastro.models.empresa import Empresa
from django.shortcuts import render, redirect
from cadastro.services.empresas.cadastro_manualmente import EmpresaManualmenteServices
from django.views import View


class CadastrarManual(View):

        def get(self, request):

            return render(request, 'empresas/cadastrar_manu.html')

        def post(self, request):
            service = EmpresaManualmenteServices(request.POST)
            processamento = service.create_job()

            sucess = processamento.get('sucess')
            error = processamento.get('error')
                
            if sucess:
                messages.success(request, 'Empresa cadastrada com sucesso!')
                return redirect('lista_empresas')

            else: 
                messages.error(request, f'Erro ao cadastrar a empresa! {error}')
                return redirect('lista_empresas')