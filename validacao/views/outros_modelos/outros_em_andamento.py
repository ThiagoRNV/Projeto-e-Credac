from calendar import monthrange
from csv import Error

from django.http.response import HttpResponseServerError
from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from cadastro.models.empresa import Empresa
from validacao.models.painel_controle.validacao import ValidacaoStatus, ValidacaoDataConcluida
from validacao.models.participantes.participantes import Participantes
from validacao.models.outros_modelos.registrod100 import RegistroTransporteD100
from validacao.models.outros_modelos.registrod190 import RegistroTransporteD190
from validacao.models.outros_modelos.registroc500 import RegistroEnergiaC500
from validacao.models.outros_modelos.registrod500 import RegistroComunicacaoD500

from validacao.services.outros_modelos.outros_em_andamento.finalizar_servicos import DataErrorFinish, ErrorParamFinish, FinalizarServices, ErrorFinish
from validacao.services.outros_modelos.outros_em_andamento.mover_para_edicao import CompainerIdError, DataError, ErrorMove, ErrorParam, MoverParaEdicaoServices


import logging

logger = logging.getLogger(__name__)


def _periodo_sped(data):
    if not data:
        return None, None
    ultimo_dia = monthrange(data.year, data.month)[1]
    return data.replace(day=1), data.replace(day=ultimo_dia)


class CtesView(View):

    def get(self, request):   

        validacoes = ValidacaoStatus.objects.select_related('empresa').filter(tipo_validacao='outros_modelos').order_by('-data_atualizacao')

        # Mapa (empresa_id, data_sped) -> ValidacaoStatus (mais recente) para status por data
        status_por_empresa_data = {}
        for vs in ValidacaoStatus.objects.filter(data_sped__isnull=False, tipo_validacao='outros_modelos').order_by('-data_atualizacao'):
            k = (vs.empresa_id, vs.data_sped)
            if k not in status_por_empresa_data:
                status_por_empresa_data[k] = vs
        
        movimentacoes = []
        movimentacoes_concluidas = []

        # Usados para checar duplicidade por empresa e data_sped
        chaves_concluidas = set()
        chaves_andamento = set()

        # Concluídas vêm direto de ValidacaoDataConcluida, pois o ValidacaoStatus
        # é apagado quando todas as datas da empresa são finalizadas
        for c in ValidacaoDataConcluida.objects.select_related('empresa').filter(
            tipo_validacao='outros_modelos'
        ).order_by('-data_sped'):
            tem_dados_cte = (
                RegistroTransporteD100.objects.filter(empresa=c.empresa, data_inicio_sped=c.data_sped).exists() or
                RegistroTransporteD190.objects.filter(empresa=c.empresa, data_inicio_sped=c.data_sped).exists() or
                RegistroEnergiaC500.objects.filter(empresa=c.empresa, data_inicio_sped=c.data_sped).exists() or
                RegistroComunicacaoD500.objects.filter(empresa=c.empresa, data_inicio_sped=c.data_sped).exists()
            )
            if not tem_dados_cte:
                continue

            chave = (c.empresa_id, str(c.data_sped))
            if chave in chaves_concluidas:
                continue

            data_inicial, data_final = _periodo_sped(c.data_sped)
            movimentacoes_concluidas.append({
                'empresa_id': c.empresa_id,
                'razao_social': c.empresa.razao_social,
                'cnpj': c.empresa.cnpj,
                'status': 'concluido',
                'progresso': 100,
                'data_sped': c.data_sped,
                'data_inicial': data_inicial,
                'data_final': data_final,
                'tipo_validacao': 'outros_modelos',
            })
            chaves_concluidas.add(chave)

        for v in validacoes:
            # Verifica existência de qualquer dado para a empresa
            tem_upload = (
                RegistroTransporteD100.objects.filter(empresa=v.empresa).exists() or
                RegistroTransporteD190.objects.filter(empresa=v.empresa).exists() or
                RegistroEnergiaC500.objects.filter(empresa=v.empresa).exists() or
                RegistroComunicacaoD500.objects.filter(empresa=v.empresa).exists() or
                Participantes.objects.filter(empresa=v.empresa).exists()
            )
            if not tem_upload:
                continue

            datas_com_dados = set()

            # Participantes com dados
            participantes_datas = Participantes.objects.filter(empresa=v.empresa).values_list('data_inicio_sped', flat=True).distinct()
            for data in participantes_datas:
                if data is not None:
                    datas_com_dados.add(data)

            # Notas_participantes com dados
            notas_participantes_datas = RegistroTransporteD100.objects.filter(empresa=v.empresa).values_list('data_inicio_sped', flat=True).distinct()
            for data in notas_participantes_datas:
                if data is not None:
                    datas_com_dados.add(data)

            # Produtos com dados
            produtos_datas = RegistroTransporteD100.objects.filter(empresa=v.empresa).values_list('data_inicio_sped', flat=True).distinct()
            for data in produtos_datas:
                if data is not None:
                    datas_com_dados.add(data)

            # Energia (C500) com dados
            energia_datas = RegistroEnergiaC500.objects.filter(empresa=v.empresa).values_list('data_inicio_sped', flat=True).distinct()
            for data in energia_datas:
                if data is not None:
                    datas_com_dados.add(data)

            # Comunicação (D500) com dados
            comunicacao_datas = RegistroComunicacaoD500.objects.filter(empresa=v.empresa).values_list('data_inicio_sped', flat=True).distinct()
            for data in comunicacao_datas:
                if data is not None:
                    datas_com_dados.add(data)

            # Se não houver datas com dados reais, não exibe a empresa
            if not datas_com_dados:
                continue

            for data in sorted(datas_com_dados, reverse=True):
                chave = (v.empresa.id, str(data))
                foi_finalizada_pelo_usuario = ValidacaoDataConcluida.objects.filter(
                    empresa=v.empresa,
                    data_sped=data,
                    tipo_validacao='outros_modelos',
                ).exists()

                if foi_finalizada_pelo_usuario:
                    # Concluídas já foram montadas acima a partir de ValidacaoDataConcluida
                    continue
                else:
                    if chave not in chaves_andamento:
                        # Status de SPED, XML e DUE específicos para ESTA data (não do v genérico)
                        status_esta_data = status_por_empresa_data.get((v.empresa.id, data))
                        if status_esta_data is None and data:
                            for (eid, d), vs in status_por_empresa_data.items():
                                if eid == v.empresa.id and d and d.month == data.month and d.year == data.year:
                                    status_esta_data = vs
                                    break
                        if status_esta_data:
                            s_sped = '🟢' if status_esta_data.sped else '🔴'
                        else:
                            s_sped = s_xml = s_due = '🔴'

                        data_inicial, data_final = _periodo_sped(data)
                        movimentacoes.append({
                            'empresa_id': v.empresa.id,
                            'razao_social': v.empresa.razao_social,
                            'cnpj': v.empresa.cnpj,
                            'status': v.status if v.status != 'concluido' else 'em_andamento',
                            'progresso': v.progresso,
                            'data_sped': data,
                            'data_inicial': data_inicial,
                            'data_final': data_final,
                            'sped': s_sped,
                        })
                        chaves_andamento.add(chave)

        empresas_filtro = Empresa.objects.filter(
            id__in={
                *(m['empresa_id'] for m in movimentacoes),
                *(m['empresa_id'] for m in movimentacoes_concluidas),
            }
        ).order_by('razao_social')

        total_movimentacoes = len(movimentacoes) + len(movimentacoes_concluidas)

        return render(request, 'outros_modelos/outros_em_andamento.html', {
            'empresas': movimentacoes,
            'empresas_concluidas': movimentacoes_concluidas,
            'empresas_outros_modelos': movimentacoes,
            'empresas_concluidas_outros_modelos': movimentacoes_concluidas,
            'empresas_filtro': empresas_filtro,
            'total_movimentacoes': total_movimentacoes,
            'agora': timezone.now(),
        })


    def post(self, request):
        
        opcs = request.POST.get('opcs')

        if opcs == 'finalizar':
            return self.finalizar(request)

        elif opcs == 'mover_para_edicao':
            return self.mover_para_edicao(request)

        return redirect('outros_em_andamento')

    def finalizar(self, request):

        empresa_id = request.POST.get('empresa_id')
        data_sped = request.POST.get('data_sped')

        try:
            service = FinalizarServices(empresa_id, data_sped)

            dados = service.finalizar_servico()

            success = dados.get('success')
            
            if success:
                messages.success(request, 'Movimentação finalizada com sucesso.')
                return redirect ('outros_modelos_em_andamento')
        except ErrorParamFinish as e:
            return HttpResponseServerError(
                'Não foi possível realizar sua solicitação. Favor entrar em contato com o suporte.'
            )
        except DataErrorFinish:
            return HttpResponseServerError(
                'Não foi possível realizar sua solicitação. Favor entrar em contato com o suporte.'
            )
        except ErrorFinish as e:
            messages.error(request, str(e))
            return redirect ('outros_modelos_em_andamento')
        
    def mover_para_edicao(self, request):

        empresa_id = request.GET.get('empresa_id') or request.POST.get('empresa_id')
        data_sped_param = request.GET.get('data_sped') or request.POST.get('data_sped')

        try:

            services = MoverParaEdicaoServices(empresa_id, data_sped_param)

            mover_edicao = services.mover_edicao_services()

            success = mover_edicao.get('success')
            
            if success:
                messages.success(request, 'Movimentação movida para edição com sucesso.')
                return redirect(reverse('outros_modelos_em_andamento') + f'?empresa_id={empresa_id}&data_sped={data_sped_param}')
        
        except DataError:
            return HttpResponseServerError(
                'Erro ao realizar sua solicitação. Favor entrar em contato com o suporte.'
            )
        except ErrorParam:
            return HttpResponseServerError(
                'Erro ao realizar sua solicitação. Favor entrar em contato com o suporte.'
            )
        except CompainerIdError:
            return HttpResponseServerError(
                'Erro ao realizar sua solicitação. Favor entrar em contato com o suporte.'
            )

        except CompainerIdError:
            return HttpResponseServerError(
                'Erro ao realizar sua solicitação. Favor entrar em contato com o suporte.'
            )

        except ErrorMove as e:
            messages.error(request, str(e))
            return redirect('outros_modelos_em_andamento')