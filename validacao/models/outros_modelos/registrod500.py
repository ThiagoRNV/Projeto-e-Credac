from django.db import models
from validacao.models.participantes.participantes import Participantes
from cadastro.models.empresa import Empresa

class RegistroComunicacaoD500(models.Model):

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', blank=True, null=True)

    # REG: Texto fixo "D500"
    reg = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default="D500",
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

    # COD_PART: Código do participante (aponta para o Registro 0150)
    cod_part = models.ForeignKey(
        Participantes,
        on_delete=models.CASCADE,
        max_length=60,
        blank=True,
        null=True,
        verbose_name="Código do Participante"
    )

    # COD_MOD: Código do modelo do documento fiscal (Ex: "21" ou "22" para Serviço de Comunicação/Telecomunicação)
    cod_mod = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name="Modelo do Documento"
    )

    # COD_SIT: Código da situação do documento fiscal
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

    # NUM_DOC: Número do documento fiscal
    num_doc = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Número do Documento"
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

    # VL_DOC: Valor total do documento fiscal
    vl_doc = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor Total do Documento"
    )

    # VL_DESC: Valor total do desconto
    vl_desc = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor Total do Desconto"
    )

    # VL_SERV: Valor da prestação de serviços
    vl_serv = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor do Serviço"
    )

    # VL_SERV_NT: Valor total dos serviços não-tributados pelo ICMS
    vl_serv_nt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor Serviços Não Tributados"
    )

    # VL_TERC: Valor total cobrado em nome de terceiros
    vl_terc = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor Cobrado de Terceiros"
    )

    # VL_DA: Valor total de despesas acessórias
    vl_da = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor Despesas Acessórias"
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

    # COD_INF: Código da informação complementar (aponta para o Registro 0450)
    cod_inf = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Código da Informação Complementar"
    )

    # VL_PIS: Valor do PIS
    vl_pis = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor do PIS"
    )

    # VL_COFINS: Valor da COFINS
    vl_cofins = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor da COFINS"
    )

    # COD_CTA: Código da conta analítica contábil debitada/creditada
    cod_cta = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Conta Contábil"
    )

    # TP_ASSINANTE: Código do tipo de assinante (1- Comercial/Industrial; 2- Poder Público; etc.)
    tp_assinante = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        verbose_name="Tipo de Assinante"
    )

    class Meta:
        verbose_name = "Registro D500"
        verbose_name_plural = "Registros D500"

    def __str__(self):
        return f"D500 - Doc {self.num_doc}"
