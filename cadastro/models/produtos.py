from enum import unique
from django.db import models
from django.db.models import constraints
from validacao.models.mercadorias_nfe.produtos import Produtos_notas
from cadastro.models.empresa import Empresa

class Cadastro_itens_sped(models.Model):
    
    produto_titular = models.ForeignKey(Produtos_notas, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Produto titular')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, blank=True, null=True)

    data_inicio_sped = models.DateField('Data de Início do SPED', null=True, blank=True)
    data_fim_sped = models.DateField('Data de Fim do SPED', null=True, blank=True)
    codigo_prod = models.CharField('Código do Produto', max_length=50, blank=True, null=True)
    descricao_prod = models.CharField('Descrição do Produto', max_length=150, blank=True, null=True)
    unidade = models.CharField('Unidade', max_length=10, blank=True, null=True)
    tipo_item = models.CharField('Tipo de Item', max_length=30, blank=True, null=True)
    ncm = models.CharField('NCM', max_length=50, blank=True, null=True)
    cest = models.CharField('CEST', max_length=50, blank=True, null=True)
    saldo_inicial_produto = models.DecimalField('Saldo Inicial do Produto', max_digits=10, decimal_places=2, null=True, blank=True)
    saldo_final_produto = models.DecimalField('Saldo Inicial do Produto', max_digits=10, decimal_places=2, null=True, blank=True)
    genero = models.CharField('Gênero', max_length=50, null=True, blank=True)
    mes_ref = models.CharField('Mês ref', max_length=20, null=True, blank=True)
    ano_sped = models.CharField('Ano sped', max_length=4, null=True, blank=True)

    class Meta:
        verbose_name = 'Cadastro de Item SPED'
        verbose_name_plural = 'Cadastros de Itens SPED'
        constraints = [
            models.UniqueConstraint(
                fields=['codigo_prod', 'empresa'],
                name='unique_codigo_mes_empresa',
            ),
        ]