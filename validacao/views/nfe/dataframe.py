from csv import Error
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseServerError
from datetime import datetime
from decimal import Decimal
from django.db import connection
from django.core.paginator import Paginator
from urllib.parse import urlencode
import json
import pandas as pd
from django.http import JsonResponse
from validacao.services.nfe.dataframe.salvar_service import ErrorJson, ErrorSave, JsonInvalid
from cadastro.models.empresa import Empresa
from validacao.services.nfe.dataframe.salvar_service import SalvarEdicaoService
from validacao.services.nfe.dataframe.exportar_service import ExportarService
from validacao.utils.normalizadores import _to_decimal

class DataFrame(View):

    def get(self, request):
        empresa_id_param = request.GET.get('empresa_id')
        data_sped_param = request.GET.get('data_sped')

        razao_social = Empresa.objects.filter(id=empresa_id_param).values_list('razao_social', flat=True).first()

        if not empresa_id_param:
            return HttpResponseServerError("Empresa ID não fornecido", status=400)
        try:
            empresa_id = int(empresa_id_param)
        except (TypeError, ValueError):
            return HttpResponseServerError("Empresa ID inválido", status=400)

        data_sped_obj = None
        if data_sped_param:
            try:
                data_sped_obj = datetime.strptime(data_sped_param, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return HttpResponseServerError("Data SPED inválida. Deve ser no formato YYYY-MM-DD.", status=400)

        # ✅ Se data_sped não foi fornecida, retornar erro (obrigatória para evitar mistura de meses)
        if not data_sped_obj:
            return HttpResponseServerError("Data SPED é obrigatória. Forneça o parâmetro data_sped no formato YYYY-MM-DD.", status=400)

        filtros = {
            'tipo': request.GET.get('tipo') or '',
            'cnpj_cpf': request.GET.get('cnpj_cpf') or '',
            'numero_nota': request.GET.get('numero_nota') or '',
            'chave_nota': request.GET.get('chave_nota') or '',
            'nome': request.GET.get('nome') or '',
            'codigo_uf': request.GET.get('codigo_uf') or '',
            'cfop_prod': request.GET.get('cfop_prod') or '',
            'codigo_prod': request.GET.get('codigo_prod') or '',
            'descricao_prod': request.GET.get('descricao_prod') or '',
            'ncm': request.GET.get('ncm') or '',
            'quantidade_prod': request.GET.get('quantidade_prod') or '',
            'valor_unitario': request.GET.get('valor_unitario') or '',
            'valor_icms': request.GET.get('valor_icms') or '',
            'aliquota_icms': request.GET.get('aliquota_icms') or '',
            'valor_ipi': request.GET.get('valor_ipi') or '',
            'valor_total': request.GET.get('valor_total') or '',
            'cst': request.GET.get('cst') or '',
            'cest': request.GET.get('cest') or '',
            'data_inicio_sped': request.GET.get('data_inicio_sped') or '',
            'tipo_operacao': request.GET.get('tipo_operacao') or '',
            'numero_documento': request.GET.get('numero_documento') or '',
        }

        query_sped = (
            "SELECT "
            "  p.nome AS nome, "
            "  p.cnpj_cpf AS cnpj_cpf, "
            "  p.cod_part AS cod_part, "
            "  n.tipo AS tipo_nota, "
            "  n.id AS nota_id, "
            "  n.numero_nota AS numero_nota, "
            "  n.codigo_uf AS codigo_uf, "
            "  n.chave_nota AS chave_nota, "
            "  COALESCE(n.tipo_operacao, '') AS tipo_operacao, "
            "  COALESCE(n.numero_documento, '') AS numero_documento, "
            "  pr.codigo_prod AS codigo_prod, "
            "  pr.descricao_prod AS descricao_prod, "
            "  pr.ncm AS ncm, "
            "  pr.quantidade_prod AS quantidade_prod, "
            "  pr.valor_unitario AS valor_unitario, "
            "  COALESCE(pr.valor_total, 0) AS valor_total, "
            "  COALESCE(pr.base_icms, 0) AS base_icms, "
            "  COALESCE(pr.valor_icms, 0) AS valor_icms, "
            "  COALESCE(pr.aliquota_icms, 0) AS aliquota_icms, "
            "  COALESCE(pr.cst, '---') AS cst, "
            "  COALESCE(pr.cest, '---') AS cest, "
            "  COALESCE(pr.valor_ipi, 0) AS valor_ipi, "
            "  COALESCE(pr.cfop_prod, '---') AS cfop_prod "
            "FROM validacao_participantes AS p "
            "INNER JOIN validacao_notas_participantes AS n "
            "  ON n.part_titular_id = p.id "
            "INNER JOIN validacao_produtos_notas AS pr "
            "  ON pr.nota_titular_id = n.id "
            "WHERE p.empresa_id = %s "
            "  AND p.data_inicio_sped = %s "
            "  AND n.tipo IS NOT NULL "
            "  AND pr.status IN ('C/N', 'S/CADASTRO') "
        )
        params = [empresa_id, data_sped_param]

        def like(val):
            return f"%{val}%"

        if filtros['tipo']:
            query_sped += " AND UPPER(n.tipo) LIKE UPPER(%s)"
            params.append(like(filtros['tipo']))
        if filtros['cnpj_cpf']:
            query_sped += " AND UPPER(p.cnpj_cpf) LIKE UPPER(%s)"
            params.append(like(filtros['cnpj_cpf']))
        if filtros['numero_nota']:
            query_sped += " AND UPPER(n.numero_nota) LIKE UPPER(%s)"
            params.append(like(filtros['numero_nota']))
        if filtros['chave_nota']:
            query_sped += " AND UPPER(n.chave_nota) LIKE UPPER(%s)"
            params.append(like(filtros['chave_nota']))
        if filtros['nome']:
            query_sped += " AND UPPER(p.nome) LIKE UPPER(%s)"
            params.append(like(filtros['nome']))
        if filtros['codigo_uf']:
            query_sped += " AND UPPER(n.codigo_uf) LIKE UPPER(%s)"
            params.append(like(filtros['codigo_uf']))
        if filtros['cfop_prod']:
            query_sped += " AND UPPER(pr.cfop_prod) LIKE UPPER(%s)"
            params.append(like(filtros['cfop_prod']))
        if filtros['codigo_prod']:
            query_sped += " AND UPPER(pr.codigo_prod) LIKE UPPER(%s)"
            params.append(like(filtros['codigo_prod']))
        if filtros['descricao_prod']:
            query_sped += " AND UPPER(pr.descricao_prod) LIKE UPPER(%s)"
            params.append(like(filtros['descricao_prod']))
        if filtros['ncm']:
            query_sped += " AND UPPER(pr.ncm) LIKE UPPER(%s)"
            params.append(like(filtros['ncm']))
        if filtros['quantidade_prod']:
            query_sped += " AND CAST(pr.quantidade_prod AS TEXT) LIKE %s"
            params.append(like(filtros['quantidade_prod']))
        if filtros['valor_unitario']:
            query_sped += " AND CAST(pr.valor_unitario AS TEXT) LIKE %s"
            params.append(like(filtros['valor_unitario']))
        if filtros['valor_icms']:
            query_sped += " AND CAST(pr.valor_icms AS TEXT) LIKE %s"
            params.append(like(filtros['valor_icms']))
        if filtros['aliquota_icms']:
            query_sped += " AND CAST(pr.aliquota_icms AS TEXT) LIKE %s"
            params.append(like(filtros['aliquota_icms']))
        if filtros['valor_total']:
            query_sped += " AND CAST(pr.valor_total AS TEXT) LIKE %s"
            params.append(like(filtros['valor_total']))
        if filtros['cst']:
            query_sped += " AND UPPER(pr.cst) LIKE UPPER(%s)"
            params.append(like(filtros['cst']))
        if filtros['cest']:
            query_sped += " AND UPPER(pr.cest) LIKE UPPER(%s)"
            params.append(like(filtros['cest']))
        if filtros['valor_ipi']:
            query_sped += " AND CAST(pr.valor_ipi AS TEXT) LIKE %s"
            params.append(like(filtros['valor_ipi']))
        if filtros['data_inicio_sped']:
            try:
                data_filtro = datetime.strptime(filtros['data_inicio_sped'], '%Y-%m-%d').date()
                # ✅ Só adicionar se for diferente da data_sped principal (caso contrário é redundante)
                if data_filtro != data_sped_obj:
                    query_sped += " AND pr.data_inicio_sped = %s"
                    params.append(data_filtro)
            except (ValueError, TypeError):
                pass 
        if filtros['tipo_operacao']:
            query_sped += " AND UPPER(n.tipo_operacao) LIKE UPPER(%s)"
            params.append(like(filtros['tipo_operacao']))
        if filtros['numero_documento']:
            query_sped += " AND UPPER(n.numero_documento) LIKE UPPER(%s)"
            params.append(like(filtros['numero_documento']))

        busca = (request.GET.get('busca') or '').strip()
        if busca:
            busca_like = like(busca)
            query_sped += (
                " AND ("
                "UPPER(p.nome) LIKE UPPER(%s) OR "
                "UPPER(p.cnpj_cpf) LIKE UPPER(%s) OR "
                "UPPER(n.numero_nota) LIKE UPPER(%s) OR "
                "UPPER(n.chave_nota) LIKE UPPER(%s) OR "
                "UPPER(pr.codigo_prod) LIKE UPPER(%s) OR "
                "UPPER(pr.descricao_prod) LIKE UPPER(%s) OR "
                "UPPER(pr.ncm) LIKE UPPER(%s) OR "
                "UPPER(pr.cfop_prod) LIKE UPPER(%s)"
                ")"
            )
            params.extend([busca_like] * 8)


        # Executar query do zero a cada requisição (stateless)
        # A query SQL já filtra corretamente por data_inicio_sped, não precisa de filtro adicional
        dados_sped_query = pd.read_sql_query(query_sped, connection, params=params).to_dict(orient="records")

        try:
            per_page = int(request.GET.get('per_page', 10))
        except (TypeError, ValueError):
            per_page = 10
        if per_page not in (10, 25, 50, 100):
            per_page = 10

        paginator = Paginator(dados_sped_query, per_page)
        pagina_atual = request.GET.get('page', 1)
        dados_pag = paginator.get_page(pagina_atual)

        total_valor_total_geral = sum(_to_decimal(item.get("valor_total")) for item in dados_sped_query)
        total_valor_ipi_geral = sum(_to_decimal(item.get("valor_ipi")) for item in dados_sped_query)
        total_valor_icms_geral = sum(_to_decimal(item.get("valor_icms")) for item in dados_sped_query)

        total_valor_total_pagina = sum(_to_decimal(item.get("valor_total")) for item in dados_pag)
        total_valor_ipi_pagina = sum(_to_decimal(item.get("valor_ipi")) for item in dados_pag)
        total_valor_icms_pagina = sum(_to_decimal(item.get("valor_icms")) for item in dados_pag)
        
        if total_valor_icms_pagina != total_valor_icms_pagina:
            total_valor_icms_pagina = Decimal("0")
        if total_valor_total_pagina != total_valor_total_pagina:
            total_valor_total_pagina = Decimal("0")
        if total_valor_ipi_pagina != total_valor_ipi_pagina:
            total_valor_ipi_pagina = Decimal("0")
        if total_valor_icms_geral != total_valor_icms_geral:
            total_valor_icms_geral = Decimal("0")
        if total_valor_total_geral != total_valor_total_geral:
            total_valor_total_geral = Decimal("0")
        if total_valor_ipi_geral != total_valor_ipi_geral:
            total_valor_ipi_geral = Decimal("0")

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
        current_query_str = urlencode(current_query)

        def query_url(extra=None, exclude_page=False):
            params = dict(current_query)
            if exclude_page:
                params.pop('page', None)
            if extra:
                params.update(extra)
            return '?' + urlencode(params)

        somente_visualizacao = request.GET.get('modo') == 'visualizacao'
        contexto = {
            'texto': f'{razao_social} - NF-es',
            'somente_visualizacao': somente_visualizacao,
        }
        
        mes_number = data_sped_obj.month

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

        mes_sped = meses_dict.get(mes_number)
        return render(request, 'mercadorias_nfe/view_data.html', {
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
            "total_valor_total_geral": total_valor_total_geral,
            "total_valor_ipi_geral": total_valor_ipi_geral,
            "total_valor_icms_geral": total_valor_icms_geral,
            "total_valor_total_pagina": total_valor_total_pagina,
            "total_valor_ipi_pagina": total_valor_ipi_pagina,
            "total_valor_icms_pagina": total_valor_icms_pagina,
            **contexto
        })

    def post (self, request):

        data = json.loads(request.body.decode("utf-8"))
        opcs = data.get('opcs')
        user = request.user.id

        if opcs == 'salvar':
            return self.salvar_edicoes(data, user)
        elif opcs == 'exportar':
            return self.exportar_relatorio(data)
        else:
            return HttpResponseServerError('Não foi possível realizar sua solicitação. Favor entrar em contato com o suporte.', status=500)

# ------------------------------------------------------------------------------------------------------------------------------------ #

    """  MÉTODO PARA SALVAR EDIÇÕES NO DATAFRAME """
    def salvar_edicoes(self, data, user):
        try:
            items = data.get("items", [])
            empresa_id = data.get("empresa_id")
            user_id = user
            
            service = SalvarEdicaoService(items, empresa_id, user_id).process_salvar()

            process_ok = service.get('success')

            if process_ok:
                return JsonResponse(
                {
                    "status": "ok", 
                    "message": "itens salvos com sucesso"
                }, status=200
            )

        except ErrorSave:
            return JsonResponse(
               {
                "status": "error", "message": "adadsadsa"
               },status=500
            )
        except JsonInvalid as e:
            return JsonResponse(
                {
                    "status": "error", 
                    "message": f"JSON inválido: {str(e)}"
                }, status=400
            )
        except ErrorJson as e:
            return JsonResponse(
                {"status": "error", 
                "message": f"Erro ao salvar: {str(e)}"
                }, status=500
            )



# ------------------------------------------------------------------------------------------------------------------------------------ #

    def exportar_relatorio(self, request):
      
      service = ExportarService(request.POST)

      return service.exportar_relatorio()


