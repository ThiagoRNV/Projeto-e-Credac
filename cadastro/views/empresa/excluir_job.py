from django.shortcuts import get_object_or_404, render, redirect
from cadastro.models.empresa import Empresa
from django.views import View

class ExcluirJob(View):
    
    def get(self, request):

        return render(request, 'empresas/lista_empresas.html')

    def post(self, request, id):
        empresa = get_object_or_404(
            Empresa, 
            id=id
        )
        empresa.delete()

        return redirect('lista_empresas')