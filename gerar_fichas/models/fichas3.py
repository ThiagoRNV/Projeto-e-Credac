from django.db import models


class Ficha3a(models.Model):
    """Produtos acabados — ficha3A."""

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
    cod_origem_ou_destino = models.CharField('Código de origem ou destino', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do custo', max_length=500, blank=True)
    entrada_valor_icms = models.CharField('Entradas — Valor do ICMS', max_length=500, blank=True)
    saida_quantidade = models.CharField('Saídas — Quantidade', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do Custo', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do ICMS', max_length=500, blank=True)
    saldo_quantidade = models.CharField('Saldos — Quantidade', max_length=500, blank=True)
    saldo_valor_unitario_custo = models.CharField('Saldos — Valor do unitário do custo', max_length=500, blank=True)
    saldo_valor_custo = models.CharField('Saldos — Valor do Custo', max_length=500, blank=True)
    saldo_valor_unitario_icms = models.CharField('Saldos — Valor unitário do icms', max_length=500, blank=True)
    saldo_valor_icms = models.CharField('Saldos — Valor do icms', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha3a'
        verbose_name = 'Ficha 3A'
        verbose_name_plural = 'Fichas 3A'


class Ficha3b(models.Model):
    """Mercadorias de revenda — ficha3B."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Histórico', max_length=500, blank=True)
    cfop = models.CharField('CFOP', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo do Documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do Documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do Documento', max_length=500, blank=True)
    numero_di_dsi = models.CharField('Número da DI ou DSI', max_length=500, blank=True)
    cod_remetente_destinatario = models.CharField('Código remetente e destinatário', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do lançamento', max_length=500, blank=True)
    ficha_origem_ou_destino = models.CharField('Ficha de origem ou destino', max_length=500, blank=True)
    cod_origem_ou_destino = models.CharField('Código de origem ou destino', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do custo', max_length=500, blank=True)
    entrada_valor_icms = models.CharField('Entradas — Valor do ICMS', max_length=500, blank=True)
    entrada_ipi = models.CharField('Entradas — IPI', max_length=500, blank=True)
    entrada_outros = models.CharField('Entradas — Outros impostos e contribuições', max_length=500, blank=True)
    saida_quantidade = models.CharField('Saídas — Quantidade', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do custo', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do ICMS', max_length=500, blank=True)
    saldo_quantidade = models.CharField('Saldos — Quantidade', max_length=500, blank=True)
    saldo_valor_unitario_custo = models.CharField('Saldos — Valor do unitário do custo', max_length=500, blank=True)
    saldo_valor_custo = models.CharField('Saldos — Valor do custo', max_length=500, blank=True)
    saldo_valor_unitario_icms = models.CharField('Saldos — Valor unitário do icms', max_length=500, blank=True)
    saldo_valor_icms = models.CharField('Saldos — Valor do icms', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha3b'
        verbose_name = 'Ficha 3B'
        verbose_name_plural = 'Fichas 3B'


class Ficha3c(models.Model):
    """Custo agregado industrialização outro estabelecimento — ficha3C."""

    numero_ordem = models.CharField('Número da Ordem', max_length=500, blank=True)
    numero_lancamento = models.CharField('Número do lançamento', max_length=500, blank=True)
    data = models.DateField('Data', null=True, blank=True)
    historico = models.CharField('Histórico', max_length=500, blank=True)
    cfop = models.CharField('CFOP', max_length=500, blank=True)
    tipo_documento = models.CharField('Tipo do Documento', max_length=500, blank=True)
    serie_documento = models.CharField('Série do Documento', max_length=500, blank=True)
    numero_documento = models.CharField('Número do Documento', max_length=500, blank=True)
    cod_remetente_destinatario = models.CharField('Código do remetente e destinatário', max_length=500, blank=True)
    codigo_lancamento = models.CharField('Código do lançamento', max_length=500, blank=True)
    entrada_quantidade = models.CharField('Entradas — Quantidade', max_length=500, blank=True)
    entrada_valor_custo = models.CharField('Entradas — Valor do custo', max_length=500, blank=True)
    entrada_valor_icms = models.CharField('Entradas — Valor do ICMS', max_length=500, blank=True)
    saida_quantidade = models.CharField('Saídas — Quantidade', max_length=500, blank=True)
    saida_valor_custo = models.CharField('Saídas — Valor do custo', max_length=500, blank=True)
    saida_valor_icms = models.CharField('Saídas — Valor do ICMS', max_length=500, blank=True)
    saldo_quantidade = models.CharField('Saldos — Quantidade', max_length=500, blank=True)
    saldo_valor_custo = models.CharField('Saldos — Valor do custo', max_length=500, blank=True)
    saldo_valor_icms = models.CharField('Saldos — Valor do ICMS', max_length=500, blank=True)

    class Meta:
        db_table = 'Ficha3c'
        verbose_name = 'Ficha 3C'
        verbose_name_plural = 'Fichas 3C'
