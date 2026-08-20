from cadastro.models.produtos import Cadastro_itens_sped
from datetime import datetime
from cadastro.models.empresa import Empresa

class CadastroManualServices:
    
    def __init__(self, data_job):
        self.data_job = data_job
        
    def cadatro_manual(self):

        empresa_id = self.data_job.get('empresa_id')

        empresa = Empresa.objects.get(id=empresa_id)


        try:
            Cadastro_itens_sped.objects.create(
                empresa=empresa,
                data_inicio_sped=self.data_job.get('data_inicio_sped'),
                codigo_prod=self.data_job.get('codigo_prod'),
                descricao_prod=self.data_job.get('descricao_prod'),
                unidade=self.data_job.get('unidade'),
                tipo_item=self.data_job.get('tipo_item'),
                genero=self.data_job.get('genero'),
                ncm=self.data_job.get('ncm'),
                cest=self.data_job.get('cest'),
                saldo_inicial_produto=self.data_job.get('saldo_inicial_produto'),
                saldo_final_produto=self.data_job.get('saldo_final_produto'),
            )    

            return {'sucess': True}

        except Exception as e:
            return {'sucess': False , 'error': {e}}