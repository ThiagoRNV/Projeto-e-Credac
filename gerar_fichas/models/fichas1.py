from django.db import models


class Ficha1a(models.Model):
    """Controle de materiais — colunas conforme template ficha1A."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Histórico', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo de documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do documento', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do lançamento', max_length=500, blank=True)
    ficha_origem_ou_destino = models.CharField('Ficha de Origem ou Destino', max_length=500, blank=True)
    codigo_item_movimentado = models.CharField('Código do item movimentado', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do custo', max_length=500, blank=True)
    entrada_valor_icms = models.CharField('Entradas — Valor do Icms', max_length=500, blank=True)
    saida_quantidade = models.CharField('Saídas — Quantidade', max_length=500, blank=True)
    saida_valor_unitario_custo = models.CharField('Saídas — Valor unitário do custo', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do custo', max_length=500, blank=True)
    saida_valor_unitario_icms = models.CharField('Saídas — Valor unitário do icms', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do Icms', max_length=500, blank=True)
    saldo_valor_custo = models.CharField('Saldo — Valor do custo', max_length=500, blank=True)
    saldo_valor_icms = models.CharField('Saldo — Valor do Icms', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha1a'
        verbose_name = 'Ficha 1A'
        verbose_name_plural = 'Fichas 1A'


class Ficha1b(models.Model):
    """Industrialização por outro estabelecimento — ficha1B."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Historico', max_length=500, blank=True)
    cfop = models.CharField('CFOP', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo de documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do documento', max_length=500, blank=True)
    numero_di_dsi = models.CharField('Número do DI ou DSI', max_length=500, blank=True)
    cod_remetente_destinatario = models.CharField('Código remetente e destinatário', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do lançamento', max_length=500, blank=True)
    ficha_origem_ou_destino = models.CharField('Ficha de origem ou destino', max_length=500, blank=True)
    cod_origem_ou_destino = models.CharField('Código de Origem ou Destino', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do custo', max_length=500, blank=True)
    entrada_icms = models.CharField('Entradas — Icms', max_length=500, blank=True)
    entrada_ipi = models.CharField('Entradas — Ipi', max_length=500, blank=True)
    entrada_outros = models.CharField('Entradas — Outros impostos e contribuições', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do custo', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do icms', max_length=500, blank=True)
    saldo_valor_custo = models.CharField('Saldo — Valor do custo', max_length=500, blank=True)
    saldo_valor_icms = models.CharField('Saldo — Valor do icms', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha1b'
        verbose_name = 'Ficha 1B'
        verbose_name_plural = 'Fichas 1B'


class Ficha1c(models.Model):
    """Energia elétrica — ficha1C."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Historico', max_length=500, blank=True)
    cfop = models.CharField('CFOP', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo de documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do documento', max_length=500, blank=True)
    cod_remetente = models.CharField('Código Remetente', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do lançamento', max_length=500, blank=True)
    ficha_origem_ou_destino = models.CharField('Ficha de origem ou destino', max_length=500, blank=True)
    cod_origem_ou_destino = models.CharField('Código de Origem ou Destino', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do custo', max_length=500, blank=True)
    entrada_icms = models.CharField('Entradas — Icms', max_length=500, blank=True)
    entrada_outros = models.CharField('Entradas — Outros impostos e contribuições', max_length=500, blank=True)
    saida_quantidade = models.CharField('Saídas — Quantidade', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do custo', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do icms', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha1c'
        verbose_name = 'Ficha 1C'
        verbose_name_plural = 'Fichas 1C'


class Ficha1d(models.Model):
    """Serviços e comunicações — ficha1D."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Historico', max_length=500, blank=True)
    cfop = models.CharField('CFOP', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo de documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do documento', max_length=500, blank=True)
    cod_remetente = models.CharField('Código Remetente', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do lançamento', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do custo', max_length=500, blank=True)
    entrada_outros = models.CharField('Entradas — Outros impostos e contribuições', max_length=500, blank=True)
    entrada_valor_icms = models.CharField('Entradas — Valor do icms', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha1d'
        verbose_name = 'Ficha 1D'
        verbose_name_plural = 'Fichas 1D'


class Ficha1e(models.Model):
    """Transportes mesma natureza — ficha1E."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Historico', max_length=500, blank=True)
    cfop = models.CharField('CFOP', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo de documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do documento', max_length=500, blank=True)
    cod_remetente = models.CharField('Código remetente', max_length=500, blank=True)
    cod_destinatario = models.CharField('Código do destinatário', max_length=500, blank=True)
    uf_inicio_transporte = models.CharField('UF de início da inicio do transporte', max_length=500, blank=True)
    uf_destino_mercadoria = models.CharField('UF de destino da mercadoria', max_length=500, blank=True)
    cod_tomador_servico = models.CharField('Código do tomador do serviço', max_length=500, blank=True)
    aliquota = models.CharField('Aliquota', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do lançamento', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do custo', max_length=500, blank=True)
    entrada_icms = models.CharField('Entradas — Icms', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do custo', max_length=500, blank=True)
    saida_icms = models.CharField('Saídas — Icms', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha1e'
        verbose_name = 'Ficha 1E'
        verbose_name_plural = 'Fichas 1E'
