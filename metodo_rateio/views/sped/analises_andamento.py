from datetime import datetime
from django.shortcuts import render
from cadastro.models.empresa import Empresa
from metodo_rateio.models.sped import (
    analise_k23x,
    analise_k25x,
)
from django.views import View


def _empresas_filtro(ids):
    ids = {i for i in ids if i}
    if not ids:
        return []
    return list(Empresa.objects.filter(id__in=ids).order_by('razao_social'))


def _anos_como_lista(ano_sped):
    if ano_sped is None or ano_sped == '':
        return []
    if isinstance(ano_sped, list):
        valores = ano_sped
    else:
        valores = [ano_sped]
    return sorted({int(a) for a in valores if str(a).isdigit()})


class AnalisesEmAndamentoK23x(View):

    def get(self, request):
        analises = analise_k23x.objects.select_related('empresa').all()
        dados = []
        empresa_ids = set()
        for analise in analises:
            empresa_ids.add(analise.empresa_id)
            anos = _anos_como_lista(analise.ano_sped)
            if not anos:
                ano_exibicao = '-'
            elif len(anos) == 1:
                ano_exibicao = str(anos[0])
            else:
                ano_exibicao = f'{anos[0]} - {anos[-1]}'

            dados.append({
                'razao_social': analise.empresa.razao_social if analise.empresa else '-',
                'cnpj': analise.empresa.cnpj if analise.empresa else '-',
                'ano_sped': ano_exibicao,
                'empresa_id': analise.empresa_id,
                'data_inicio': analise.data_inicio,
            })

        return render(request, 'sped/analise_bloco_k.html', {
            'tipo': 'k23x',
            'dados': dados,
            'empresas_filtro': _empresas_filtro(empresa_ids),
            'agora': datetime.now(),
        })


class AnalisesEmAndamentoK25x(View):

    def get(self, request):
        analises = analise_k25x.objects.select_related('empresa').all()
        dados = []
        empresa_ids = set()
        for analise in analises:
            empresa_ids.add(analise.empresa_id)
            dados.append({
                'razao_social': analise.empresa.razao_social if analise.empresa else '-',
                'cnpj': analise.empresa.cnpj if analise.empresa else '-',
                'mes_sped': analise.mes_sped or '-',
                'ano_sped': analise.ano_sped or '-',
                'empresa_id': analise.empresa_id,
                'data_inicio': analise.data_inicio,
            })


        return render(request, 'sped/analise_bloco_k.html', {
            'tipo': 'k25x',
            'dados': dados,
            'empresas_filtro': _empresas_filtro(empresa_ids),
            'agora': datetime.now(),
        })
