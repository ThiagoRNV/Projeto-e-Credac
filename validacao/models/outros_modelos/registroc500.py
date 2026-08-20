from django.db import models
from validacao.models.participantes.participantes import Participantes
from cadastro.models.empresa import Empresa

class RegistroEnergiaC500(models.Model):

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', blank=True, null=True)

    # REG: Texto fixo "C500"
    reg = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default="C500",
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

    # COD_MOD: Código do modelo do documento fiscal (Ex: "06" para Nota Fiscal/Conta de Energia Elétrica)
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

    # COD_CONS: Código de classe de consumo de energia elétrica
    cod_cons = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name="Classe de Consumo"
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

    # DT_E_S: Data da entrada ou da saída
    dt_e_s = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Entrada/Saída"
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

    # VL_FORN: Valor total fornecido/consumido
    vl_forn = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor Fornecido/Consumido"
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

    # VL_BC_ICMS_ST: Valor da base de cálculo do ICMS substituição tributária
    vl_bc_icms_st = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Base de Cálculo do ICMS-ST"
    )

    # VL_ICMS_ST: Valor do ICMS retido por substituição tributária
    vl_icms_st = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor do ICMS-ST"
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

    # TP_LIGACAO: Código de tipo de ligação (1- Monofásico; 2- Bifásico; 3- Trifásico)
    tp_ligacao = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        verbose_name="Tipo de Ligação"
    )

    # COD_GRUPO_TENSAO: Código de grupo de tensão
    cod_grupo_tensao = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name="Grupo de Tensão"
    )

    # CHV_DOCe: Chave da Nota Fiscal de Energia Elétrica Eletrônica
    chv_doce = models.CharField(
        max_length=44,
        blank=True,
        null=True,
        verbose_name="Chave do Documento Eletrônico"
    )

    # FIN_DOCe: Finalidade da emissão do documento eletrônico
    fin_doce = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        verbose_name="Finalidade do Documento Eletrônico"
    )

    # CHV_DOCe_REF: Chave do documento eletrônico referenciado
    chv_doce_ref = models.CharField(
        max_length=44,
        blank=True,
        null=True,
        verbose_name="Chave do Documento Eletrônico Referenciado"
    )

    # IND_DEST: Indicador do destinatário/acessante
    ind_dest = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        verbose_name="Indicador do Destinatário"
    )

    # COD_MUN_DEST: Código do município do destinatário (Tabela IBGE)
    cod_mun_dest = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Código IBGE do Município do Destinatário"
    )

    # COD_CTA: Código da conta analítica contábil debitada/creditada
    cod_cta = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Conta Contábil"
    )

    # COD_MOD_DOC_REF: Código do modelo do documento fiscal referenciado
    cod_mod_doc_ref = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name="Modelo do Documento Referenciado"
    )

    # HASH_DOC_REF: Código de autenticação digital do registro
    hash_doc_ref = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name="Hash do Documento Referenciado"
    )

    # SER_DOC_REF: Série do documento fiscal referenciado
    ser_doc_ref = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name="Série do Documento Referenciado"
    )

    # NUM_DOC_REF: Número do documento fiscal referenciado
    num_doc_ref = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        verbose_name="Número do Documento Referenciado"
    )

    # MES_DOC_REF: Mês e ano da emissão do documento fiscal referenciado (MMAAAA)
    mes_doc_ref = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name="Mês/Ano do Documento Referenciado"
    )

    # ENER_INJET: Energia injetada
    ener_injet = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Energia Injetada"
    )

    # OUTRAS_DED: Outras deduções
    outras_ded = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Outras Deduções"
    )

    class Meta:
        verbose_name = "Registro C500"
        verbose_name_plural = "Registros C500"

    def __str__(self):
        return f"C500 - Doc {self.num_doc}"
