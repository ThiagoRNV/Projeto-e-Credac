from django.db import models
from validacao.models.outros_modelos.registroc500 import RegistroEnergiaC500
from cadastro.models.empresa import Empresa

class RegistroEnergiaC590(models.Model):

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=True)

    registro_c500 = models.ForeignKey(
        RegistroEnergiaC500,
        on_delete=models.CASCADE,
        related_name="analiticos",
        verbose_name="Documento de Energia (C500)"
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

    # REG: Texto fixo "C590"
    reg = models.CharField(
        max_length=4,
        default="C590",
        verbose_name="Código do Registro"
    )

    # CST_ICMS: Código da Situação Tributária do ICMS (3 caracteres, ex: 000)
    cst_icms = models.CharField(
        max_length=7,
        verbose_name="Código da Situação Tributária (CST)"
    )

    # CFOP: Código Fiscal de Operações e Prestações (4 caracteres, ex: 2252)
    cfop = models.CharField(
        max_length=4,
        verbose_name="Código Fiscal de Operações (CFOP)"
    )

    # ALIQ_ICMS: Alíquota do ICMS (Ex: 18.00)
    aliq_icms = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Alíquota do ICMS"
    )

    # VL_OPR: Valor da operação correspondente à combinação de CST, CFOP e alíquota
    vl_opr = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor da Operação"
    )

    # VL_BC_ICMS: Parcela correspondente à base de cálculo do ICMS
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

    # VL_RED_BC: Valor não tributado em função da redução da base de cálculo do ICMS
    vl_red_bc = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor da Redução da BC"
    )

    # COD_OBS: Código da observação do lançamento fiscal (aponta para o Registro 0460)
    cod_obs = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Código da Observação"
    )

    class Meta:
        verbose_name = "Registro C590"
        verbose_name_plural = "Registros C590"

    def __str__(self):
        return f"C590 - CFOP {self.cfop} - CST {self.cst_icms} (Doc: {self.registro_c500.num_doc})"
