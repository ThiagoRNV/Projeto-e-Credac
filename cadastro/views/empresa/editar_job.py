from django.shortcuts import get_object_or_404, redirect, render
from cadastro.models.empresa import Empresa
from django.contrib import messages
from cadastro.services.empresas.editar_companie import UpdateServices
from django.views import View

# Class based view ( CBV)
class Editarjob(View):

    def get(self, request, id):

        empresa = get_object_or_404(Empresa, id=id)

        return render(request, 'empresas/lista_empresas.html', {'empresa': empresa})

    def post(self, request, id):

        empresa_id = get_object_or_404(Empresa, id=id)

        service = UpdateServices(request.POST, empresa_id)

        upt = service.editar_job()

        sucess = upt.get('sucess')

        if sucess:
            messages.success(request, 'Dados salvos com sucesso.')
            return redirect ('lista_empresas')

        else:
            messages.error(request, 'Erro ao editar empresa.')
            return redirect ('lista_empresas')
          