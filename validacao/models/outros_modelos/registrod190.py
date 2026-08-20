from django.db import models
from validacao.models.outros_modelos.registrod100 import RegistroTransporteD100
from cadastro.models.empresa import Empresa

class RegistroTransporteD190(models.Model):

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=True)


    registro_d100 = models.ForeignKey(
        RegistroTransporteD100, 
        on_delete=models.CASCADE, 
        related_name="analiticos",
        verbose_name="Documento de Transporte (D100)"
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

    # REG: Texto fixo "D190"
    reg = models.CharField(
        max_length=4, 
        default="D190", 
        verbose_name="Código do Registro"
    )
    
    # CST_ICMS: Código da Situação Tributária do ICMS (3 caracteres, ex: 090)
    cst_icms = models.CharField(
        max_length=7, 
        verbose_name="Código da Situação Tributária (CST)"
    )
    
    # CFOP: Código Fiscal de Operações e Prestações (4 caracteres, ex: 1352)
    cfop = models.CharField(
        max_length=4, 
        verbose_name="Código Fiscal de Operações (CFOP)"
    )
    
    # ALIQ_ICMS: Alíquota do ICMS (Ex: 12.00, 18.00)
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
    
    # VL_RED_BC: Valor da base de cálculo do ICMS substituição tributária (ou redução da BC)
    vl_red_bc = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Valor da Redução da BC / ICMS-ST"
    )
    
    # COD_OBS: Código da observação do lançamento fiscal (opcional, aponta para o Registro 0460)
    cod_obs = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Código da Observação"
    )

    class Meta:
        verbose_name = "Registro D190"
        verbose_name_plural = "Registros D190"

    def __str__(self):
        return f"D190 - CFOP {self.cfop} - CST {self.cst_icms} (Doc: {self.registro_d100.num_doc})"