import logging
from datetime import datetime

from validacao.models.painel_controle.validacao import ValidacaoStatus, ValidacaoDataConcluida
from validacao.models.outros_modelos.registrod100 import RegistroTransporteD100
from validacao.models.outros_modelos.registrod190 import RegistroTransporteD190
from validacao.models.outros_modelos.registroc500 import RegistroEnergiaC500
from validacao.models.outros_modelos.registrod500 import RegistroComunicacaoD500
from validacao.models.participantes.participantes import Participantes
logger = logging.getLogger(__name__)

class ErrorParamFinish(Exception):
    pass

class ErrorFinish(Exception):
    def __init__(self, message='Erro ao finalizar. Favor entrar em contato com o suporte.') -> None:
        super().__init__(message)

class DataErrorFinish(ValueError, TypeError):
    pass

class FinalizarServices:
    def __init__(self, empresa_id, data_sped) -> None:
        self.empresa_id = empresa_id
        self.data_sped = data_sped
        
    def finalizar_servico(self):


        if not self.empresa_id or not self.data_sped:
            logger.warning('Parâmetros inválidos para finalizar.')
            raise ErrorParamFinish()

        try:
            data_sped_obj = datetime.strptime(self.data_sped, '%Y-%m-%d').date()
        except (ValueError, TypeError) as e:
            logger.error(f'Data SPED inválida: {self.data_sped}. Deve ser no formato DD-MM-YYYY.')
            raise DataErrorFinish()

        lista_mes ={
            '01': 'Janeiro',
            '02': 'Fevereiro',
            '03': 'Março',
            '04': 'Abril',
            '05': 'Maio',
            '06': 'Junho',
            '07': 'Julho',
            '08': 'Agosto',
            '09': 'Setembro',
            '10': 'Outubro',
            '11': 'Novembro',
            '12': 'Dezembro',
        }

        data_sped_str = data_sped_obj.strftime('%d%m%Y')
        
        mes_sped = lista_mes.get(data_sped_str[2:4])

        try:
            ValidacaoDataConcluida.objects.get_or_create(
                empresa_id=self.empresa_id,
                data_sped=data_sped_obj,
                tipo_validacao='outros_modelos',
                defaults={'mes_sped': mes_sped},
            )

            todas_datas = set(RegistroTransporteD100.objects.filter(empresa_id=self.empresa_id).exclude(data_inicio_sped__isnull=True).values_list('data_inicio_sped', flat=True).distinct())
            todas_datas.update(RegistroTransporteD190.objects.filter(empresa_id=self.empresa_id).exclude(data_inicio_sped__isnull=True).values_list('data_inicio_sped', flat=True).distinct())
            todas_datas.update(RegistroEnergiaC500.objects.filter(empresa_id=self.empresa_id).exclude(data_inicio_sped__isnull=True).values_list('data_inicio_sped', flat=True).distinct())
            todas_datas.update(RegistroComunicacaoD500.objects.filter(empresa_id=self.empresa_id).exclude(data_inicio_sped__isnull=True).values_list('data_inicio_sped', flat=True).distinct())
            todas_datas.update(Participantes.objects.filter(empresa_id=self.empresa_id).exclude(data_inicio_sped__isnull=True).values_list('data_inicio_sped', flat=True).distinct())
            todas_datas = {d for d in todas_datas if d is not None}

            concluidas = set(
                ValidacaoDataConcluida.objects.filter(
                    empresa_id=self.empresa_id,
                    tipo_validacao='outros_modelos',
                ).values_list('data_sped', flat=True)
            )

            if todas_datas and todas_datas.issubset(concluidas):
                ValidacaoStatus.objects.filter(empresa_id=self.empresa_id, tipo_validacao='outros_modelos').delete()

            return {'success': True}
            
        except Exception as e:
            logger.error(f'Erro ao finalizar movimentação')
            raise ErrorFinish() from e