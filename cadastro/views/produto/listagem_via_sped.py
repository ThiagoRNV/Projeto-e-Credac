from urllib.parse import urlencode

from django.shortcuts import render
from django.views import View
from cadastro.models.produtos import Cadastro_itens_sped
from cadastro.models.empresa import Empresa
from django.core.paginator import Paginator

class ListarProdutosSped(View):

    def get(self, request):

        filtros = {
            'f0': request.GET.get('f0', '').strip(),
            'f1': request.GET.get('f1', '').strip(),
            'f2': request.GET.get('f2', '').strip(),
            'f3': request.GET.get('f3', '').strip(),
            'f4': request.GET.get('f4', '').strip(),
        }

        produtos = Cadastro_itens_sped.objects.select_related('empresa').all().order_by('codigo_prod', 'ncm', 'cest')

        if filtros['f0']:
            produtos = produtos.filter(empresa__razao_social__icontains=filtros['f0'])
        if filtros['f1']:
            produtos = produtos.filter(codigo_prod__icontains=filtros['f1'])
        if filtros['f2']:
            produtos = produtos.filter(descricao_prod__icontains=filtros['f2'])
        if filtros['f3']:
            produtos = produtos.filter(ncm__icontains=filtros['f3'])
        if filtros['f4']:
            produtos = produtos.filter(mes_ref__icontains=filtros['f4'])

        meses = (
            Cadastro_itens_sped.objects.values_list('mes_ref', flat=True).distinct()
        )

        paginator = Paginator(produtos, 100)
        pagina_atual = request.GET.get('page', 1)
        dados_pag = paginator.get_page(pagina_atual)
        empresas = Empresa.objects.all().order_by('razao_social').filter(status=True)

        current_query = {k: v for k, v in filtros.items() if v}
        current_query_str = urlencode(current_query)

        return render(request, 'produtos/lista_produtosSped.html',
            {
                'produtos': dados_pag,
                'empresas': empresas,
                'meses': meses,
                'filtros': filtros,
                'current_query': current_query_str,
            }
        )   