from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.core.paginator import Paginator
from urllib.parse import urlencode
from datetime import datetime
import json

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

from validacao.utils.normalizadores import _to_decimal
from cadastro.models.empresa import Empresa
from validacao.services.outros_modelos.dataframe.salvar_servico import SalvarDadosServico
from validacao.services.outros_modelos.dataframe.exportar_dados import ExportarServices 
import logging

logger = logging.getLogger(__name__)

class DataFrameServicos(View):

    def get(self, request):
        empresa_id_param = request.GET.get('empresa_id')
        data_sped_param = request.GET.get('data_sped')

        razao_social = Empresa.objects.filter(id=empresa_id_param).values_list('razao_social', flat=True).first()

        if not empresa_id_param:
            return HttpResponse("Empresa ID não fornecido", status=400)
        try:
            empresa_id = int(empresa_id_param)
        except (TypeError, ValueError):
            return HttpResponse("Empresa ID inválido", status=400)

        data_sped_obj = None
        if data_sped_param:
            try:
                data_sped_obj = datetime.strptime(data_sped_param, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return HttpResponse("Data SPED inválida. Deve ser no formato YYYY-MM-DD.", status=400)

        if not data_sped_obj:
            return HttpResponse("Data SPED é obrigatória. Forneça o parâmetro data_sped no formato YYYY-MM-DD.", status=400)

        filtros = {
            'cnpj_cpf': request.GET.get('cnpj_cpf') or '',
            'nome': request.GET.get('nome') or '',
            'num_doc': request.GET.get('num_doc') or '',
            'chv_cte': request.GET.get('chv_cte') or '',
            'ser': request.GET.get('ser') or '',
            'dt_doc': request.GET.get('dt_doc') or '',
            'cfop': request.GET.get('cfop') or '',
            'cst_icms': request.GET.get('cst_icms') or '',
            'aliq_icms': request.GET.get('aliq_icms') or '',
            'vl_opr': request.GET.get('vl_opr') or '',
            'vl_bc_icms': request.GET.get('vl_bc_icms') or '',
            'vl_icms': request.GET.get('vl_icms') or '',
            'vl_red_bc': request.GET.get('vl_red_bc') or '',
            'vl_doc': request.GET.get('vl_doc') or '',
            'vl_serv': request.GET.get('vl_serv') or '',
            'cod_obs': request.GET.get('cod_obs') or '',
        }

        query_sped = (
            "SELECT "
            "  p.nome AS nome, "
            "  p.cnpj_cpf AS cnpj_cpf, "
            "  p.cod_part AS cod_part, "
            "  d.id AS d100_id, "
            "  a.id AS d190_id, "
            "  COALESCE(d.reg, 'D100') AS reg_d100, "
            "  COALESCE(a.reg, 'D190') AS reg_d190, "
            "  CASE d.ind_oper WHEN '0' THEN 'Entrada' WHEN '1' THEN 'Saida' ELSE '---' END AS tipo_nota, "
            "  d.num_doc AS num_doc, "
            "  COALESCE(d.chv_cte, '---') AS chv_cte, "
            "  COALESCE(d.ser, '---') AS ser, "
            "  d.dt_doc AS dt_doc, "
            "  COALESCE(d.vl_doc, 0) AS vl_doc, "
            "  COALESCE(d.vl_serv, 0) AS vl_serv, "
            "  COALESCE(a.cfop, '---') AS cfop, "
            "  COALESCE(a.cst_icms, '---') AS cst_icms, "
            "  COALESCE(a.aliq_icms, 0) AS aliq_icms, "
            "  COALESCE(a.vl_opr, 0) AS vl_opr, "
            "  COALESCE(a.vl_bc_icms, 0) AS vl_bc_icms, "
            "  COALESCE(a.vl_icms, 0) AS vl_icms, "
            "  COALESCE(a.vl_red_bc, 0) AS vl_red_bc, "
            "  COALESCE(a.cod_obs, '---') AS cod_obs "
            "FROM validacao_registrotransported100 AS d "
            "LEFT JOIN validacao_participantes AS p "
            "  ON d.cod_part_id = p.id "
            "INNER JOIN validacao_registrotransported190 AS a "
            "  ON a.registro_d100_id = d.id "
            "WHERE d.empresa_id = %s "
            "  AND d.data_inicio_sped = %s "
        )
        params = [empresa_id, data_sped_param]

        def like(val):
            return f"%{val}%"

        if filtros['cnpj_cpf']:
            query_sped += " AND UPPER(p.cnpj_cpf) LIKE UPPER(%s)"
            params.append(like(filtros['cnpj_cpf']))
        if filtros['nome']:
            query_sped += " AND UPPER(p.nome) LIKE UPPER(%s)"
            params.append(like(filtros['nome']))
        if filtros['num_doc']:
            query_sped += " AND CAST(d.num_doc AS TEXT) LIKE %s"
            params.append(like(filtros['num_doc']))
        if filtros['chv_cte']:
            query_sped += " AND UPPER(d.chv_cte) LIKE UPPER(%s)"
            params.append(like(filtros['chv_cte']))
        if filtros['ser']:
            query_sped += " AND UPPER(d.ser) LIKE UPPER(%s)"
            params.append(like(filtros['ser']))
        if filtros['dt_doc']:
            query_sped += " AND CAST(d.dt_doc AS TEXT) LIKE %s"
            params.append(like(filtros['dt_doc']))
        if filtros['cfop']:
            query_sped += " AND UPPER(a.cfop) LIKE UPPER(%s)"
            params.append(like(filtros['cfop']))
        if filtros['cst_icms']:
            query_sped += " AND UPPER(a.cst_icms) LIKE UPPER(%s)"
            params.append(like(filtros['cst_icms']))
        if filtros['aliq_icms']:
            query_sped += " AND CAST(a.aliq_icms AS TEXT) LIKE %s"
            params.append(like(filtros['aliq_icms']))
        if filtros['vl_opr']:
            query_sped += " AND CAST(a.vl_opr AS TEXT) LIKE %s"
            params.append(like(filtros['vl_opr']))
        if filtros['vl_bc_icms']:
            query_sped += " AND CAST(a.vl_bc_icms AS TEXT) LIKE %s"
            params.append(like(filtros['vl_bc_icms']))
        if filtros['vl_icms']:
            query_sped += " AND CAST(a.vl_icms AS TEXT) LIKE %s"
            params.append(like(filtros['vl_icms']))
        if filtros['vl_red_bc']:
            query_sped += " AND CAST(a.vl_red_bc AS TEXT) LIKE %s"
            params.append(like(filtros['vl_red_bc']))
        if filtros['vl_doc']:
            query_sped += " AND CAST(d.vl_doc AS TEXT) LIKE %s"
            params.append(like(filtros['vl_doc']))
        if filtros['vl_serv']:
            query_sped += " AND CAST(d.vl_serv AS TEXT) LIKE %s"
            params.append(like(filtros['vl_serv']))
        if filtros['cod_obs']:
            query_sped += " AND UPPER(a.cod_obs) LIKE UPPER(%s)"
            params.append(like(filtros['cod_obs']))

        busca = (request.GET.get('busca') or '').strip()
        if busca:
            busca_like = like(busca)
            query_sped += (
                " AND ("
                "UPPER(p.nome) LIKE UPPER(%s) OR "
                "UPPER(p.cnpj_cpf) LIKE UPPER(%s) OR "
                "CAST(d.num_doc AS TEXT) LIKE %s OR "
                "UPPER(d.chv_cte) LIKE UPPER(%s) OR "
                "UPPER(a.cfop) LIKE UPPER(%s) OR "
                "UPPER(a.cst_icms) LIKE UPPER(%s)"
                ")"
            )
            params.extend([busca_like] * 6)

        # Hierarquia: participante (cod_part) -> D100 -> D190
        query_sped += " ORDER BY p.cod_part, d.id, a.id"

        dados_sped_query = pd.read_sql_query(query_sped, connection, params=params).to_dict(orient="records")

        # Agrupa em hierarquia: cada documento D100 com a lista dos seus D190
        documentos = []
        documentos_por_id = {}
        for row in dados_sped_query:
            d100_id = row.get('d100_id')
            doc = documentos_por_id.get(d100_id)
            if doc is None:
                doc = {
                    'reg': row.get('reg_d100'),
                    'd100_id': d100_id,
                    'cod_part': row.get('cod_part'),
                    'nome': row.get('nome'),
                    'cnpj_cpf': row.get('cnpj_cpf'),
                    'tipo_nota': row.get('tipo_nota'),
                    'num_doc': row.get('num_doc'),
                    'chv_cte': row.get('chv_cte'),
                    'ser': row.get('ser'),
                    'dt_doc': row.get('dt_doc'),
                    'vl_doc': row.get('vl_doc'),
                    'vl_serv': row.get('vl_serv'),
                    'd190s': [],
                }
                documentos_por_id[d100_id] = doc
                documentos.append(doc)
            doc['d190s'].append({
                'reg': row.get('reg_d190'),
                'd190_id': row.get('d190_id'),
                'cfop': row.get('cfop'),
                'cst_icms': row.get('cst_icms'),
                'aliq_icms': row.get('aliq_icms'),
                'vl_opr': row.get('vl_opr'),
                'vl_bc_icms': row.get('vl_bc_icms'),
                'vl_icms': row.get('vl_icms'),
                'vl_red_bc': row.get('vl_red_bc'),
                'cod_obs': row.get('cod_obs'),
            })

        # ------------------------------- Energia (C500 -> C590) ------------------------------- #

        campos_filtro_energia = [
            'cnpj_cpf', 'nome', 'num_doc', 'chv_doce', 'ser', 'dt_doc',
            'cfop', 'cst_icms', 'aliq_icms', 'vl_opr', 'vl_bc_icms', 'vl_icms',
            'vl_bc_icms_st', 'vl_icms_st', 'vl_red_bc', 'vl_doc', 'vl_forn', 'cod_obs',
        ]
        filtros_energia = {campo: request.GET.get(f'en_{campo}') or '' for campo in campos_filtro_energia}

        query_energia = (
            "SELECT "
            "  p.nome AS nome, "
            "  p.cnpj_cpf AS cnpj_cpf, "
            "  p.cod_part AS cod_part, "
            "  c.id AS c500_id, "
            "  a.id AS c590_id, "
            "  COALESCE(c.reg, 'C500') AS reg_c500, "
            "  COALESCE(a.reg, 'C590') AS reg_c590, "
            "  CASE c.ind_oper WHEN '0' THEN 'Entrada' WHEN '1' THEN 'Saida' ELSE '---' END AS tipo_nota, "
            "  c.num_doc AS num_doc, "
            "  COALESCE(c.chv_doce, '---') AS chv_doce, "
            "  COALESCE(c.ser, '---') AS ser, "
            "  c.dt_doc AS dt_doc, "
            "  COALESCE(c.vl_doc, 0) AS vl_doc, "
            "  COALESCE(c.vl_forn, 0) AS vl_forn, "
            "  COALESCE(a.cfop, '---') AS cfop, "
            "  COALESCE(a.cst_icms, '---') AS cst_icms, "
            "  COALESCE(a.aliq_icms, 0) AS aliq_icms, "
            "  COALESCE(a.vl_opr, 0) AS vl_opr, "
            "  COALESCE(a.vl_bc_icms, 0) AS vl_bc_icms, "
            "  COALESCE(a.vl_icms, 0) AS vl_icms, "
            "  COALESCE(a.vl_bc_icms_st, 0) AS vl_bc_icms_st, "
            "  COALESCE(a.vl_icms_st, 0) AS vl_icms_st, "
            "  COALESCE(a.vl_red_bc, 0) AS vl_red_bc, "
            "  COALESCE(a.cod_obs, '---') AS cod_obs "
            "FROM validacao_registroenergiac500 AS c "
            "LEFT JOIN validacao_participantes AS p "
            "  ON c.cod_part_id = p.id "
            "INNER JOIN validacao_registroenergiac590 AS a "
            "  ON a.registro_c500_id = c.id "
            "WHERE c.empresa_id = %s "
            "  AND c.data_inicio_sped = %s "
        )
        params_energia = [empresa_id, data_sped_param]

        clausulas_energia = {
            'tipo': "UPPER(CASE c.ind_oper WHEN '0' THEN 'Entrada' WHEN '1' THEN 'Saida' ELSE '---' END) LIKE UPPER(%s)",
            'cnpj_cpf': "UPPER(p.cnpj_cpf) LIKE UPPER(%s)",
            'nome': "UPPER(p.nome) LIKE UPPER(%s)",
            'num_doc': "CAST(c.num_doc AS TEXT) LIKE %s",
            'chv_doce': "UPPER(c.chv_doce) LIKE UPPER(%s)",
            'ser': "UPPER(c.ser) LIKE UPPER(%s)",
            'dt_doc': "CAST(c.dt_doc AS TEXT) LIKE %s",
            'cfop': "UPPER(a.cfop) LIKE UPPER(%s)",
            'cst_icms': "UPPER(a.cst_icms) LIKE UPPER(%s)",
            'aliq_icms': "CAST(a.aliq_icms AS TEXT) LIKE %s",
            'vl_opr': "CAST(a.vl_opr AS TEXT) LIKE %s",
            'vl_bc_icms': "CAST(a.vl_bc_icms AS TEXT) LIKE %s",
            'vl_icms': "CAST(a.vl_icms AS TEXT) LIKE %s",
            'vl_bc_icms_st': "CAST(a.vl_bc_icms_st AS TEXT) LIKE %s",
            'vl_icms_st': "CAST(a.vl_icms_st AS TEXT) LIKE %s",
            'vl_red_bc': "CAST(a.vl_red_bc AS TEXT) LIKE %s",
            'vl_doc': "CAST(c.vl_doc AS TEXT) LIKE %s",
            'vl_forn': "CAST(c.vl_forn AS TEXT) LIKE %s",
            'cod_obs': "UPPER(a.cod_obs) LIKE UPPER(%s)",
        }
        for campo, clausula in clausulas_energia.items():
            if filtros_energia.get(campo):
                query_energia += f" AND {clausula}"
                params_energia.append(like(filtros_energia[campo]))

        if busca:
            busca_like = like(busca)
            query_energia += (
                " AND ("
                "UPPER(p.nome) LIKE UPPER(%s) OR "
                "UPPER(p.cnpj_cpf) LIKE UPPER(%s) OR "
                "CAST(c.num_doc AS TEXT) LIKE %s OR "
                "UPPER(c.chv_doce) LIKE UPPER(%s) OR "
                "UPPER(a.cfop) LIKE UPPER(%s) OR "
                "UPPER(a.cst_icms) LIKE UPPER(%s)"
                ")"
            )
            params_energia.extend([busca_like] * 6)

        # Hierarquia: participante (cod_part) -> C500 -> C590
        query_energia += " ORDER BY p.cod_part, c.id, a.id"

        dados_energia_query = pd.read_sql_query(query_energia, connection, params=params_energia).to_dict(orient="records")

        documentos_energia = []
        documentos_energia_por_id = {}
        for row in dados_energia_query:
            c500_id = row.get('c500_id')
            doc = documentos_energia_por_id.get(c500_id)
            if doc is None:
                doc = {
                    'reg': row.get('reg_c500'),
                    'c500_id': c500_id,
                    'cod_part': row.get('cod_part'),
                    'nome': row.get('nome'),
                    'cnpj_cpf': row.get('cnpj_cpf'),
                    'tipo_nota': row.get('tipo_nota'),
                    'num_doc': row.get('num_doc'),
                    'chv_doce': row.get('chv_doce'),
                    'ser': row.get('ser'),
                    'dt_doc': row.get('dt_doc'),
                    'vl_doc': row.get('vl_doc'),
                    'vl_forn': row.get('vl_forn'),
                    'c590s': [],
                }
                documentos_energia_por_id[c500_id] = doc
                documentos_energia.append(doc)
            doc['c590s'].append({
                'reg': row.get('reg_c590'),
                'c590_id': row.get('c590_id'),
                'cfop': row.get('cfop'),
                'cst_icms': row.get('cst_icms'),
                'aliq_icms': row.get('aliq_icms'),
                'vl_opr': row.get('vl_opr'),
                'vl_bc_icms': row.get('vl_bc_icms'),
                'vl_icms': row.get('vl_icms'),
                'vl_bc_icms_st': row.get('vl_bc_icms_st'),
                'vl_icms_st': row.get('vl_icms_st'),
                'vl_red_bc': row.get('vl_red_bc'),
                'cod_obs': row.get('cod_obs'),
            })

        # ------------------------------- Comunicação (D500 -> D590) ------------------------------- #

        campos_filtro_comunicacao = [
            'tipo', 'cnpj_cpf', 'nome', 'num_doc', 'ser', 'dt_doc',
            'cfop', 'cst_icms', 'aliq_icms', 'vl_opr', 'vl_bc_icms', 'vl_icms',
            'vl_bc_icms_st', 'vl_icms_st', 'vl_red_bc', 'vl_doc', 'vl_serv', 'cod_obs',
        ]
        filtros_comunicacao = {campo: request.GET.get(f'com_{campo}') or '' for campo in campos_filtro_comunicacao}

        query_comunicacao = (
            "SELECT "
            "  p.nome AS nome, "
            "  p.cnpj_cpf AS cnpj_cpf, "
            "  p.cod_part AS cod_part, "
            "  d.id AS d500_id, "
            "  a.id AS d590_id, "
            "  COALESCE(d.reg, 'D500') AS reg_d500, "
            "  COALESCE(a.reg, 'D590') AS reg_d590, "
            "  CASE d.ind_oper WHEN '0' THEN 'Entrada' WHEN '1' THEN 'Saida' ELSE '---' END AS tipo_nota, "
            "  d.num_doc AS num_doc, "
            "  COALESCE(d.ser, '---') AS ser, "
            "  d.dt_doc AS dt_doc, "
            "  COALESCE(d.vl_doc, 0) AS vl_doc, "
            "  COALESCE(d.vl_serv, 0) AS vl_serv, "
            "  COALESCE(a.cfop, '---') AS cfop, "
            "  COALESCE(a.cst_icms, '---') AS cst_icms, "
            "  COALESCE(a.aliq_icms, 0) AS aliq_icms, "
            "  COALESCE(a.vl_opr, 0) AS vl_opr, "
            "  COALESCE(a.vl_bc_icms, 0) AS vl_bc_icms, "
            "  COALESCE(a.vl_icms, 0) AS vl_icms, "
            "  COALESCE(a.vl_bc_icms_st, 0) AS vl_bc_icms_st, "
            "  COALESCE(a.vl_icms_st, 0) AS vl_icms_st, "
            "  COALESCE(a.vl_red_bc, 0) AS vl_red_bc, "
            "  COALESCE(a.cod_obs, '---') AS cod_obs "
            "FROM validacao_registrocomunicacaod500 AS d "
            "LEFT JOIN validacao_participantes AS p "
            "  ON d.cod_part_id = p.id "
            "INNER JOIN validacao_registrocomunicacaod590 AS a "
            "  ON a.registro_d500_id = d.id "
            "WHERE d.empresa_id = %s "
            "  AND d.data_inicio_sped = %s "
        )
        params_comunicacao = [empresa_id, data_sped_param]

        clausulas_comunicacao = {
            'tipo': "UPPER(CASE d.ind_oper WHEN '0' THEN 'Entrada' WHEN '1' THEN 'Saida' ELSE '---' END) LIKE UPPER(%s)",
            'cnpj_cpf': "UPPER(p.cnpj_cpf) LIKE UPPER(%s)",
            'nome': "UPPER(p.nome) LIKE UPPER(%s)",
            'num_doc': "CAST(d.num_doc AS TEXT) LIKE %s",
            'ser': "UPPER(d.ser) LIKE UPPER(%s)",
            'dt_doc': "CAST(d.dt_doc AS TEXT) LIKE %s",
            'cfop': "UPPER(a.cfop) LIKE UPPER(%s)",
            'cst_icms': "UPPER(a.cst_icms) LIKE UPPER(%s)",
            'aliq_icms': "CAST(a.aliq_icms AS TEXT) LIKE %s",
            'vl_opr': "CAST(a.vl_opr AS TEXT) LIKE %s",
            'vl_bc_icms': "CAST(a.vl_bc_icms AS TEXT) LIKE %s",
            'vl_icms': "CAST(a.vl_icms AS TEXT) LIKE %s",
            'vl_bc_icms_st': "CAST(a.vl_bc_icms_st AS TEXT) LIKE %s",
            'vl_icms_st': "CAST(a.vl_icms_st AS TEXT) LIKE %s",
            'vl_red_bc': "CAST(a.vl_red_bc AS TEXT) LIKE %s",
            'vl_doc': "CAST(d.vl_doc AS TEXT) LIKE %s",
            'vl_serv': "CAST(d.vl_serv AS TEXT) LIKE %s",
            'cod_obs': "UPPER(a.cod_obs) LIKE UPPER(%s)",
        }
        for campo, clausula in clausulas_comunicacao.items():
            if filtros_comunicacao.get(campo):
                query_comunicacao += f" AND {clausula}"
                params_comunicacao.append(like(filtros_comunicacao[campo]))

        if busca:
            busca_like = like(busca)
            query_comunicacao += (
                " AND ("
                "UPPER(p.nome) LIKE UPPER(%s) OR "
                "UPPER(p.cnpj_cpf) LIKE UPPER(%s) OR "
                "CAST(d.num_doc AS TEXT) LIKE %s OR "
                "UPPER(a.cfop) LIKE UPPER(%s) OR "
                "UPPER(a.cst_icms) LIKE UPPER(%s)"
                ")"
            )
            params_comunicacao.extend([busca_like] * 5)

        # Hierarquia: participante (cod_part) -> D500 -> D590
        query_comunicacao += " ORDER BY p.cod_part, d.id, a.id"

        dados_comunicacao_query = pd.read_sql_query(query_comunicacao, connection, params=params_comunicacao).to_dict(orient="records")

        documentos_comunicacao = []
        documentos_comunicacao_por_id = {}
        for row in dados_comunicacao_query:
            d500_id = row.get('d500_id')
            doc = documentos_comunicacao_por_id.get(d500_id)
            if doc is None:
                doc = {
                    'reg': row.get('reg_d500'),
                    'd500_id': d500_id,
                    'cod_part': row.get('cod_part'),
                    'nome': row.get('nome'),
                    'cnpj_cpf': row.get('cnpj_cpf'),
                    'tipo_nota': row.get('tipo_nota'),
                    'num_doc': row.get('num_doc'),
                    'ser': row.get('ser'),
                    'dt_doc': row.get('dt_doc'),
                    'vl_doc': row.get('vl_doc'),
                    'vl_serv': row.get('vl_serv'),
                    'd590s': [],
                }
                documentos_comunicacao_por_id[d500_id] = doc
                documentos_comunicacao.append(doc)
            doc['d590s'].append({
                'reg': row.get('reg_d590'),
                'd590_id': row.get('d590_id'),
                'cfop': row.get('cfop'),
                'cst_icms': row.get('cst_icms'),
                'aliq_icms': row.get('aliq_icms'),
                'vl_opr': row.get('vl_opr'),
                'vl_bc_icms': row.get('vl_bc_icms'),
                'vl_icms': row.get('vl_icms'),
                'vl_bc_icms_st': row.get('vl_bc_icms_st'),
                'vl_icms_st': row.get('vl_icms_st'),
                'vl_red_bc': row.get('vl_red_bc'),
                'cod_obs': row.get('cod_obs'),
            })

        try:
            per_page = int(request.GET.get('per_page', 10))
        except (TypeError, ValueError):
            per_page = 10
        if per_page not in (10, 25, 50, 100):
            per_page = 10

        paginator = Paginator(documentos, per_page)
        pagina_atual = request.GET.get('page', 1)
        dados_pag = paginator.get_page(pagina_atual)

        paginator_energia = Paginator(documentos_energia, per_page)
        pagina_atual_energia = request.GET.get('page_energia', 1)
        dados_pag_energia = paginator_energia.get_page(pagina_atual_energia)

        paginator_comunicacao = Paginator(documentos_comunicacao, per_page)
        pagina_atual_comunicacao = request.GET.get('page_comunicacao', 1)
        dados_pag_comunicacao = paginator_comunicacao.get_page(pagina_atual_comunicacao)

        total_vl_opr_geral = sum(_to_decimal(item.get("vl_opr")) for item in dados_sped_query)
        total_vl_icms_geral = sum(_to_decimal(item.get("vl_icms")) for item in dados_sped_query)
        # Valores do D100 contados uma vez por documento (não por linha D190)
        total_vl_serv_geral = sum(_to_decimal(doc.get("vl_serv")) for doc in documentos)

        total_vl_opr_energia = sum(_to_decimal(item.get("vl_opr")) for item in dados_energia_query)
        total_vl_icms_energia = sum(_to_decimal(item.get("vl_icms")) for item in dados_energia_query)
        # Valores do C500 contados uma vez por documento (não por linha C590)
        total_vl_forn_energia = sum(_to_decimal(doc.get("vl_forn")) for doc in documentos_energia)

        total_vl_opr_comunicacao = sum(_to_decimal(item.get("vl_opr")) for item in dados_comunicacao_query)
        total_vl_icms_comunicacao = sum(_to_decimal(item.get("vl_icms")) for item in dados_comunicacao_query)
        # Valores do D500 contados uma vez por documento (não por linha D590)
        total_vl_serv_comunicacao = sum(_to_decimal(doc.get("vl_serv")) for doc in documentos_comunicacao)

        current_query = {
            'empresa_id': empresa_id,
        }
        if data_sped_param:
            current_query['data_sped'] = data_sped_param
        if request.GET.get('modo') == 'visualizacao':
            current_query['modo'] = 'visualizacao'
        if busca:
            current_query['busca'] = busca
        current_query['per_page'] = per_page
        for k, v in filtros.items():
            if v:
                current_query[k] = v
        for k, v in filtros_energia.items():
            if v:
                current_query[f'en_{k}'] = v
        for k, v in filtros_comunicacao.items():
            if v:
                current_query[f'com_{k}'] = v
        current_query_str = urlencode(current_query)

        # Páginas atuais de cada aba, preservadas ao navegar em outra aba
        paginas_atuais = {}
        for page_param in ('page', 'page_energia', 'page_comunicacao'):
            if request.GET.get(page_param):
                paginas_atuais[page_param] = request.GET.get(page_param)

        def query_url(extra=None, exclude_page=False):
            params = dict(current_query)
            params.update(paginas_atuais)
            if exclude_page:
                params.pop('page', None)
            if extra:
                params.update(extra)
            return '?' + urlencode(params)

        somente_visualizacao = request.GET.get('modo') == 'visualizacao'

        meses_dict = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',    
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'
        }
        mes_sped = meses_dict.get(data_sped_obj.month)

        return render(request, 'outros_modelos/view_data.html', {
            "dados_sped": dados_pag,
            "empresa_id": empresa_id,
            "data_sped": data_sped_param,
            "mes_sped": mes_sped,
            "filters": filtros,
            "busca": busca,
            "current_query": current_query_str,
            "per_page": per_page,
            "prev_page_url": query_url({'page': dados_pag.previous_page_number}) if dados_pag.has_previous else None,
            "next_page_url": query_url({'page': dados_pag.next_page_number}) if dados_pag.has_next else None,
            "page_urls": [
                {
                    'number': num,
                    'url': query_url({'page': num}),
                    'is_current': num == dados_pag.number,
                }
                for num in dados_pag.paginator.page_range
            ],
            "total_registros": paginator.count,
            "total_vl_opr_geral": total_vl_opr_geral,
            "total_vl_icms_geral": total_vl_icms_geral,
            "total_vl_serv_geral": total_vl_serv_geral,

            # Energia (C500/C590)
            "dados_energia": dados_pag_energia,
            "filters_energia": filtros_energia,
            "total_registros_energia": paginator_energia.count,
            "total_vl_opr_energia": total_vl_opr_energia,
            "total_vl_icms_energia": total_vl_icms_energia,
            "total_vl_forn_energia": total_vl_forn_energia,
            "prev_page_url_energia": query_url({'page_energia': dados_pag_energia.previous_page_number}) if dados_pag_energia.has_previous else None,
            "next_page_url_energia": query_url({'page_energia': dados_pag_energia.next_page_number}) if dados_pag_energia.has_next else None,
            "page_urls_energia": [
                {
                    'number': num,
                    'url': query_url({'page_energia': num}),
                    'is_current': num == dados_pag_energia.number,
                }
                for num in dados_pag_energia.paginator.page_range
            ],

            # Comunicação (D500/D590)
            "dados_comunicacao": dados_pag_comunicacao,
            "filters_comunicacao": filtros_comunicacao,
            "total_registros_comunicacao": paginator_comunicacao.count,
            "total_vl_opr_comunicacao": total_vl_opr_comunicacao,
            "total_vl_icms_comunicacao": total_vl_icms_comunicacao,
            "total_vl_serv_comunicacao": total_vl_serv_comunicacao,
            "prev_page_url_comunicacao": query_url({'page_comunicacao': dados_pag_comunicacao.previous_page_number}) if dados_pag_comunicacao.has_previous else None,
            "next_page_url_comunicacao": query_url({'page_comunicacao': dados_pag_comunicacao.next_page_number}) if dados_pag_comunicacao.has_next else None,
            "page_urls_comunicacao": [
                {
                    'number': num,
                    'url': query_url({'page_comunicacao': num}),
                    'is_current': num == dados_pag_comunicacao.number,
                }
                for num in dados_pag_comunicacao.paginator.page_range
            ],

            "texto": f'{razao_social} - Serviços',
            "somente_visualizacao": somente_visualizacao,
        })

# ------------------------------------------------------------------------------------------------------------------------------------ #

    def post (self, request):
        if request.method != "POST":
            logger.error('Erro no método, pois era pra estar vindo o método POST e estamos recebendo outro tipo. Favor verificar')
            return HttpResponse(
                'Não foi possível fazer sua solicitação. Favor entrar em contato com o suporte.',
                status=405
                )
                
        data = json.loads(request.body)
        opcs = data.get('opcs')
        user = request.user.id

        if opcs == 'salvar':
            return self.salvar_edicoes_cte(data, user)
        elif opcs == 'exportar':
            return self.exportar_relatorio_servicos(data)
        return JsonResponse({"status": "error", "message": "Opção inválida ou ausente (opcs)"}, status=400)

# ------------------------------------------------------------------------------------------------------------------------------------- #

    def salvar_edicoes_cte(self, data, user):
        try:
            items = data.get("items", [])
            empresa_id = data.get("empresa_id")

            services = SalvarDadosServico(items, empresa_id, user)

            salvar_services = services.salvar_services()

            empresa_id_services = salvar_services.get('empresa_id')
            items_services = salvar_services.get("items")
            erros = salvar_services.get('erros')
            itens_processados = salvar_services.get('itens_processados')
            success = salvar_services.get('success')

            if empresa_id_services:
                return JsonResponse({"status": "error", "message": "Empresa ID é obrigatório"}, status=400)

            if items_services:
                return JsonResponse({"status": "error", "message": "Nenhum item para salvar"}, status=400)


            if erros:
                return JsonResponse({
                    "status": "error",
                    "message": f"Processados {itens_processados} itens. Erros: {'; '.join(erros[:3])}"
                }, status=200)
            
            if success:
                return JsonResponse({"status": "ok", "message": f"{itens_processados} itens salvos com sucesso"})

        except json.JSONDecodeError as e:
            return JsonResponse({"status": "error", "message": f"JSON inválido: {str(e)}"}, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": f"Erro ao salvar: {str(e)}"}, status=500)

# ------------------------------------------------------------------------------------------------------------------------------------ #

    def exportar_relatorio_servicos(self, data):

        empresa_id = data.get('empresa_id')
        data_sped_param = data.get('data_sped')

        services = ExportarServices(empresa_id, data_sped_param)

        exportar_service = services.exportar_service()

        empresa_id_error = exportar_service.get('empresa_id_error')
        dt_sped_error = exportar_service.get('dt_sped_error')
        formato_date = exportar_service.get('formato_date')

        if empresa_id_error:
            HttpResponse(
                'Empresa ID não fornecido. Favor entrar em contato com o suporte',
                status=400
            )
        if dt_sped_error:
            HttpResponse(
                'Data não fornecida. Favor entrar em contato com o suporte.',
                status=400
            )

        if formato_date:
            HttpResponse(
                'Formato data inválida. Favor entrar em contato com o suporte.',
                status=400
            )

        return exportar_service

