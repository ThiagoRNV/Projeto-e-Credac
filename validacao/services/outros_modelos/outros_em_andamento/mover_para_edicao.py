from mimetypes import init
from validacao.models.painel_controle.validacao import ValidacaoStatus, ValidacaoDataConcluida
from cadastro.models.empresa import Empresa
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ErrorMove(Exception):
    def __init__(self, message='Erro ao mover edição. Favor entrar em contato com Suporte.') -> None:
        super().__init__(message)

class ErrorParam(Exception):
    pass

class DataError(Exception):
    pass

class CompainerIdError(ValueError, TypeError):
    pass

class MoverParaEdicaoServices:
    def __init__(self, empresa_id, data_sped) -> None:
            self.empresa_id = empresa_id
            self.data_sped = data_sped
            
    def mover_edicao_services(self):
        
        if not self.data_sped:
            logger.error('Parâmetros inválidos para mover para edição.')
            raise ErrorParam()

        try:
            self.empresa_id = int(self.empresa_id)
            empresa_obj = Empresa.objects.get(id=self.empresa_id)

        except (TypeError, ValueError) as e:
            logger.error('Empresa ID inválido.', str(e))
            raise CompainerIdError()

        try:
            data_sped_obj = datetime.strptime(self.data_sped, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            logger.error('Data SPED inválida. Deve ser no formato YYYY-MM-DD.')
            raise DataError()

        try:
            ValidacaoStatus.objects.create(
                empresa=empresa_obj,
                status='em_andamento',
                progresso=0,
                # data_atualizacao=timezone.now(),
                data_sped=self.data_sped,
                sped=True,
                tipo_validacao='outros_modelos'
            )

            ValidacaoDataConcluida.objects.filter(
                empresa_id=self.empresa_id,
                data_sped=data_sped_obj,
                tipo_validacao='outros_modelos'
            ).delete()

            return {'success': True}
        except Exception as e:
            logger.error('Erro ao mover edição')
            raise ErrorMove() from e