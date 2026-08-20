from cadastro.models.empresa import Empresa

class EmpresaManualmenteServices:
    
    def __init__(self, data):
        self.data = data

    def create_job(self):
        try:
            Empresa.objects.create(
                razao_social=self.data.get('razao_social'),
                email=self.data.get('email'),
                cnpj=self.data.get('cnpj'),
                cnae=self.data.get('cnae'),
                inscricao_estadual=self.data.get('inscricao_estadual'),
                inscricao_estadual_intima=self.data.get('inscricao_estadual_intima'),
                ladca=self.data.get('ladca'),
                cod_ver=self.data.get('cod_ver'),
                cod_fin=self.data.get('cod_fin'),
                opc_cred_outorgado=self.data.get('opc_cred_outorgado'),
                uf=self.data.get('uf'),
                indicador_atividade=self.data.get('indicador_atividade'),
                indicador_movimento=self.data.get('indicador_movimento'),
                configuracao=self.data.get('configuracao'),
                codigo_municipio=self.data.get('codigo_municipio'),
                nome_fantasia=self.data.get('nome_fantasia'),
                cep=self.data.get('cep'),
                endereco=self.data.get('endereco'),
                numero_endereco=self.data.get('numero_endereco'),
                complemento=self.data.get('complemento'),
                bairro=self.data.get('bairro'),
                telefone=self.data.get('telefone'),
                metodo_rateio=self.data.get('metodo_rateio'),
            )
            return {'sucess': True}

        except Exception as e:
            return {'sucess': False, 'error': str(e)}
            