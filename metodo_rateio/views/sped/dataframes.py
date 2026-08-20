from django.shortcuts import render, redirect
from django.db import connection
import pandas as pd
from django.core.paginator import Paginator
from datetime import datetime, date
from metodo_rateio.models.sped import ItensProduzidos230, InsumosUsados235, ItensProduzidos250, InsumosUsados255
from django.db.models import Prefetch
from django.views import View

class DataFrameViewK23x(View):
       ##### View paxra blocos K230/K235 (Produção Própria) #####
       def get(self, request):
              """View apenas para blocos K230/K235 (Produção Própria)"""
              meses_ordem = {
                  'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
                  'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
                  'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
              }
              filtros = {
                  'bloco': request.GET.get('f0', '').strip(),
                  'data_inicial_op': request.GET.get('f1', '').strip(),
                  'data_final_op': request.GET.get('f2', '').strip(),
                  'cod_ordem_prod': request.GET.get('f3', '').strip(),
                  'codigo_item': request.GET.get('f4', '').strip(),
                  'qtd_producao_acabada': request.GET.get('f5', '').strip(),
                  'mes_referencia_k230': request.GET.get('f6', '').strip(),
                  'data_saida_estoque': request.GET.get('f7', '').strip(),
                  'quantidade': request.GET.get('f8', '').strip(),
                  'codigo_insumo': request.GET.get('f9', '').strip(),
                  'ano_sped': request.GET.get('f10', '').strip(),
                  'mes_referencia_k235': request.GET.get('f11', '').strip(),
              }
              itens_produzidos230 = ItensProduzidos230.objects.select_related('empresa')
              if filtros['data_inicial_op']:
                     itens_produzidos230 = itens_produzidos230.filter(data_inicial_op__icontains=filtros['data_inicial_op'])
              if filtros['data_final_op']:
                     itens_produzidos230 = itens_produzidos230.filter(data_final_op__icontains=filtros['data_final_op'])
              if filtros['cod_ordem_prod']:
                     itens_produzidos230 = itens_produzidos230.filter(cod_ordem_prod__icontains=filtros['cod_ordem_prod'])
              if filtros['codigo_item']:
                     itens_produzidos230 = itens_produzidos230.filter(codigo_item__icontains=filtros['codigo_item'])
              if filtros['qtd_producao_acabada']:
                     itens_produzidos230 = itens_produzidos230.filter(qtd_producao_acabada__icontains=filtros['qtd_producao_acabada'])
              if filtros['mes_referencia_k230']:
                     itens_produzidos230 = itens_produzidos230.filter(mes_referencia_k230__icontains=filtros['mes_referencia_k230'])
              if filtros['ano_sped']:
                     itens_produzidos230 = itens_produzidos230.filter(ano_sped__icontains=filtros['ano_sped'])
              insumos_queryset235 = InsumosUsados235.objects.all().order_by('data_saida_estoque', 'registro', 'id')
              if filtros['data_saida_estoque']:
                     insumos_queryset235 = insumos_queryset235.filter(data_saida_estoque__icontains=filtros['data_saida_estoque'])
              if filtros['quantidade']:
                     insumos_queryset235 = insumos_queryset235.filter(quantidade__icontains=filtros['quantidade'])
              if filtros['codigo_insumo']:
                     insumos_queryset235 = insumos_queryset235.filter(codigo_insumo__icontains=filtros['codigo_insumo'])
              if filtros['ano_sped']:
                     insumos_queryset235 = insumos_queryset235.filter(ano_sped__icontains=filtros['ano_sped'])
              if filtros['mes_referencia_k235']:
                     insumos_queryset235 = insumos_queryset235.filter(mes_referencia_k235__icontains=filtros['mes_referencia_k235'])
              itens_produzidos230 = itens_produzidos230.prefetch_related(Prefetch('insumosusados235_set', queryset=insumos_queryset235))
              grupos_ordem = {}
              for item in itens_produzidos230:
                     chave_grupo = (item.cod_ordem_prod or '', item.codigo_item or '')
                     if chave_grupo not in grupos_ordem:
                            grupos_ordem[chave_grupo] = []
                     grupos_ordem[chave_grupo].append(item)
              grupos_ordenados = []
              for chave, itens_grupo in grupos_ordem.items():
                     itens_grupo_ordenados = sorted(itens_grupo, key=lambda x: (meses_ordem.get(x.mes_referencia_k230 or '', 99), x.data_inicial_op or date.min, x.registro or ''))
                     grupos_ordenados.append({'chave': chave, 'k230s': itens_grupo_ordenados, 'k235s': []})
              grupos_ordenados = sorted(grupos_ordenados, key=lambda g: (g['chave'][0], g['chave'][1]))
              for grupo in grupos_ordenados:
                     todos_k235s_com_ref = [{'k235': k235, 'mes_k230': k230.mes_referencia_k230 or ''} for k230 in grupo['k230s'] for k235 in k230.insumosusados235_set .all()]
                     grupo['k235s'] = [item['k235'] for item in sorted(todos_k235s_com_ref, key=lambda i: (meses_ordem.get(i['mes_k230'], 99), i['k235'].data_saida_estoque or date.min, i['k235'].registro or '', i['k235'].id or 0))]
              if filtros['bloco']:
                     bloco_filtro = filtros['bloco'].upper().strip()
                     grupos_filtrados_bloco = []
                     for grupo in grupos_ordenados:
                            gf = {'chave': grupo['chave'], 'k230s': grupo['k230s'] if 'K230' in bloco_filtro and grupo['k230s'] else [], 'k235s': grupo['k235s'] if 'K235' in bloco_filtro and grupo['k235s'] else []}
                            if 'K230' not in bloco_filtro and 'K235' not in bloco_filtro:
                                   grupos_filtrados_bloco.append(grupo)
                            elif gf['k230s'] or gf['k235s']:
                                   grupos_filtrados_bloco.append(gf)
                     grupos_ordenados = grupos_filtrados_bloco
              grupos_filtrados = [g for g in grupos_ordenados if not (filtros['data_saida_estoque'] or filtros['quantidade'] or filtros['codigo_insumo']) or g['k235s'] or g['k230s']]
              grupos_ordenados = grupos_filtrados
              paginator = Paginator(grupos_ordenados, 50)
              dados_query = paginator.get_page(request.GET.get('page', 1))
              current_query_parts = []
              col_map = {'bloco': 'f0', 'data_inicial_op': 'f1', 'data_final_op': 'f2', 'cod_ordem_prod': 'f3', 'codigo_item': 'f4', 'qtd_producao_acabada': 'f5', 'mes_referencia_k230': 'f6', 'data_saida_estoque': 'f7', 'quantidade': 'f8', 'codigo_insumo': 'f9', 'ano_sped': 'f10', 'mes_referencia_k235': 'f11'}
              for key, value in filtros.items():
                     if value and col_map.get(key):
                            current_query_parts.append(f"{col_map[key]}={value}")
              return render(request, 'sped/view_producao_k230_k235.html', {
                     'dados_query': dados_query,
                     'filters': filtros,
                     'current_query': '&'.join(current_query_parts),
                     'empresa_id': request.GET.get('empresa_id', ''),
              })
class DataFrameViewK25x(View):
       ##### View para blocos K250/K255 (Industrialização Terceiros) #####
       def get(self, request):
              """
              View apenas para blocos K250/K255 (Industrialização Terceiros), filtrando
              corretamente pelo mes_sped e empresa_id, conforme selecionado no template.
              """
              empresa_id_param = request.GET.get('empresa_id', '').strip()
              mes_sped_param = request.GET.get('mes_sped', '').strip()  # Ex: "Janeiro", "Fevereiro" (sem case)

              meses_ordem = {'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12}
              
              filtros_terceiros = {
                  'bloco': request.GET.get('tf0', '').strip(),
                  'data_prod': request.GET.get('tf1', '').strip(),
                  'cod_item': request.GET.get('tf2', '').strip(),
                  'quantidade': request.GET.get('tf3', '').strip(),
                  'data_consumo_insumo': request.GET.get('tf4', '').strip(),
                  'qtd_perda': request.GET.get('tf5', '').strip(),
                  'mes_sped': request.GET.get('tf6', '').strip(),
                  'ano_sped': request.GET.get('tf7', '').strip(),
              }

              # Forçar filtro por empresa_id e mes_sped do botão, se existirem (eles prevalecem)
              if empresa_id_param:
                     filtros_terceiros['empresa_id'] = empresa_id_param
              if mes_sped_param:
                     filtros_terceiros['mes_sped'] = mes_sped_param

              itens_produzidos250 = ItensProduzidos250.objects.select_related('empresa')
              
              # Aplicar filtro por empresa_id (se fornecido)
              if filtros_terceiros.get('empresa_id'):
                     itens_produzidos250 = itens_produzidos250.filter(empresa_id=filtros_terceiros['empresa_id'])
              
              # Aplicar filtro por mes_sped (string mês em extenso)
              if filtros_terceiros.get('mes_sped'):
                     itens_produzidos250 = itens_produzidos250.filter(mes_sped__iexact=filtros_terceiros['mes_sped'])
              
              if filtros_terceiros['data_prod']:
                     itens_produzidos250 = itens_produzidos250.filter(data_prod__icontains=filtros_terceiros['data_prod'])
              if filtros_terceiros['cod_item']:
                     itens_produzidos250 = itens_produzidos250.filter(cod_item__icontains=filtros_terceiros['cod_item'])
              if filtros_terceiros['quantidade']:
                     itens_produzidos250 = itens_produzidos250.filter(quantidade__icontains=filtros_terceiros['quantidade'])
              if filtros_terceiros['ano_sped']:
                     itens_produzidos250 = itens_produzidos250.filter(ano_sped__icontains=filtros_terceiros['ano_sped'])

              insumos_queryset255 = InsumosUsados255.objects.select_related('empresa').order_by('data_consumo_insumo', 'registro', 'id')
              
              # Filtro por empresa_id e mes_sped também para insumos
              if filtros_terceiros.get('empresa_id'):
                     insumos_queryset255 = insumos_queryset255.filter(empresa_id=filtros_terceiros['empresa_id'])
              if filtros_terceiros.get('mes_sped'):
                     insumos_queryset255 = insumos_queryset255.filter(mes_sped__iexact=filtros_terceiros['mes_sped'])

              if filtros_terceiros['data_consumo_insumo']:
                     insumos_queryset255 = insumos_queryset255.filter(data_consumo_insumo__icontains=filtros_terceiros['data_consumo_insumo'])
              if filtros_terceiros['quantidade']:
                     insumos_queryset255 = insumos_queryset255.filter(quantidade__icontains=filtros_terceiros['quantidade'])
              if filtros_terceiros['qtd_perda']:
                     insumos_queryset255 = insumos_queryset255.filter(qtd_perda__icontains=filtros_terceiros['qtd_perda'])
              if filtros_terceiros['cod_item']:
                     insumos_queryset255 = insumos_queryset255.filter(cod_item__icontains=filtros_terceiros['cod_item'])
              if filtros_terceiros['ano_sped']:
                     insumos_queryset255 = insumos_queryset255.filter(ano_sped__icontains=filtros_terceiros['ano_sped'])

              grupos_250 = {}
              for item in itens_produzidos250:
                     chave_grupo = (item.cod_item or '',)
                     if chave_grupo not in grupos_250:
                            grupos_250[chave_grupo] = []
                     grupos_250[chave_grupo].append(item)
              grupos_250_ordenados = []
              for chave, itens_grupo in grupos_250.items():
                     itens_grupo_ordenados = sorted(itens_grupo, key=lambda x: (x.data_prod or date.min, x.registro or ''))
                     grupos_250_ordenados.append({'chave': chave, 'k250s': itens_grupo_ordenados, 'k255s': []})
              grupos_250_ordenados = sorted(grupos_250_ordenados, key=lambda g: g['chave'][0])
              todos_k255 = list(insumos_queryset255)
              k250_por_cod_item = {g['chave'][0]: g for g in grupos_250_ordenados if g['chave'][0]}
              grupos_por_empresa = {}
              for grupo in grupos_250_ordenados:
                     if grupo['k250s']:
                            eid = grupo['k250s'][0].empresa_id
                            if eid not in grupos_por_empresa:
                                   grupos_por_empresa[eid] = []
                            grupos_por_empresa[eid].append(grupo)
              for k255 in todos_k255:
                     relacionado = False
                     if k255.cod_item and k255.cod_item in k250_por_cod_item:
                            k250_por_cod_item[k255.cod_item]['k255s'].append(k255)
                            relacionado = True
                     elif k255.qtd_perda and k255.qtd_perda in k250_por_cod_item:
                            k250_por_cod_item[k255.qtd_perda]['k255s'].append(k255)
                            relacionado = True
                     if not relacionado and k255.empresa_id in grupos_por_empresa:
                            grupos_empresa = grupos_por_empresa[k255.empresa_id]
                            grupo_mais_proximo = None
                            menor_diferenca = None
                            if k255.data_consumo_insumo:
                                   for grupo in grupos_empresa:
                                          for k250 in grupo['k250s']:
                                                 if k250.data_prod:
                                                        d = abs((k255.data_consumo_insumo - k250.data_prod).days)
                                                        if menor_diferenca is None or d < menor_diferenca:
                                                               menor_diferenca = d
                                                               grupo_mais_proximo = grupo
                            if grupo_mais_proximo:
                                   grupo_mais_proximo['k255s'].append(k255)
                            elif grupos_empresa:
                                   grupos_empresa[0]['k255s'].append(k255)
              for grupo in grupos_250_ordenados:
                     grupo['k255s'] = sorted(grupo['k255s'], key=lambda x: (x.data_consumo_insumo or date.min, x.registro or '', x.id or 0))
              if filtros_terceiros['bloco']:
                     bloco_filtro = filtros_terceiros['bloco'].upper().strip()
                     grupos_filtrados_bloco_250 = []
                     for grupo in grupos_250_ordenados:
                            gf = {'chave': grupo['chave'], 'k250s': grupo['k250s'] if 'K250' in bloco_filtro and grupo['k250s'] else [], 'k255s': grupo['k255s'] if 'K255' in bloco_filtro and grupo['k255s'] else []}
                            if 'K250' not in bloco_filtro and 'K255' not in bloco_filtro:
                                   grupos_filtrados_bloco_250.append(grupo)
                            elif gf['k250s'] or gf['k255s']:
                                   grupos_filtrados_bloco_250.append(gf)
                     grupos_250_ordenados = grupos_filtrados_bloco_250
              k255_relacionados = {k255.id for grupo in grupos_250_ordenados for k255 in grupo['k255s']}
              k255_orfos = [k255 for k255 in todos_k255 if k255.id not in k255_relacionados]
              if k255_orfos:
                     k255_orfos_por_empresa = {}
                     for k255 in k255_orfos:
                            eid = k255.empresa_id
                            if eid not in k255_orfos_por_empresa:
                                   k255_orfos_por_empresa[eid] = []
                            k255_orfos_por_empresa[eid].append(k255)
                     for empresa_id, k255s_empresa in k255_orfos_por_empresa.items():
                            grupos_250_ordenados.append({'chave': ('',), 'k250s': [], 'k255s': sorted(k255s_empresa, key=lambda x: (x.data_consumo_insumo or date.min, x.registro or '', x.id or 0))})
              grupos_filtrados_250 = [g for g in grupos_250_ordenados if not (filtros_terceiros['data_consumo_insumo'] or filtros_terceiros['qtd_perda']) or g['k255s'] or g['k250s']]
              grupos_250_ordenados = grupos_filtrados_250
              paginator_terceiros = Paginator(grupos_250_ordenados, 50)
              dados_terceiros = paginator_terceiros.get_page(request.GET.get('page_terceiros', 1))
              current_query_parts_terceiros = []
              col_map_t = {'bloco': 'tf0', 'data_prod': 'tf1', 'cod_item': 'tf2', 'quantidade': 'tf3', 'data_consumo_insumo': 'tf4', 'qtd_perda': 'tf5', 'mes_sped': 'tf6', 'ano_sped': 'tf7'}
              # Inclua empresa_id e mes_sped (URL amigável para troca via botão)
              for key, value in filtros_terceiros.items():
                     if value and col_map_t.get(key):
                            current_query_parts_terceiros.append(f"{col_map_t[key]}={value}")
              if empresa_id_param:
                     current_query_parts_terceiros.append(f"empresa_id={empresa_id_param}")
              if mes_sped_param:
                     current_query_parts_terceiros.append(f"mes_sped={mes_sped_param}")
              return render(request, 'sped/view_producao_k250_k255.html', {
                     'dados_terceiros': dados_terceiros,
                     'filters_terceiros': filtros_terceiros,
                     'current_query_terceiros': '&'.join(current_query_parts_terceiros),
                     'empresa_id': empresa_id_param,
                     'mes_sped': mes_sped_param,
              })