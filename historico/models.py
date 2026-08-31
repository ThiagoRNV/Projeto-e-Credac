from django.contrib.auth.models import User
from cadastro.models.empresa import Empresa
from django.db import models


class Historico(models.Model):
    TELA_CHOICES = [
        ('movimentacao', 'Movimentação'),
        ('metodo_rateio', 'Método Rateio'),
        ('cadastro', 'Cadastro'),
        ('gerar_arquivo', 'Arquivo baixados'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario responsável',
    )

    tela_modificada = models.CharField(
        'Tela modificada',
        max_length=30,
        choices=TELA_CHOICES,
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Empresa ID')
    nome_empresa = models.CharField('Nome empresa', max_length=50, null=True, blank=True)
    part_titular = models.CharField('Participante Titular', max_length=50, null=True, blank=True)
    entidade_pai = models.CharField('Entidade pai', max_length=50, null=True, blank=True)
    entidade_filho = models.CharField('Entidade Filho', max_length=30, null=True, blank=True)
    tabela = models.CharField('Tabela', max_length=30, null=True, blank=True)
    campo = models.CharField('Campo', max_length=100)
    valor_antigo = models.TextField('Valor antigo', null=True, blank=True)
    valor_novo = models.TextField('Valor novo', null=True, blank=True)
    mes_sped = models.CharField('Mês do sped', max_length=9, null=True, blank=True)
    ano_sped = models.CharField('Ano do sped', max_length=4, null=True, blank=True)
    data_alteracao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Histórico'
        verbose_name_plural = 'Históricos'
        ordering = ['-data_alteracao']

    def __str__(self):
        return f'{self.tela_modificada} - {self.campo}'
