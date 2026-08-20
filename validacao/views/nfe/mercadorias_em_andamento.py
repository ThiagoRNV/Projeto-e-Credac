from calendar import monthrange

from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from django.contrib import messages
from datetime import datetime
from django.urls import reverse
from cadastro.models.empresa import Empresa
from validacao.models.painel_controle.validacao import ValidacaoStatus, ValidacaoDataConcluida
from validacao.models.mercadorias_nfe.produtos import Produtos_notas
from validacao.models.mercadorias_nfe.notas import Notas_participantes
from validacao.models.participantes.participantes import Participantes
import logging

logger = logging.getLogger(__name__)

def _periodo_sped(data):
    if not data:
        return None, None
    ultimo_dia = monthrange(data.year, data.month)[1]
    return data.replace(day=1), data.replace(day=ultimo_dia)


class MercadoriasView:

    @staticmethod
    def mercadorias_em_andamento(request):   
    
        validacoes_em_andamento = ValidacaoStatus.objects.select_related('empresa').filter(tipo_validacao='nfe').order_by('-data_atualizacao')
        validacoes_concluidas = ValidacaoDataConcluida.objects.select_related('empresa').filter(tipo_validacao='nfe')
        # Mapa (empresa_id, data_sped) -> ValidacaoStatus (mais recente) para status por data
        status_por_empresa_data = {}
        for vs in ValidacaoStatus.objects.filter(data_sped__isnull=False, tipo_validacao='nfe').order_by('-data_atualizacao'):
            k = (vs.empresa_id, vs.data_sped)
            if k not in status_por_empresa_data:
                status_por_empresa_data[k] = vs
        
        movimentacoes = []
        movimentacoes_concluidas = []

        # Usados para checar duplicidade por empresa e data_sped
        chaves_concluidas = set()
        chaves_andamento = set()


        if validacoes_em_andamento:
            for v_andamento in validacoes_em_andamento:
                # Verifica existência de qualquer dado para a empresa
                tem_upload = (
                    Produtos_notas.objects.filter(empresa=v_andamento.empresa).exists() or
                    Notas_participantes.objects.filter(empresa=v_andamento.empresa).exists() or
                    Participantes.objects.filter(empresa=v_andamento.empresa).exists()
                )
                if not tem_upload:
                    continue

                datas_com_dados = set()

                # Participantes com dados
                participantes_datas = Participantes.objects.filter(empresa=v_andamento.empresa).values_list('data_inicio_sped', flat=True).distinct()
                for data in participantes_datas:
                    if data is not None:
                        datas_com_dados.add(data)

                # Notas_participantes com dados
                notas_participantes_datas = Notas_participantes.objects.filter(empresa=v_andamento.empresa).values_list('data_inicio_sped', flat=True).distinct()
                for data in notas_participantes_datas:
                    if data is not None:
                        datas_com_dados.add(data)

                # Produtos com dados
                produtos_datas = Produtos_notas.objects.filter(empresa=v_andamento.empresa).values_list('data_inicio_sped', flat=True).distinct()
                for data in produtos_datas:
                    if data is not None:
                        datas_com_dados.add(data)

                # Se não houver datas com dados reais, não exibe a empresa
                if not datas_com_dados:
                    continue

                for data in sorted(datas_com_dados, reverse=True):
                    chave = (v_andamento.empresa.id, str(data))
                    
                    if chave not in chaves_andamento:
                            # Status de SPED, XML e DUE específicos para ESTA data (não do v genérico)
                            status_esta_data = status_por_empresa_data.get((v_andamento.empresa.id, data))
                            if status_esta_data is None and data:
                                for (eid, d), vs in status_por_empresa_data.items():
                                    if eid == v_andamento.empresa.id and d and d.month == data.month and d.year == data.year:
                                        status_esta_data = vs
                                        break
                            if status_esta_data:
                                s_sped = '🟢' if status_esta_data.sped else '🔴'
                                s_xml = '🟢' if status_esta_data.xml else '🔴'
                                s_due = '🟢' if status_esta_data.due else '🔴'
                            else:
                                s_sped = s_xml = s_due = '🔴'

                            data_inicial, data_final = _periodo_sped(data)
                            movimentacoes.append({
                                'empresa_id': v_andamento.empresa.id,
                                'razao_social': v_andamento.empresa.razao_social,
                                'cnpj': v_andamento.empresa.cnpj,
                                'status': v_andamento.status if v_andamento.status != 'concluido' else 'em_andamento',
                                'progresso': v_andamento.progresso,
                                'data_sped': data,
                                'data_inicial': data_inicial,
                                'data_final': data_final,
                                'sped': s_sped,
                                'xml': s_xml,
                                'due': s_due,
                            })
                            chaves_andamento.add(chave)

        if validacoes_concluidas:
            for v_concluido in validacoes_concluidas:
                # Verifica existência de qualquer dado para a empresa
                tem_upload = (
                    Produtos_notas.objects.filter(empresa=v_concluido.empresa).exists() or
                    Notas_participantes.objects.filter(empresa=v_concluido.empresa).exists() or
                    Participantes.objects.filter(empresa=v_concluido.empresa).exists()
                )
                if not tem_upload:
                    continue

                datas_com_dados = set()

                # Participantes com dados
                participantes_datas = Participantes.objects.filter(empresa=v_concluido.empresa).values_list('data_inicio_sped', flat=True).distinct()
                for data in participantes_datas:
                    if data is not None:
                        datas_com_dados.add(data)

                # Notas_participantes com dados
                notas_participantes_datas = Notas_participantes.objects.filter(empresa=v_concluido.empresa).values_list('data_inicio_sped', flat=True).distinct()
                for data in notas_participantes_datas:
                    if data is not None:
                        datas_com_dados.add(data)

                # Produtos com dados
                produtos_datas = Produtos_notas.objects.filter(empresa=v_concluido.empresa).values_list('data_inicio_sped', flat=True).distinct()
                for data in produtos_datas:
                    if data is not None:
                        datas_com_dados.add(data)

                # Se não houver datas com dados reais, não exibe a empresa
                if not datas_com_dados:
                    continue
                
                for data in sorted(datas_com_dados, reverse=True):
                    chave = (v_concluido.empresa.id, str(data))

                    if validacoes_concluidas:
                        if chave not in chaves_concluidas:
                            data_inicial, data_final = _periodo_sped(data)
                            movimentacoes_concluidas.append({
                                'empresa_id': v_concluido.empresa.id,
                                'razao_social': v_concluido.empresa.razao_social,
                                'cnpj': v_concluido.empresa.cnpj,
                                'status': 'concluido',
                                'data_sped': data,
                                'data_inicial': data_inicial,
                                'data_final': data_final,
                            })
                            chaves_concluidas.add(chave)

        empresas_filtro = Empresa.objects.filter(
                id__in={
                    *(m['empresa_id'] for m in movimentacoes),
                    *(m['empresa_id'] for m in movimentacoes_concluidas),
                }
            ).order_by('razao_social')
        total_movimentacoes = len(movimentacoes) + len(movimentacoes_concluidas)

        return render(request, 'mercadorias_nfe/mercadorias_em_andamento.html', {
            'empresas': movimentacoes,
            'empresas_concluidas': movimentacoes_concluidas,
            'empresas_filtro': empresas_filtro,
            'total_movimentacoes': total_movimentacoes,
        })
            

    # @staticmethod
    # def limpar_dados_concluidos(request):
    #     if request.method == 'POST':
    #         try:
    #             ValidacaoDataConcluida.objects.all().delete()
    #             messages.success(request, 'Dados de validações concluídas foram limpos com sucesso!')
    #         except Exception as e:
    #             messages.error(request, f'Erro ao limpar dados: {str(e)}')
        
    #     return redirect('mercadorias_em_andamento')
    
    @staticmethod
    def finalizar_movimentacao(request):
        if request.method == 'POST':
            
            empresa_id = request.POST.get('empresa_id')
            data_sped = request.POST.get('data_sped')

            if not empresa_id or not data_sped:
                messages.error(request, 'Parâmetros inválidos para finalizar.')
                return redirect('mercadorias_em_andamento')

            try:
                data_sped_obj = datetime.strptime(data_sped, '%Y-%m-%d').date()
            except (ValueError, TypeError) as e:
                messages.error(request, f'Data SPED inválida: {data_sped}. Deve ser no formato YYYY-MM-DD.')
                return redirect('mercadorias_em_andamento')

            lista_mes ={
                '01': 'Janeiro',
                '02': 'Fevereiro',
                '03': 'Março',
                '04': 'Abril',
                '05': 'Maio',
                '06': 'Junho',
                '07': 'Julho',
                '08': 'Agosto',
                '09': 'Setembro',
                '10': 'Outubro',
                '11': 'Novembro',
                '12': 'Dezembro',
            }

            data_sped_str = data_sped_obj.strftime('%d%m%Y')
            
            mes_sped = lista_mes.get(data_sped_str[2:4])

            try:
                ValidacaoDataConcluida.objects.create(
                    empresa_id=empresa_id,
                    data_sped=data_sped_obj,
                    mes_sped=mes_sped,
                    tipo_validacao='nfe'
                )
                todas_datas = set(Produtos_notas.objects.filter(empresa_id=empresa_id).exclude(data_inicio_sped__isnull=True).values_list('data_inicio_sped', flat=True).distinct())
                todas_datas.update(Notas_participantes.objects.filter(empresa_id=empresa_id).exclude(data_inicio_sped__isnull=True).values_list('data_inicio_sped', flat=True).distinct())
                todas_datas.update(Participantes.objects.filter(empresa_id=empresa_id).exclude(data_inicio_sped__isnull=True).values_list('data_inicio_sped', flat=True).distinct())
                todas_datas = {d for d in todas_datas if d is not None}

                concluidas = set(
                    ValidacaoDataConcluida.objects.filter(
                        empresa_id=empresa_id,
                        tipo_validacao='nfe',
                    ).values_list('data_sped', flat=True)
                )

                if todas_datas and todas_datas.issubset(concluidas):
                    ValidacaoStatus.objects.filter(empresa_id=empresa_id, data_sped=data_sped_obj, tipo_validacao='nfe').delete()

                messages.success(request, 'Movimentação finalizada com sucesso!')
                return redirect ("mercadorias_em_andamento")
            except Exception as e:
                logger.error(request, f'Erro ao finalizar movimentação: {str(e)}')

        return redirect('mercadorias_em_andamento')
        
    @staticmethod
    def mover_para_edicao(request):

        empresa_id = request.GET.get('empresa_id') or request.POST.get('empresa_id')
        data_sped_param = request.GET.get('data_sped') or request.POST.get('data_sped')


        if not empresa_id or not data_sped_param:
            messages.error(request, 'Parâmetros inválidos para mover para edição.')
            return redirect('mercadorias_em_andamento')

        try:
            empresa_id = int(empresa_id)
            empresa_obj = Empresa.objects.get(id=empresa_id)

        except (TypeError, ValueError):
            messages.error(request, 'Empresa ID inválido.')
            return redirect('mercadorias_em_andamento')


        try:
            data_sped_obj = datetime.strptime(data_sped_param, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, 'Data SPED inválida. Deve ser no formato YYYY-MM-DD.')
            return redirect('mercadorias_em_andamento')

        ValidacaoStatus.objects.create(
            empresa=empresa_obj,
            status='em_andamento',
            progresso=0,
            # data_atualizacao=timezone.now(),
            data_sped=data_sped_param,
            sped=True,
            xml=True,
            tipo_validacao='nfe'
        )

        ValidacaoDataConcluida.objects.filter(
            empresa_id=empresa_id,
            data_sped=data_sped_obj,
            tipo_validacao='nfe'
        ).delete()

        messages.success(request, 'Movimentação movida para edição com sucesso!')
        return redirect(reverse('mercadorias_em_andamento') + f'?empresa_id={empresa_id}&data_sped={data_sped_param}')