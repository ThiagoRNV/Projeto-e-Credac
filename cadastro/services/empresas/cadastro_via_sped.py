from this import d
from typing import Any, Dict
from cadastro.utils.extract_sped import SPEDcadastroUtils
from cadastro.models.empresa import Empresa

class EmpresaViaSpedServices:

    def __init__(self, sped_file):
        self.sped_file = sped_file

    def create_job_sped(self) -> Dict[str, Any]:
        
        dados_empresa = self.sped_file 

        sped_processor = SPEDcadastroUtils(dados_empresa)
        
        if sped_processor.load_sped_file():
            dados_sped = sped_processor.extract_value_job()
        else:
            dados_sped = None   

        empresa_dados = dados_sped.get('dados_empresa', [])
        razao_social = empresa_dados.get('razao_social', [])
        try:
            Empresa.objects.get_or_create(
                cnpj=empresa_dados.get('cnpj'),
                defaults={
                    'ladca': empresa_dados.get('ladca', ''),
                    'cod_ver': empresa_dados.get('cod_ver', ''),
                    'cod_fin': empresa_dados.get('cod_fin', ''), 
                    'razao_social': razao_social,
                    'cnpj': empresa_dados.get('cnpj', ''),
                    'inscricao_estadual': empresa_dados.get('inscricao_estadual', ''),
                    'uf': empresa_dados.get('uf', ''),  
                    'codigo_municipio': empresa_dados.get('codigo_municipio', ''),
                    'opc_cred_outorgado': empresa_dados.get('opc_cred_outorgado'),
                    'inscricao_estadual_intima': empresa_dados.get('inscricao_estadual_intima'),
                    'configuracao': empresa_dados.get('configuracao', ''),
                    'nome_fantasia': empresa_dados.get('nome_fantasia', ''),
                    'cep': empresa_dados.get('cep', ''),
                    'endereco': empresa_dados.get('endereco', ''),
                    'numero_endereco': empresa_dados.get('numero_endereco', ''),
                    'bairro': empresa_dados.get('bairro', ''),
                    'telefone': empresa_dados.get('telefone', ''),
                    'telefone': empresa_dados.get('telefone', ''),
                    'email': empresa_dados.get('email', ''),
                    'indicador_perfil': empresa_dados.get('ind_perfil', ''),
                    'indicador_movimento': empresa_dados.get('indicador_movimento', ''),
                    'indicador_atividade': empresa_dados.get('ind_atividade', '')
                }

            )
            
            return {'processamento_concluido': True, 'razao_social': razao_social}

        except Exception as e:
            print(f'Erro no cadastro {e}')


