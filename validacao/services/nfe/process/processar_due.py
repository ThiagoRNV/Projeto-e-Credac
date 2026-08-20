from csv import Error
import logging
from validacao.parser.nfe.extract_planilhaDue import ExtractPlanilhaDue
from validacao.models.mercadorias_nfe.notas import Notas_participantes
from validacao.models.painel_controle.validacao import ValidacaoStatus

logger = logging.getLogger(__name__)

class DueException(Exception):
    pass

class DueTypeError(DueException):
    def __init__(self, message='O arquivo deve ser .xlsx') -> None:
        super().__init_(message)

class ErrorDate(DueException):
    def __init__(self, message='Nenhum dado encontrado na planilha DUE. Favor verificar planilha') -> None:
        super().__init__(message)

class ProcessDueService:
    def __init__(self, due_file) -> None:
        self.planilha_due = due_file

    def due(self):
        try:
            if not self.planilha_due:
                logger.error('Planilha DUE não informada')
                raise 
            
            if not self.planilha_due.name.endswith('.xlsx'):
                raise DueTypeError()

            dados_planilha = ExtractPlanilhaDue(self.planilha_due)
            if not dados_planilha.load_planilha_due():
                logger.error('Erro ao carregar planilha DUE')
                raise DueException()

            values_planilha = dados_planilha.extract_values_planilha()
            if not values_planilha or not values_planilha.get('planilha_due'):
                logger.error('Erro ao extrair valores da planilha DUE')
                raise DueException()

            lista_due = values_planilha.get('planilha_due', [])
            
            

            if not lista_due:
                raise ErrorDate()

            notas_atualizadas = 0
            notas_nao_encontradas = 0

            for item in lista_due:
                try:
                    nota = item.get('nota')
                    numero_due = item.get('numero_due')
                    mes = item.get('mes')
                    
                    if not nota or not numero_due:
                        continue

                    notas_query = Notas_participantes.objects.filter(
                        numero_nota=nota, 
                        mes_sped=mes,
                    )
                
                    ValidacaoStatus.objects.filter(
                        mes_sped=mes,
                    ).update(due=True)

                    
                    notas_encontradas = notas_query.first()

                    if notas_encontradas:
                        notas_encontradas.tipo_operacao = 'Exportação'
                        notas_encontradas.numero_documento = numero_due
                        notas_encontradas.save()
                        notas_atualizadas += 1
                    else:
                        notas_nao_encontradas += 1
                except Exception as e:
                    logger.error(f'Erro ao processar item da planilha DUE: {str(e)}')
                    raise DueException() from e

            if notas_atualizadas > 0:
                logger.success(f'{notas_atualizadas} nota(s) encontrada(s) e atualizada(s) com sucesso!')
            if notas_nao_encontradas > 0:
                logger.warning(f'{notas_nao_encontradas} nota(s) não encontrada(s) no sistema.')
            if notas_atualizadas == 0 and notas_nao_encontradas == 0:
                logger.warning('Arquivo já usado para processamento.')

            
            return {'success': True}
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f'Erro ao processar planilha DUE: {str(e)}\n{error_trace}')
            logger.error(f'Erro ao processar planilha DUE: {str(e)}')
            raise