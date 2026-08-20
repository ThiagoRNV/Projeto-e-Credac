from django.db import models

class PlanilhaCusto(models.Model):
    empresa = models.CharField('Empresa', max_length=255)
    data_referencia = models.DateField('Data de Referência', blank=True, null=True)
    categoria = models.CharField('Categoria', max_length=255, blank=True, null=True)
    centro_custo = models.CharField('Centro de Custo', max_length=255, blank=True, null=True)
    descricao = models.TextField('Descrição', blank=True, null=True)
    documento_fiscal = models.CharField('Documento Fiscal', max_length=255, blank=True, null=True)
    fornecedor = models.CharField('Fornecedor', max_length=255, blank=True, null=True)
    conta_contabil = models.CharField('Conta Contábil', max_length=255, blank=True, null=True)
    valor_total = models.DecimalField('Valor Total', max_digits=10, decimal_places=2, blank=True, null=True)
    percentual_aplicado = models.DecimalField('Percentual Aplicado', max_digits=10, decimal_places=2, blank=True, null=True)
    valor_alocado = models.DecimalField('Valor Alocado', max_digits=10, decimal_places=2, blank=True, null=True)
    icms_passivel_credito = models.DecimalField('Icms Passivel de Crédito', max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'Planilha de Custo'
        verbose_name_plural = 'Planilhas de Custo'
