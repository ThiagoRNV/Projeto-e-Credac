from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from cadastro.models.produtos import Cadastro_itens_sped
from validacao.models.painel_controle.validacao import ValidacaoDataConcluida
from django.views import View

class DeleteProductsViaSped(View):
    
    def post(self, request, id):
        produto = Cadastro_itens_sped.objects.filter(id=id).first()
        data_sped = produto.data_inicio_sped
        

        tem_movimentacao_concluida = ValidacaoDataConcluida.objects.filter(data_sped=data_sped)

        if tem_movimentacao_concluida:
            messages.warning(request, 'Item já com movimentação finalizada!')
            return redirect ('lista_produtos_sped')
        else:
            item = get_object_or_404(Cadastro_itens_sped, id=id)
            item.delete()
        messages.success(request, 'Item excluido com sucesso!')

        return redirect('lista_produtos_sped')

            