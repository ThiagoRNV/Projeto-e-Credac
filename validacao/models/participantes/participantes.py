from django.db import models  # type: ignore
from cadastro.models.empresa import Empresa

class Participantes(models.Model):
    
    # Participante
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa')
    data_inicio_sped = models.DateField('Data de Início do SPED', null=True, blank=True)
    data_fim_sped = models.DateField('Data de Fim do SPED', null=True, blank=True)
    cod_part = models.CharField('Código do Participante', max_length=50, null=True, blank=True)
    nome = models.CharField('Nome', max_length=255, null=True, blank=True)
    codigo_pais = models.CharField('Código do País', max_length=20, null=True, blank=True)
    cnpj_cpf = models.CharField('CNPJ/CPF', max_length=30, null=True, blank=True)
    ie = models.CharField('Inscrição Estadual', max_length=30, null=True, blank=True)
    codigo_municipio = models.CharField('Código do Município', max_length=20, null=True, blank=True)
    suframa = models.CharField('SUFRAMA', max_length=20, null=True, blank=True)
    endereco = models.TextField('Endereço', null=True, blank=True)
    numero = models.CharField('Número', max_length=30, null=True, blank=True)
    complemento = models.TextField('Complemento', null=True, blank=True)
    bairro = models.CharField('Bairro', max_length=100, null=True, blank=True)
    phone = models.CharField('Telefone', max_length=30, null=True, blank=True)

    class Meta:
        verbose_name = 'Participante'
        verbose_name_plural = 'Participantes'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cod_part", "empresa", "data_inicio_sped"],
                name="unique_participante_por_empresa_periodo"
            )
        ]
