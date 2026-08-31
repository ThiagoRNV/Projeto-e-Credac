class UpdateServices:

    def __init__(self, data, empresa):
        self.data = data
        self.empresa = empresa

    def editar_job(self):
        try:
            self.empresa.razao_social = self.data.get('razao_social')
            self.empresa.email = self.data.get('email')
            self.empresa.cnpj = self.data.get('cnpj')
            self.empresa.cnae = self.data.get('cnae')
            self.empresa.inscricao_estadual = self.data.get('inscricao_estadual')
            self.empresa.inscricao_estadual_intima = self.data.get('inscricao_estadual_intima')
            self.empresa.ladca = self.data.get('ladca')
            self.empresa.cod_ver = self.data.get('cod_ver')
            self.empresa.cod_fin = self.data.get('cod_fin')
            self.empresa.opc_cred_outorgado = self.data.get('opc_cred_outorgado')
            self.empresa.uf = self.data.get('uf')
            self.empresa.indicador_atividade = self.data.get('indicador_atividade')
            self.empresa.indicador_movimento = self.data.get('indicador_movimento')
            self.empresa.configuracao = self.data.get('configuracao')
            self.empresa.codigo_municipio = self.data.get('codigo_municipio')
            self.empresa.nome_fantasia = self.data.get('nome_fantasia')
            self.empresa.cep = self.data.get('cep')
            self.empresa.endereco = self.data.get('endereco')
            self.empresa.numero_endereco = self.data.get('numero_endereco')
            self.empresa.complemento = self.data.get('complemento')
            self.empresa.bairro = self.data.get('bairro')
            self.empresa.telefone = self.data.get('telefone')
            self.empresa.metodo_rateio = self.data.get('metodo_rateio')

            self.empresa.save()

            return {'sucess': True}

        except Exception as e:
            print(f'Erro ao editar {e}')
            return {'sucess': False}
