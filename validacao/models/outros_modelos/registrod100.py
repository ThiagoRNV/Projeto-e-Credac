from django.db import models
from validacao.models.participantes.participantes import Participantes
from cadastro.models.empresa import Empresa

class RegistroTransporteD100(models.Model):
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', blank=True, null=True)
    
    # REG: Texto fixo "D100"
    reg = models.CharField(
        max_length=4,
        blank=True,
        null=True, 
        default="D100", 
        verbose_name="Código do Registro"
    )
    
    data_inicio_sped = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data inicio sped"
    )

    data_final_sped = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data final sped"
    )

    mes_referencia = models.CharField('Mês referencia', max_length=9, null=True, blank=True)

    # IND_OPER: Indicador do tipo de operação (0- Aquisição/Entrada; 1- Prestação/Saída)
    ind_oper = models.CharField(
        max_length=1,
        blank=True,
        null=True, 
        verbose_name="Indicador do Tipo de Operação"
    )
    
    # IND_EMIT: Indicador do emitente do documento fiscal (0- Emissão própria; 1- Terceiros)
    ind_emit = models.CharField(
        max_length=1,
        blank=True,
        null=True, 
        verbose_name="Indicador do Emitente"
    )
    
    # COD_PART: Código do participante (emitente ou destinatário - aponta para o Registro 0150)
    cod_part = models.ForeignKey(
        Participantes,
        on_delete=models.CASCADE,
        max_length=60,
        blank=True,
        null=True,
        verbose_name="Código do Participante"
    )
    
    # COD_MOD: Código do modelo do documento fiscal (Ex: "57" para CT-e)
    cod_mod = models.CharField(
        max_length=2,
        blank=True,
        null=True, 
        verbose_name="Modelo do Documento"
    )
    
    # COD_SIT: Código da situação do documento fiscal (Ex: "00" para Documento Regular)
    cod_sit = models.CharField(
        max_length=2,
        blank=True,
        null=True, 
        verbose_name="Código da Situação"
    )
    
    # SER: Série do documento fiscal
    ser = models.CharField(
        max_length=4, 
        blank=True, 
        null=True, 
        verbose_name="Série"
    )
    
    # SUB: Subsérie do documento fiscal
    sub = models.CharField(
        max_length=7, 
        blank=True, 
        null=True, 
        verbose_name="Subsérie"
    )
    
    # NUM_DOC: Número do documento fiscal (Ex: 2443531)
    num_doc = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Número do Documento"
    )
    
    # CHV_CTE: Chave do Conhecimento de Transporte Eletrônico (44 caracteres)
    chv_cte = models.CharField(
        max_length=44, 
        blank=True, 
        null=True, 
        verbose_name="Chave do CT-e"
    )
    
    # DT_DOC: Data da emissão do documento fiscal
    dt_doc = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Emissão"
    )
    
    # DT_A_P: Data da entrada (aquisição) ou da saída (prestação do serviço)
    dt_a_p = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data de Entrada/Prestação"
    )
    
    # TP_CT_E: Tipo de CT-e conforme tabela indicada no guia
    tp_cte = models.IntegerField(
        verbose_name="Tipo do CT-e"
    )
    
    # CHV_CTE_REF: Chave do CT-e de referência (se houver)
    chv_cte_ref = models.CharField(
        max_length=44, 
        blank=True, 
        null=True, 
        verbose_name="Chave do CT-e de Referência"
    )
    
    # VL_DOC: Valor total do documento fiscal
    vl_doc = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name="Valor Total do Documento"
    )
    
    # VL_DESC: Valor total do desconto
    vl_desc = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Valor Total do Desconto"
    )
    
    # IND_FRT: Indicador do tipo do frete (0- Emitente; 1- Destinatário; 2- Terceiros; 9- Sem frete)
    ind_frt = models.CharField(
        blank=True,
        null=True,
        max_length=1, 
        verbose_name="Indicador do Frete"
    )
    
    # VL_SERV: Valor total da prestação de serviço
    vl_serv = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name="Valor do Serviço"
    )
    
    # VL_BC_ICMS: Valor da base de cálculo do ICMS
    vl_bc_icms = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Base de Cálculo do ICMS"
    )
    
    # VL_ICMS: Valor do ICMS
    vl_icms = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Valor do ICMS"
    )
    
    # VL_NT: Valor não tributado do ICMS (isentas ou não tributadas)
    vl_nt = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Valor Não Tributado"
    )
    
    # COD_INF: Código da informação complementar (se houver, aponta para o Registro 0450)
    cod_inf = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name="Código da Informação Complementar"
    )
    
    # COD_CTA: Código da conta analítica contábil debitada/creditada
    cod_cta = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Conta Contábil"
    )
    
    # COD_MUN_ORIG: Código do município de origem do serviço (Tabela IBGE)
    cod_mun_orig = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name="Código IBGE do Município de Origem"
    )
    
    # COD_MUN_DEST: Código do município de destino do serviço (Tabela IBGE)
    cod_mun_dest = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name="Código IBGE do Município de Destino"
    )

    class Meta:
        verbose_name = "Registro D100"
        verbose_name_plural = "Registros D100"

    def __str__(self):
        return f"D100 - CT-e {self.num_doc} (Chave: {self.chv_cte[:6]}...)"