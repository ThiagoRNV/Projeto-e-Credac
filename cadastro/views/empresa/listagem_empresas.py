from django.shortcuts import render
from django.views import View
from cadastro.models.empresa import Empresa
from django.db.models import Q

CAMPOS_OBRIGATORIOS = [
    'razao_social', 'cnpj', 'uf', 'email', 'cnae',
    'indicador_atividade', 'indicador_movimento', 'configuracao',
    'inscricao_estadual', 'codigo_municipio', 'ladca',
    'cod_ver', 'cod_fin',
]

class EmpresaView(View):

    def get(self, request):
        
        empresas_ativas = Empresa.objects.all().order_by('razao_social', 'cnpj', 'uf', 'status').filter(status=True)
        
        empresas_inativas = Empresa.objects.all().order_by('razao_social', 'cnpj', 'uf', 'status').filter(status=False)

        contagem_empresas_inativas = 0
        for empresa in empresas_inativas:
            if not empresa.status:
                contagem_empresas_inativas += 1

        filtro_pendente = Q()
        for campo in CAMPOS_OBRIGATORIOS:
            filtro_pendente |= Q(**{f'{campo}__isnull': True}) | Q(**{f'{campo}': ''})

        ids_com_pendencia = set(
            Empresa.objects.filter(filtro_pendente, status=True).values_list('id', flat=True)
        )
        total_empresas = empresas_ativas.count()
        total_pendentes = len(ids_com_pendencia)

        return render(request, 'empresas/lista_empresas.html', {
            'empresas': empresas_ativas,
            'empresas_inativas': empresas_inativas,
            'ids_com_pendencia': ids_com_pendencia,
            'total_pendentes': total_pendentes,
            'total_completas': total_empresas - total_pendentes,
            'inativas': contagem_empresas_inativas,
        })