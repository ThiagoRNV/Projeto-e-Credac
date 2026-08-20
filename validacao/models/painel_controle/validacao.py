from django.db import models  # type: ignore
from cadastro.models.empresa import Empresa
from django.utils import timezone

 
class ValidacaoStatus(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em andamento'),
        ('concluido', 'Concluído'),
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='validacoes',
        verbose_name='Empresa',
    )
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='em_andamento')
    progresso = models.PositiveIntegerField('Progresso', default=0)
    data_inicio = models.DateTimeField('Data de Início', default=timezone.now)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    data_sped = models.DateField('Data do SPED', null=True, blank=True)
    sped = models.BooleanField('SPED', default=False)
    xml = models.BooleanField('XML', default=False)
    due = models.BooleanField('DUE', default=False)
    mes_sped = models.CharField('Mês do SPED', max_length=20, null=True, blank=True)
    tipo_validacao = models.CharField('Tipo documento', max_length=15, null=True, blank=True)


    class Meta:
        verbose_name = 'Status da Validação'
        verbose_name_plural = 'Status das Validações'

    def __str__(self):
        return f"{self.empresa.razao_social} - {self.get_status_display()} ({self.progresso}%)"
''

class ValidacaoDataConcluida(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='datas_concluidas',
        verbose_name='Empresa',
    )
    data_sped = models.DateField('Data do SPED')
    criado_em = models.DateTimeField('Criado Em', default=timezone.now)
    mes_sped = models.CharField('Mês do SPED', max_length=20, null=True, blank=True)
    tipo_validacao = models.CharField('Tipo documento', max_length=15, null=True, blank=True)

    class Meta:
        verbose_name = 'Data de Validação Concluída'
        verbose_name_plural = 'Datas de Validação Concluídas'
        unique_together = ('empresa', 'data_sped', 'tipo_validacao')

    
    def __str__(self):
        return f"{self.empresa.razao_social} - {self.data_sped} concluída"


   
