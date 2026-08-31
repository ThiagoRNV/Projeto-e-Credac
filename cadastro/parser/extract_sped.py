from typing import Dict, Any, Optional

class SPEDcadastroUtils:
    """
    Classe para processar arquivos SPED enviados via formulário (sped_files).
    """

    def __init__(self, sped_file):
        """
        :param sped_file: arquivo enviado via request.FILES['sped_files']
        """
        self.sped_file = sped_file
        self.data_sped = []
        print("Iniciando o processamento do arquivo SPED...")

    def load_sped_file(self) -> bool:
        """
            Carrega o arquivo SPED enviado e armazena cada linha em self.data_sped
        """
        try:
            self.sped_file.seek(0)  # volta para o início do arquivo
            self.data_sped = [line.decode('utf-8', errors='ignore').strip() for line in self.sped_file]
            print(f"Arquivo SPED carregado com sucesso: {len(self.data_sped)} linhas")
            return True
        except Exception as e:
            print(f"Erro ao carregar SPED: {e}")
            return False

    
    def extract_value_job (self) -> Dict[str, Any]:
        '''PROCESSA OS DADOS DA EMPRESA PARA CADASTRO'''
        print('Iniciando extração dos dados da empresa do SPED...')
        empresa = {}


        for line in self.data_sped:
            line = line.strip()
            if not line:
                continue

            # Bloco 0000 - Dados da empresa
            parts = line.strip().split('|')
            if len(parts) < 2:
                continue

            bloco = parts[1] if parts[0] == '' else parts[0]  
            
             
            if bloco == '0000':
                empresa['ladca'] = parts[2] if len(parts) > 2 else None
                empresa['cod_ver'] = parts[3] if len(parts) > 3 else None
                empresa['cod_fin'] = parts[4] if len(parts) > 4 else None
                empresa['razao_social'] = parts[6] if len(parts) > 6 else None
                empresa['cnpj'] = parts[7] if len(parts) > 7 else None
                empresa['inscricao_estadual'] = parts[8] if len(parts) > 8 else None        
                empresa['uf'] = parts[9] if len(parts) > 9 else None
                empresa['codigo_municipio'] = parts[10] if len(parts) > 10 else None
                empresa['opc_cred_outorgado'] = parts[11] if len(parts) > 11 else None
                empresa['inscricao_estadual_intima'] = parts[12] if len(parts) > 12 else None
                empresa['suframa'] = parts[13] if len(parts) > 13 else None
                empresa['ind_perfil'] = parts[14] if len(parts) > 14 else None
                empresa['ind_atividade'] = parts[15] if len(parts) > 15 else None


            elif bloco == '0001':
                empresa['indicador_movimento'] = parts[2] if len(parts) > 2 else None
       
            # Bloco 0005 - Dados complementares da empresa
            elif bloco == '0005':
                empresa['nome_fantasia'] = parts[2] if len(parts) > 2 else None
                empresa['cep'] = parts[3] if len(parts) > 3 else None
                empresa['endereco'] = parts[4] if len(parts) > 4 else None
                empresa['numero_endereco'] = parts[5] if len(parts) > 5 else None
                empresa['bairro'] = parts[6] if len(parts) > 6 else None
                empresa['telefone'] = parts[7] if len(parts) > 7 else None
                empresa['email'] = parts[8] if len(parts) > 8 else None

        return {
            'dados_empresa': empresa
        }
