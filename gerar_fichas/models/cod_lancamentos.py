from django.db import models

class Codigos_lancamentos(models.Model):
    cod_lancamento = models.CharField('Código de Lançamento', max_length=20, null=True, blank=True)
    descricao = models.CharField('Descrição', max_length=300, null=True, blank=True)

    class Meta:
        verbose_name = 'Código de Lançamento'
        verbose_name_plural = 'Códigos de Lançamentos'
