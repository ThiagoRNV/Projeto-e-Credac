from tabnanny import verbose
from django.db import models
from cadastro.models.empresa import Empresa
from validacao.models.mercadorias_nfe.notas import Notas_participantes

class Produtos_notas(models.Model):

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Empresa', )
    nota_titular = models.ForeignKey(Notas_participantes, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Nota Titular', )
    # Identificação da nota
    tipo_nota = models.CharField('Tipo da Nota', max_length=50, blank=True, null=True)
    data_inicio_sped = models.DateField('Data de Início do SPED', null=True, blank=True)
    data_fim_sped = models.DateField('Data de Fim do SPED', null=True, blank=True)

    # Dados do produto
    codigo_prod = models.CharField('Código do Produto', max_length=50, blank=True, null=True)
    descricao_prod = models.TextField('Descrição do Produto', blank=True, null=True)
    unidade = models.CharField('Unidade', max_length=50, blank=True, null=True)
    quantidade_prod = models.DecimalField('Quantidade do Produto', max_digits=15, decimal_places=4, null=True, blank=True)
    valor_unitario = models.DecimalField('Valor Unitário', max_digits=15, decimal_places=6, null=True, blank=True)
    valor_total = models.DecimalField('Valor Total', max_digits=18, decimal_places=2, null=True, blank=True)
    cfop_prod = models.CharField('CFOP do Produto', max_length=10, blank=True, null=True)
    ncm = models.CharField('NCM', max_length=50, blank=True, null=True)
    cest = models.CharField('CEST', max_length=50, blank=True, null=True)
    cst = models.CharField('CST', max_length=15, blank=True, null=True)
    aliquota_icms = models.DecimalField('Alíquota do ICMS', max_digits=18, decimal_places=2, null=True, blank=True)
    base_icms = models.DecimalField('Base do ICMS', max_digits=18, decimal_places=2, null=True, blank=True)
    valor_ipi = models.DecimalField('Valor do IPI', max_digits=18, decimal_places=2, null=True, blank=True)
    valor_pis = models.DecimalField('Valor do PIS', max_digits=18, decimal_places=2, null=True, blank=True)
    valor_icms = models.DecimalField('Valor do ICMS', max_digits=18, decimal_places=2, null=True, blank=True)
    tipo_movimento = models.CharField('Tipo de Movimento', max_length=50, null=True, blank=True)
    cod_lancamento = models.CharField('Código de Lançamento', max_length=10, null=True, blank=True)

    # Complementares
    tipo_item = models.CharField('Tipo de Item', max_length=50, blank=True, null=True)
    status = models.CharField('Status', max_length=50, blank=True, null=True)  # ex: processado, autorizado, cancelado

    class Meta:
        verbose_name = 'Produto da Nota'
        verbose_name_plural = 'Produtos das Notas'

    def __str__(self):
        num = self.nota_titular.numero_nota if self.nota_titular_id else ''
        desc = (self.descricao_prod or '')[:50]
        return f"{num} - {self.codigo_prod} - {desc}"

