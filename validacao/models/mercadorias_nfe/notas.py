from django.db import models  # type: ignore
from cadastro.models.empresa import Empresa
from validacao.models.participantes.participantes import Participantes

class Notas_participantes(models.Model):
    # Nota fiscal
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Empresa',
    )
    tipo = models.CharField('Tipo', max_length=50, blank=True, null=True)
    data_inicio_sped = models.DateField('Data de Início do SPED', null=True, blank=True)
    data_fim_sped = models.DateField('Data de Fim do SPED', null=True, blank=True)
    part_titular = models.ForeignKey(
        Participantes,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Participante Titular',
    )
    numero_nota = models.CharField('Número da Nota', max_length=50, blank=True, null=True)
    codigo_uf = models.CharField('Código da UF', max_length=50, blank=True, null=True)
    chave_nota = models.CharField('Chave da Nota', max_length=50, blank=True, null=True)
    status = models.CharField('Status', max_length=15, blank=True, null=True)
    tipo_operacao = models.CharField('Tipo de Operação', max_length=50, blank=True, null=True)
    numero_documento = models.CharField('Número do Documento', max_length=50, blank=True, null=True)
    mes_sped = models.CharField('Mês do SPED', max_length=20, blank=True, null=True)
    data_entrada_saida = models.DateField('Data de Entrada e Saída', null=True, blank=True)
    tipo_documento = models.CharField('Tipo de Documento', max_length=4, null=True, blank=True)
    serie_documento = models.CharField('Série do Documento', max_length=4, null=True, blank=True)

    class Meta:
        verbose_name = 'Nota do Participante'
        verbose_name_plural = 'Notas dos Participantes'
