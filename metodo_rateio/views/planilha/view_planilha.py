from django.shortcuts import render
from django.db import connection
import pandas as pd
from django.core.paginator import Paginator
from django.views import View


class ViewPlanilha(View):

    def get(self, request):

              query = ( 
                     "SELECT "
                     "data_referencia, "
                     "COALESCE(categoria, '---') as categoria, "
                     "COALESCE(centro_custo, '---') as centro_custo, "
                     "COALESCE(descricao, '---') as descricao, "
                     "COALESCE(documento_fiscal, '---') as documento_fiscal, "
                     "COALESCE(fornecedor, '---') as fornecedor, "
                     "COALESCE(conta_contabil, '---') as conta_contabil, "
                     "COALESCE(valor_total, 0) as valor_total, "
                     "COALESCE(percentual_aplicado, 0) as percentual_aplicado, "
                     "COALESCE(valor_alocado, 0) as valor_alocado, "
                     "COALESCE(icms_passivel_credito, 0) as icms_passivel_credito "
                     "FROM metodo_rateio_planilhacusto "
              ) 

              dados_query = pd.read_sql_query(query, connection).to_dict(orient="records")
              paginator = Paginator(dados_query, 100)
              pagina_atual = request.GET.get('page', 1)
              dados_query = paginator.get_page(pagina_atual)

              # Query para calcular totais agrupados por descrição
              query_totais = (
                     "SELECT "
                     "COALESCE(descricao, categoria, '---') as descricao, "
                     "COALESCE(categoria, '---') as categoria, "
                     "SUM(COALESCE(valor_total, 0)) as valor_total, "
                     "SUM(COALESCE(valor_alocado, 0)) as valor_alocado, "
                     "SUM(COALESCE(icms_passivel_credito, 0)) as icms_passivel_credito "
                     "FROM metodo_rateio_planilhacusto "
                     "WHERE descricao IS NOT NULL AND descricao != '---' "
                     "AND categoria = 'Serviço' "
                     "GROUP BY descricao, categoria "
                     "ORDER BY descricao"
              )

              totais = pd.read_sql_query(query_totais, connection).to_dict(orient="records")
              
              # Totais gerais (apenas para categoria Serviço)
              query_geral = (
                     "SELECT "
                     "SUM(COALESCE(valor_total, 0)) as valor_total, "
                     "SUM(COALESCE(valor_alocado, 0)) as valor_alocado, "
                     "SUM(COALESCE(icms_passivel_credito, 0)) as icms_passivel_credito "
                     "FROM metodo_rateio_planilhacusto "
                     "WHERE categoria = 'Serviço'"
              )
              
              totais_geral = pd.read_sql_query(query_geral, connection).to_dict(orient="records")
              totais_geral = totais_geral[0] if totais_geral else {}

              return render(request, 'view_analisePlanilha.html', {
                     'dados_query': dados_query,
                     'totais': totais,
                     'totais_geral': totais_geral,
              })
