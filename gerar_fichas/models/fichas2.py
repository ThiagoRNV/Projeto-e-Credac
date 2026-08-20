from django.db import models


class Ficha2a(models.Model):
    """PEE industrialização no estabelecimento — ficha2A."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Histórico', max_length=500, blank=True)
    cfop = models.CharField('CFOP', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo do Documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do Documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do Documento', max_length=500, blank=True)
    numero_di_dsi = models.CharField('Número da DI ou DSI', max_length=500, blank=True)
    cod_remetente_destinatario = models.CharField('Código do Remetente ou Destinatário', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do Lançamento', max_length=500, blank=True)
    ficha_origem_ou_destino = models.CharField('Ficha de Origem ou Destino', max_length=500, blank=True)
    cod_origem_e_destino = models.CharField('Código de Origem e Destino', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do Custo', max_length=500, blank=True)
    entrada_icms = models.CharField('Entradas — ICMS', max_length=500, blank=True)
    entrada_ipi = models.CharField('Entradas — IPI', max_length=500, blank=True)
    entrada_outros = models.CharField('Entradas — Outros Impostos e Contribuições', max_length=500, blank=True)
    saida_quantidade = models.CharField('Saídas — Quantidade', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do Custo', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do ICMS', max_length=500, blank=True)
    saldo_qtd_mercadoria = models.CharField('Saldo — Quantidade de Mercadoria', max_length=500, blank=True)
    saldo_valor_unit_custo = models.CharField('Saldo — Valor Unitário do Custo', max_length=500, blank=True)
    saldo_valor_custo = models.CharField('Saldo — Valor do Custo', max_length=500, blank=True)
    saldo_valor_unit_icms = models.CharField('Saldo — Valor Unitário do ICMS', max_length=500, blank=True)
    saldo_valor_icms = models.CharField('Saldo — Valor do ICMS', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha2a'
        verbose_name = 'Ficha 2A'
        verbose_name_plural = 'Fichas 2A'


class Ficha2b(models.Model):
    """PEE industrialização em outro estabelecimento — ficha2B."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Histórico', max_length=500, blank=True)
    cfop = models.CharField('CFOP', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo do Documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do Documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do Documento', max_length=500, blank=True)
    cod_remetente_destinatario = models.CharField('Código do Remetente ou Destinatário', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do Lançamento', max_length=500, blank=True)
    ficha_origem_ou_destino = models.CharField('Ficha de Origem ou Destino', max_length=500, blank=True)
    cod_item_movimentado = models.CharField('Código do Item Movimentado', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do Custo', max_length=500, blank=True)
    entrada_icms = models.CharField('Entradas — ICMS', max_length=500, blank=True)
    saida_quantidade = models.CharField('Saídas — Quantidade', max_length=500, blank=True)
    saida_valor_unit_custo = models.CharField('Saídas — Valor Unitário do Custo', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do Custo', max_length=500, blank=True)
    saida_valor_unit_icms = models.CharField('Saídas — Valor Unitário do ICMS', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do ICMS', max_length=500, blank=True)
    saldo_valor_custo = models.CharField('Saldo — Valor do Custo', max_length=500, blank=True)
    saldo_valor_icms = models.CharField('Saldo — Valor do ICMS', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha2b'
        verbose_name = 'Ficha 2B'
        verbose_name_plural = 'Fichas 2B'


class Ficha2c(models.Model):
    """PEE para outro estabelecimento — ficha2C."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Histórico', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo do Documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do Documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do Documento', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do Lançamento', max_length=500, blank=True)
    ficha_origem_ou_destino = models.CharField('Ficha de Origem ou Destino', max_length=500, blank=True)
    cod_item_movimentado = models.CharField('Código do Item Movimentado', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do Custo', max_length=500, blank=True)
    entrada_valor_icms = models.CharField('Entradas — Valor do ICMS', max_length=500, blank=True)
    saida_quantidade = models.CharField('Saídas — Quantidade', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do Custo', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do ICMS', max_length=500, blank=True)
    saldo_valor_custo = models.CharField('Saldo — Valor do Custo', max_length=500, blank=True)
    saldo_valor_icms = models.CharField('Saldo — Valor do ICMS', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha2c'
        verbose_name = 'Ficha 2C'
        verbose_name_plural = 'Fichas 2C'


class Ficha2d(models.Model):
    """Custo serviços de transporte — ficha2D."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Histórico', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo do Documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do Documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do Documento', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do Lançamento', max_length=500, blank=True)
    ficha_origem = models.CharField('Ficha de Origem', max_length=500, blank=True)
    cod_origem = models.CharField('Código de Origem', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do Custo', max_length=500, blank=True)
    entrada_valor_icms = models.CharField('Entradas — Valor do ICMS', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha2d'
        verbose_name = 'Ficha 2D'
        verbose_name_plural = 'Fichas 2D'


class Ficha2e(models.Model):
    """Gastos gerais de fabricação — ficha2E."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Histórico', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo do Documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do Documento', max_length=500, blank=True)
    documento_interno = models.CharField('Documento Interno', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do Lançamento', max_length=500, blank=True)
    ficha_origem_ou_destino = models.CharField('Ficha de Origem ou Destino', max_length=500, blank=True)
    cod_item_movimentado = models.CharField('Código do item movimentado', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_unidade = models.CharField('Entradas — Unidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do Custo', max_length=500, blank=True)
    entrada_valor_icms = models.CharField('Entradas — Valor do ICMS', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do Custo', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do ICMS', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha2e'
        verbose_name = 'Ficha 2E'
        verbose_name_plural = 'Fichas 2E'


class Ficha2f(models.Model):
    """Insumo conjunto preço de saída — ficha2F."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Histórico', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo do Documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do Documento', max_length=500, blank=True)
    documento_interno = models.CharField('Documento Interno', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do Lançamento', max_length=500, blank=True)
    ficha_origem_ou_destino = models.CharField('Ficha de Origem ou Destino', max_length=500, blank=True)
    cod_item_movimentado = models.CharField('Código do item movimentado', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do Custo', max_length=500, blank=True)
    entrada_valor_icms = models.CharField('Entradas — Valor do ICMS', max_length=500, blank=True)
    percentual_atrib_insumo_conjunto = models.CharField(
        'Percentual de atribuição do insumos conjunto', max_length=500, blank=True
    )
    saida_quantidade = models.CharField('Saídas — Quantidade', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do Custo', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do ICMS', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha2f'
        verbose_name = 'Ficha 2F'
        verbose_name_plural = 'Fichas 2F'


class Ficha2g(models.Model):
    """Produção conjunta ficha técnica — ficha2G."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Histórico', max_length=500, blank=True)
    cfop = models.CharField('CFOP', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo do Documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do Documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do Documento', max_length=500, blank=True)
    cod_remetente_destinatario = models.CharField('Código do Remetente ou Destinatário', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do Lançamento', max_length=500, blank=True)
    ficha_origem_ou_destino = models.CharField('Ficha de Origem ou Destino', max_length=500, blank=True)
    cod_item_movimentado = models.CharField('Código do item movimentado', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do custo', max_length=500, blank=True)
    entrada_valor_icms = models.CharField('Entradas — Valor do ICMS', max_length=500, blank=True)
    saida_qtd_coproduto = models.CharField('Saídas — Quantidade de co-produto ou subproduto', max_length=500, blank=True)
    saida_valor_unit_custo = models.CharField('Saídas — Valor Unitário do Custo', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do Custo', max_length=500, blank=True)
    saida_valor_unit_icms = models.CharField('Saídas — Valor Unitário do ICMS', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do ICMS', max_length=500, blank=True)
    saldo_valor_custo = models.CharField('Saldos — Valor do Custo', max_length=500, blank=True)
    saldo_valor_icms = models.CharField('Saldos — Valor do ICMS', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha2g'
        verbose_name = 'Ficha 2G'
        verbose_name_plural = 'Fichas 2G'
