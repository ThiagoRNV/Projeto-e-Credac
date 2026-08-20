from django.db import models


class Ficha4a(models.Model):
    """Rateio energia elétrica — ficha4A."""

    codigo_item = models.CharField('Código do item', max_length=500, blank=True)
    percentual_rateio = models.CharField('Percentual de Rateio', max_length=500, blank=True)
    custo_energia_eletrica = models.CharField('Custo da energia elétrica', max_length=500, blank=True)
    icms_energia_eletrica = models.CharField('ICMS da energia elétrica', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha4a'
        verbose_name = 'Ficha 4A'
        verbose_name_plural = 'Fichas 4A'


class Ficha4b(models.Model):
    """Rateio insumo conjunto — ficha4B."""

    codigo_produto_subproduto = models.CharField('Código do produto ou sub-produto', max_length=500, blank=True)
    qtd_coproduto_subproduto = models.CharField(
        'Quantidade de co-produto ou sub-produto resultante do insumo conjunto', max_length=500, blank=True
    )
    preco_medio_unit_saida = models.CharField(
        'Preço médio unitário de saída do co-produto ou sub-produto', max_length=500, blank=True
    )
    valor_projetado_saidas = models.CharField('Valor projetado das saídas', max_length=500, blank=True)
    percentual_atrib_insumo = models.CharField('Percentual de atribuição do insumo conjunto', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha4b'
        verbose_name = 'Ficha 4B'
        verbose_name_plural = 'Fichas 4B'


class Ficha4c(models.Model):
    """Rateio gastos gerais fabricação — ficha4C."""

    codigo_item = models.CharField('Código do item', max_length=500, blank=True)
    percentual_rateio = models.CharField('Percentual de rateio', max_length=500, blank=True)
    custo_ggf = models.CharField('Custo do gastos gerais de fabricação', max_length=500, blank=True)
    icms_ggf = models.CharField('ICMS do gastos gerais de fabricação', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha4c'
        verbose_name = 'Ficha 4C'
        verbose_name_plural = 'Fichas 4C'
