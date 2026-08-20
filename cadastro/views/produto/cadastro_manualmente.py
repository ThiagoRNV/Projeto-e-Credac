from django.contrib import messages
from cadastro.models.empresa import Empresa
from django.shortcuts import redirect, render
from cadastro.services.produto.cadastro_manualmente import CadastroManualServices
from django.views import View

class CadastroItensManual(View):
    
    def get(self, request):
        empresas = Empresa.objects.all().order_by('razao_social')

        return render(request, 'produtos/lista_produtosSped.html', {
            'empresas': empresas
        })    

    def post(self, request):

        services = CadastroManualServices(request.POST)

        processamento = services.cadatro_manual()

        sucess = processamento.get('sucess')
        error = processamento.get('error')

        if sucess:
            messages.success(request, 'Produto cadastrado com sucesso')
            return redirect ('lista_produtos_sped')
        else:
            messages.error(request, 'Erro ao cadastrar produto')
            print(f'Error: {error}')
            return redirect ('lista_produtos_sped')

