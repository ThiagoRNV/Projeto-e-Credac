from metodo_rateio.utils.extract_planilha import ExtractPlanilhaCusto
from metodo_rateio.utils.normalizadores import Normalizadores
from metodo_rateio.models.planilha import PlanilhaCusto

class ProcessServices:

    def __init__(self, planilha_custo, empresa, data_referencia, empresa_id, razao_social) -> None:
        self.planilha_custo = planilha_custo
        self.empresa = empresa
        self.data_referencia = data_referencia
        self.empresa_id = empresa_id
        self.razao_social = razao_social

    def process_planilha(self):

        if not self.razao_social:
            return {'razao_social': False}

        if not self.data_referencia:
            return {'data_referencia': False}

        if not self.planilha_custo:
            return {'planilha_custo': False}

        if not self.planilha_custo.name.endswith('.xlsx'):
            return {'planilha_verificacao': False}

        dados_planilha = ExtractPlanilhaCusto(self.planilha_custo)

        if not dados_planilha.load_planilha_custo():
            return {'dados_planilha': False}

        values_planilha = dados_planilha.extract_values_planilha()
        if not values_planilha:
            return {'values_planilha': False}
        
        # Preparar lista de objetos para bulk_create (muito mais rápido)
        objetos_para_criar = []
        
        for value in values_planilha.get('planilha_custo', []):
            
            if value == 'null':
                continue
            
            colunas = [
                value.get('categoria'),
                value.get('centro_custo'),
                value.get('descricao'),
                value.get('documento_fiscal'),
                value.get('fornecedor'),
                value.get('conta_contabil'),
                value.get('valor_total'),
                value.get('percentual_aplicado'),
                value.get('valor_alocado'),
                value.get('icms_passivel_credito'),
            ]
            
            tem_valor = False
            for coluna in colunas:
                if isinstance(coluna, (int, float)):
                    tem_valor = True
                    break
                elif isinstance(coluna, str):
                    if coluna.strip() != '' and coluna.lower() != 'null':
                        tem_valor = True
                        break
                # Se não for None, considera válido
                elif coluna is not None:
                    tem_valor = True
                    break
            
            if not tem_valor:
                continue
            
            objetos_para_criar.append(
                PlanilhaCusto(
                    empresa=self.razao_social,
                    data_referencia=self.data_referencia,
                    categoria=value.get('categoria'),
                    centro_custo=value.get('centro_custo'),
                    descricao=value.get('descricao'),
                    documento_fiscal=value.get('documento_fiscal'),
                    fornecedor=value.get('fornecedor'),
                    conta_contabil=value.get('conta_contabil'),
                    valor_total=Normalizadores.normalizador_decimal(value.get('valor_total')),
                    percentual_aplicado=Normalizadores.normalizador_decimal(value.get('percentual_aplicado')),
                    valor_alocado=Normalizadores.normalizador_decimal(value.get('valor_alocado')),
                    icms_passivel_credito=Normalizadores.normalizador_decimal(value.get('icms_passivel_credito')),
                )
            )
        
        if objetos_para_criar:
            PlanilhaCusto.objects.bulk_create(objetos_para_criar, batch_size=1000)
        
        return {'sucess': True}
            