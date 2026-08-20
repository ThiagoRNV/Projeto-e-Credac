from email import message
from django.shortcuts import get_object_or_404, redirect
from decimal import Decimal, InvalidOperation
from cadastro.models.produtos import Cadastro_itens_sped
from datetime import datetime
from django.http import JsonResponse
from django.views import View
from django.contrib import messages

class UpdateProductsViaSped(View):

    def post(self, request, id):
        """
        Atualiza o cadastro de itens do SPED (Cadastro_itens_sped) a partir do modal
        da tela de lista de produtos SPED.
        
        """
        produto = get_object_or_404(Cadastro_itens_sped, id=id)

      
        def parse_decimal(valor):
            if valor in (None, ''):
                return None
            valor = str(valor).strip()
            if not valor:
                return None
            if ',' in valor and '.' in valor:
                valor = valor.replace('.', '').replace(',', '.')
            else:
                valor = valor.replace(',', '.')
            try:
                return Decimal(valor)
            except (InvalidOperation, ValueError):
                return None

        # Empresa
        empresa_id = request.POST.get('empresa_id')
        if empresa_id:
            try:
                produto.empresa_id = int(empresa_id)
            except (TypeError, ValueError):
                pass

        # Datas
        data_inicio_str = request.POST.get('data_inicio_sped')
        if data_inicio_str:
            try:
                # Vem no formato dd/mm/YYYY do input
                produto.data_inicio_sped = datetime.strptime(data_inicio_str, '%d/%m/%Y').date()
            except ValueError:
                # Se der erro, apenas mantém o valor anterior
                pass

        # Campos básicos do cadastro
        produto.codigo_prod = request.POST.get('codigo_prod') or None
        produto.descricao_prod = request.POST.get('descricao_prod') or None
        produto.unidade = request.POST.get('unidade') or None
        produto.ncm = request.POST.get('ncm') or None
        produto.cest = request.POST.get('cest') or None
        produto.tipo_item = request.POST.get('tipo_item') or None
        produto.mes_ref = request.POST.get('mes_ref') or None

        produto.saldo_inicial_produto = parse_decimal(request.POST.get('saldo_inicial_produto'))
        produto.saldo_final_produto = parse_decimal(request.POST.get('saldo_final_produto'))
        produto.genero = request.POST.get('genero')

        sucess = produto.save()



        # Sempre responde JSON para chamadas AJAX, evitando HTML (<!DOCTYPE ...>)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = {
                'success': True,
                'produto': {
                    'id': produto.id,
                    'empresa': produto.empresa.razao_social if produto.empresa else '---',
                    'codigo_prod': produto.codigo_prod or '---',
                    'descricao_prod': produto.descricao_prod or '---',
                    'ncm': produto.ncm or '---',
                    'data_inicio_sped': produto.data_inicio_sped.strftime('%d/%m/%Y') if produto.data_inicio_sped else '---',
                },
                'message': 'Item atualizado'
            }
            return JsonResponse(data)

        return redirect('lista_produtos_sped')