from django.http import HttpResponseServerError
from datetime import datetime
from django.db import connection
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

class ExportarService:
    def __init__(self, data) -> None:
        self.empresa_id = data.get('empresa_id')
        self.data_sped_param = data.get('data_sped')

    def exportar_relatorio(self):

        empresa_id = self.empresa_id
        data_sped_param = self.data_sped_param

        if not empresa_id:
            return HttpResponseServerError("Empresa ID não fornecido", status=400)
        
        if not data_sped_param:
            return HttpResponseServerError("Data SPED não fornecida", status=400)

        try:
            data_sped_obj = datetime.strptime(data_sped_param, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return HttpResponseServerError("Data SPED inválida. Deve ser no formato YYYY-MM-DD.", status=400)

        query_sped = (
                "SELECT "
                "n.tipo AS tipo_nota, "                 
                "p.cnpj_cpf AS cnpj_cpf, "              
                "n.numero_nota AS numero_nota, "        
                "COALESCE(n.chave_nota, '---') AS chave_nota, "  
                "p.nome AS nome, "                      
                "n.codigo_uf AS codigo_uf, "            
                "COALESCE(pr.cfop_prod, '---') AS cfop, "  
                "pr.codigo_prod AS codigo_prod, "       
                "pr.descricao_prod AS descricao_prod, " 
                "COALESCE(pr.ncm, '---') AS ncm, "      
                "COALESCE(pr.quantidade_prod, 0) AS quantidade_prod, " 
                "COALESCE(pr.valor_unitario, 0) AS valor_unitario, "   
                "COALESCE(pr.base_icms, 0) AS base_icms, "
                "COALESCE(pr.aliquota_icms, 0) AS aliquota_icms, " 
                "COALESCE(pr.valor_icms, 0) AS valor_icms, "
                "COALESCE(pr.valor_total, 0) AS valor_total, "
                "COALESCE(pr.cst, '---') AS cst, "        
                "COALESCE(pr.cest, '---') AS cest, "  
                "COALESCE(pr.valor_ipi, 0) AS valor_ipi, "
                "COALESCE(n.tipo_operacao, '---') AS tipo_operacao, "
                "COALESCE(n.numero_documento, '---') AS numero_documento "
                "FROM validacao_participantes p "
                "LEFT JOIN validacao_notas_participantes n "
                "    ON n.cod_part = p.cod_part "
                "    AND n.empresa_id = p.empresa_id "
                "    AND n.data_inicio_sped = p.data_inicio_sped "
                "LEFT JOIN validacao_produtos_notas pr "
                "    ON pr.numero_nota = n.numero_nota "
                "    AND pr.empresa_id = n.empresa_id "
                "    AND pr.data_inicio_sped = n.data_inicio_sped "
                "    AND pr.status IN ('C/N', 'S/CADASTRO') "
                "WHERE p.empresa_id = %s "
                "    AND p.data_inicio_sped = %s "
                "    AND n.tipo IN ('Entrada', 'Saida') "
            )

        with connection.cursor() as cursor:
            cursor.execute(query_sped, [empresa_id, data_sped_obj])
            rows = cursor.fetchall()
            colunas = [
                'Tipo', 
                'CNPJ/CPF', 
                'Número Nota', 
                'Chave Nota',
                'Nome',
                'UF',
                'CFOP', 
                'Código Produto',
                'Descrição',
                'NCM',
                'Quantidade',
                'Valor Unitário',
                'Base ICMS',
                'Alíquota ICMS',
                'Valor ICMS',
                'Valor Total',
                'CST',
                'CEST',
                'Valor IPI',
                'Operação',
                'Documento',
            ]

        # Cria planilha Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Relatório Movimentações"

        # Cabeçalho
        ws.append(colunas)
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        # Dados
        for row in rows:
            ws.append(row)

        # Ajusta largura automática
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            ws.column_dimensions[column].width = max_length + 2

        # Retorna resposta HTTP (download)
        response = HttpResponseServerError(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        data_formatada = data_sped_obj.strftime("%d-%m-%Y")
        response['Content-Disposition'] = f'attachment; filename="relatorio_movimentação_{data_formatada}.xlsx"'

        wb.save(response)
        return response