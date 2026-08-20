from django.db import models
from cadastro.models.empresa import Empresa

class ItensProduzidos230(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    registro = models.CharField('Registro', max_length=5, blank=True, null=True)
    data_inicial_op = models.DateField('Data Inicial da Operação', blank=True, null=True)
    data_final_op = models.DateField('Data Final da Operação', blank=True, null=True)
    cod_ordem_prod = models.CharField('Código da Ordem de Produção', max_length=50, blank=True, null=True)
    codigo_item = models.CharField('Código do Item', max_length=50, blank=True, null=True)
    mes_referencia_k230 = models.CharField('Mês Referência do K230', max_length=20, blank=True, null=True)
    qtd_producao_acabada = models.CharField('Quantidade Produção Acabada', max_length=50, blank=True, null=True)
    ano_sped = models.CharField('Ano do Sped', max_length=4, blank=True, null=True)

    class Meta:
        verbose_name = 'Item Produzido K230'
        verbose_name_plural = 'Itens Produzidos K230'

    def __str__(self):
        return f"{self.empresa.razao_social} - {self.data_inicial_op} - {self.data_final_op} - {self.cod_ordem_prod} - {self.codigo_item} - {self.status}"

class InsumosUsados235(models.Model):
    item_produzido = models.ForeignKey(ItensProduzidos230, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    registro = models.CharField('Registro', max_length=5, blank=True, null=True)
    data_saida_estoque = models.DateField('Data de Saída do Estoque', blank=True, null=True)
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=2, blank=True, null=True)
    codigo_insumo = models.CharField('Código do Insumo', max_length=50, blank=True, null=True)
    situacao = models.CharField('Situação', max_length=50, blank=True, null=True)
    verificacao_codigo = models.CharField('Verificação do Código', max_length=50, blank=True, null=True)
    ano_sped = models.CharField('Ano do SPED', max_length=4, blank=True, null=True)
    mes_referencia_k235 = models.CharField('Mês de Referência do K235', max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = 'Insumo Usado K235'
        verbose_name_plural = 'Insumos Usados K235'

    def __str__(self):
        return f"{self.empresa.razao_social} - {self.data_saida_estoque} - {self.codigo_item} - {self.quantidade} - {self.codigo_insumo} - {self.status}"


class ItensProduzidos250(models.Model):
    registro = models.CharField('Registro', max_length=5, blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    data_prod = models.DateField('Data de Produção', blank=True, null=True)
    cod_item = models.CharField('Código do Item', max_length=50, blank=True, null=True)
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=2, blank=True, null=True)
    ano_sped = models.CharField('Ano do SPED', max_length=4, blank=True, null=True)
    mes_sped = models.CharField('Mês do SPED', max_length=18, blank=True, null=True)

    class Meta:
        verbose_name = 'Item Produzido K250'
        verbose_name_plural = 'Itens Produzidos K250'

class InsumosUsados255(models.Model):
    registro = models.CharField('Registro', max_length=5, blank=True, null=True)
    ano_sped = models.CharField('Ano do SPED', blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    data_consumo_insumo = models.DateField('Data de Consumo do Insumo', blank=True, null=True)
    cod_item = models.CharField('Código do Item', max_length=50, blank=True, null=True)
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=2, blank=True, null=True)
    qtd_perda = models.CharField('Quantidade de perda', max_length=50, blank=True, null=True)
    mes_sped = models.CharField('Mês do SPED', max_length=20, blank=True, null=True)
    k250_titular = models.ForeignKey(ItensProduzidos250, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Insumo Usado K255'
        verbose_name_plural = 'Insumos Usados K255'


class analise_k23x(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    data_inicio = models.DateField('Data de Início', blank=True, null=True)
    data_fim = models.DateField('Data de Fim', blank=True, null=True)
    ano_sped = models.JSONField(default=list, blank=True)
    
    class Meta:
        verbose_name = 'Análise em Andamento K23x'
        verbose_name_plural = 'Análises em Andamento K23x'
    
    def __str__(self):
        return f"{self.empresa.razao_social} - {self.data_inicio} - {self.data_fim} - {self.status}"

class analise_k25x(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    data_inicio = models.DateField('Data de Início', blank=True, null=True)
    data_fim = models.DateField('Data de Fim', blank=True, null=True)
    ano_sped = models.CharField('Ano do SPED', max_length=4, blank=True, null=True)
    mes_sped = models.CharField('Mês do SPED', max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = 'Análise em Andamento K25x'
        verbose_name_plural = 'Análises em Andamento K25x'
