from random import choices
from django.db import models 

class Empresa(models.Model):
    razao_social = models.CharField('Razão Social', max_length=70, null=True, blank=True )
    email = models.EmailField('E-mail', null=True, blank=True)
    cnpj = models.CharField('CNPJ', max_length=18, null=True, blank=True)
    cnae = models.CharField('CNAE', max_length=50, null=True, blank=True)
    inscricao_estadual = models.CharField('Inscrição Estadual', max_length=20, null=True, blank=True)
    ladca = models.CharField('Empresa', max_length=4, null=True, blank=True)
    cod_ver = models.CharField('Código de Verificação', max_length=18, null=True, blank=True)
    cod_fin = models.CharField('Código Financeiro', max_length=18, null=True, blank=True)
    opc_cred_outorgado = models.CharField('Opcão de Crédito Outorgado', max_length=20, null=True, blank=True)
    inscricao_estadual_intima = models.CharField('Inscrição Estadual Intima',max_length=20, null=True, blank=True) 
    uf = models.CharField('UF', max_length=2, null=True, blank=True)
    indicador_atividade = models.CharField('Indicador de Atividade', max_length=2, null=True, blank=True)
    indicador_movimento = models.CharField('Indicador de Movimento', max_length=2, null=True, blank=True)
    indicador_perfil = models.CharField('Indicador de perfil', max_length=4, null=True, blank=True)
    configuracao = models.CharField('Configuração', max_length=50, null=True, blank=True)
    codigo_municipio = models.CharField('Código do Município', max_length=50, null=True, blank=True)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=70, null=True, blank=True)
    cep = models.CharField('CEP', max_length=10, null=True, blank=True)
    endereco = models.CharField('Endereço', max_length=100, null=True, blank=True)
    numero_endereco = models.CharField('Número do Endereço', max_length=10, null=True, blank=True)
    complemento = models.CharField('Complemento', max_length=50, null=True, blank=True)
    bairro = models.CharField('Bairro', max_length=50, null=True, blank=True)
    telefone = models.CharField('Telefone', max_length=20, null=True, blank=True)
    metodo_rateio = models.CharField('Método de Rateio', max_length=50, null=True, blank=True)
    status = models.BooleanField('Status', default=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.razao_social

class Regra(models.Model):  

    TIPO_CHOICE = [
        ('prefixo', 'Prefixo'),
        ('tamanho', 'tamanho'), 
        ('formato', 'Formato'),
        ('caractere', 'Caractere'),
        ('sufixo', 'Sufixo'),
    ]

    regra = models.CharField(max_length=50, null=True, blank=True, verbose_name='Regra:')
    tipo = models.CharField('De qual tipo é:', max_length=100, null=True, blank=True, choices=TIPO_CHOICE)

    
    def __str__(self):
        return self.regra

class EmpresaRegra(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Empresa:')
    regra = models.ForeignKey(Regra, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Regra:')
    # tipo = models.CharField('Tipo')
    status = models.BooleanField('Status:', default=False)
