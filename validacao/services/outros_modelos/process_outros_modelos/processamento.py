from validacao.parser.outros_modelos.extract_campoServicos import SPEDCampoDsProcess
from validacao.models.outros_modelos.registrod100 import RegistroTransporteD100
from validacao.models.outros_modelos.registrod190 import RegistroTransporteD190
from validacao.models.outros_modelos.registroc500 import RegistroEnergiaC500
from validacao.models.outros_modelos.registroc590 import RegistroEnergiaC590
from validacao.models.outros_modelos.registrod500 import RegistroComunicacaoD500
from validacao.models.outros_modelos.registrod590 import RegistroComunicacaoD590
from validacao.models.participantes.participantes import Participantes
from validacao.models.painel_controle.validacao import ValidacaoStatus
import logging
from cadastro.models.empresa import Empresa
logger = logging.getLogger(__name__)
from datetime import datetime, timezone

""" Tratamentos de erros """
class SpedException(Exception):
    pass

class SpedFormatError(SpedException):
    def __init__(self, message='O arquivo deve ser .txt') -> None:
        super().__init__(message)
    
class SpedError(SpedException):
    pass

class LoadSpedFileError(SpedException):
    pass

class EmptyList(SpedException):
    def __init__(self, message='Não é possível fazer o processamento. Empresa está inativa') -> None:
        super().__init__(message)

class CompaineError(SpedException):
    def __init__(self, message='Empresa não cadastrada') -> None:
        super().__init__(message)



class ProcessServices:
    def __init__(self, sped_file) -> None:
        self.sped_file = sped_file
        print(f'sped file: {self.sped_file}')

    def processamento_service(self):
        if not self.sped_file:
            logger.error("Nenhum arquivo SPED enviado")
            raise SpedError()

        if not self.sped_file.name.endswith('.txt'):
            logger.error('O arquivo SPED deve ser um arquivo .txt.')
            raise SpedFormatError()

        campoD_extract = SPEDCampoDsProcess(self.sped_file)

        if not campoD_extract.load_sped_file():
            logger.error("Erro ao carregar o arquivo SPED.")
            raise LoadSpedFileError()

        dados = campoD_extract.extract_camposDs()

        ver_list_cnpj_empresa = dados.get('cnpj_empresa', [])

        if not ver_list_cnpj_empresa:
            raise EmptyList()

        cnpj_empresa = None
        if ver_list_cnpj_empresa:
            cnpj_empresa = dados.get('cnpj_empresa', [])[0]
        empresa_obj = Empresa.objects.filter(cnpj=cnpj_empresa).first()

        if not empresa_obj:
            raise CompaineError()

        

        mes_ref = dados.get('mes_referencia')
        for part in dados.get("participantes", []):
            try:
                part_obj, _ = Participantes.objects.get_or_create(
                    cod_part=part.get('cod_part'),
                    empresa=empresa_obj,
                    data_inicio_sped=part.get('data_inicio_sped'),
                    defaults={
                        'data_fim_sped': part.get('data_fim_sped'),
                        'nome': part.get('nome'),
                        'cnpj_cpf': part.get('cnpj_cpf'),
                        'ie': part.get('ie'),
                        'endereco': part.get('endereco'),
                        'numero': part.get('numero'),
                        'complemento': part.get('complemento'),
                        'bairro': part.get('bairro'),
                        'codigo_municipio': part.get('codigo_municipio'),
                        'codigo_pais': part.get('codigo_pais'),
                        'suframa': part.get('suframa'),
                        'phone': part.get('suframa'),
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao criar Participante: {e}")
                raise SpedException() from e
                

            for r_d100 in part.get('registrod100', []):
                try:
                    d100_obj = RegistroTransporteD100.objects.create(
                        reg=r_d100.get('registro'),
                        ind_oper=r_d100.get("ind_oper"),
                        ind_emit=r_d100.get("ind_emit"),
                        cod_part=part_obj,  # FK
                        cod_mod=r_d100.get("cod_mod"),
                        cod_sit=r_d100.get("cod_sit"),
                        ser=r_d100.get("ser"),
                        sub=r_d100.get("sub_serie"),
                        num_doc=r_d100.get("numero_doc"),
                        chv_cte=r_d100.get("chave_cte"),
                        dt_doc=r_d100.get("data_cod"),
                        dt_a_p=r_d100.get("data_entrada"),
                        tp_cte=r_d100.get("tipo_cte"),
                        chv_cte_ref=r_d100.get("chv_cte_rfe"),
                        vl_doc=r_d100.get("valor_doc"),
                        ind_frt=r_d100.get("indicador_frete"),
                        vl_serv=r_d100.get("valor_servico"),
                        vl_bc_icms=r_d100.get("valor_bc_icms"),
                        vl_icms=r_d100.get("valor_icms"),
                        vl_nt=r_d100.get("valor_ntributado"),
                        cod_inf=r_d100.get("cod_inf"),
                        cod_cta=r_d100.get("cod_cta"),
                        cod_mun_orig=r_d100.get("cod_mun_orig"),
                        cod_mun_dest=r_d100.get("cod_mun_dest"),
                        data_inicio_sped=part_obj.data_inicio_sped,
                        data_final_sped=part_obj.data_fim_sped,
                        empresa=empresa_obj
                    )
                except Exception as e:
                    logger.error(f"Erro ao criar Registro D100: {e}")
                    raise SpedException() from e

                for r_d190 in r_d100.get('registroD190', []):
                    try:
                        RegistroTransporteD190.objects.create(
                            registro_d100=d100_obj,  # 🔥 ligação com D100
                            cst_icms=r_d190.get("cst_icms"),
                            cfop=r_d190.get("cfop"),
                            aliq_icms=r_d190.get("aliq_icms"),
                            vl_opr=r_d190.get("valor_operacao"),
                            vl_bc_icms=r_d190.get("valor_bc_icms"),
                            vl_icms=r_d190.get("valor_icms"),
                            vl_red_bc=r_d190.get("valor_red_bc"),
                            cod_obs=r_d190.get("cod_obs"),
                            data_inicio_sped=d100_obj.data_inicio_sped,
                            data_final_sped=d100_obj.data_final_sped,
                            empresa=empresa_obj
                        )
                    except Exception as e:
                        logger.error(f"Erro ao criar Registro D190: {e}")
                        raise SpedException() from e

            # Energia (C500 -> C590)
            for r_c500 in part.get('registroc500', []):
                try:
                    c500_obj = RegistroEnergiaC500.objects.create(
                        reg=r_c500.get('registro'),
                        ind_oper=r_c500.get("ind_oper"),
                        ind_emit=r_c500.get("ind_emit"),
                        cod_part=part_obj,  # FK
                        cod_mod=r_c500.get("cod_mod"),
                        cod_sit=r_c500.get("cod_sit"),
                        ser=r_c500.get("ser"),
                        sub=r_c500.get("sub_serie"),
                        cod_cons=r_c500.get("cod_cons"),
                        num_doc=r_c500.get("numero_doc"),
                        dt_doc=r_c500.get("data_doc"),
                        dt_e_s=r_c500.get("data_entrada_saida"),
                        vl_doc=r_c500.get("valor_doc") or 0,
                        vl_desc=r_c500.get("valor_desc") or 0,
                        vl_forn=r_c500.get("valor_forn") or 0,
                        vl_serv_nt=r_c500.get("valor_serv_nt") or 0,
                        vl_terc=r_c500.get("valor_terc") or 0,
                        vl_da=r_c500.get("valor_da") or 0,
                        vl_bc_icms=r_c500.get("valor_bc_icms") or 0,
                        vl_icms=r_c500.get("valor_icms") or 0,
                        vl_bc_icms_st=r_c500.get("valor_bc_icms_st") or 0,
                        vl_icms_st=r_c500.get("valor_icms_st") or 0,
                        cod_inf=r_c500.get("cod_inf"),
                        vl_pis=r_c500.get("valor_pis") or 0,
                        vl_cofins=r_c500.get("valor_cofins") or 0,
                        tp_ligacao=r_c500.get("tp_ligacao"),
                        cod_grupo_tensao=r_c500.get("cod_grupo_tensao"),
                        chv_doce=r_c500.get("chv_doce"),
                        fin_doce=r_c500.get("fin_doce"),
                        chv_doce_ref=r_c500.get("chv_doce_ref"),
                        ind_dest=r_c500.get("ind_dest"),
                        cod_mun_dest=r_c500.get("cod_mun_dest"),
                        cod_cta=r_c500.get("cod_cta"),
                        cod_mod_doc_ref=r_c500.get("cod_mod_doc_ref"),
                        hash_doc_ref=r_c500.get("hash_doc_ref"),
                        ser_doc_ref=r_c500.get("ser_doc_ref"),
                        num_doc_ref=r_c500.get("num_doc_ref"),
                        mes_doc_ref=r_c500.get("mes_doc_ref"),
                        ener_injet=r_c500.get("ener_injet") or 0,
                        outras_ded=r_c500.get("outras_ded") or 0,
                        data_inicio_sped=part_obj.data_inicio_sped,
                        data_final_sped=part_obj.data_fim_sped,
                        mes_referencia=mes_ref,
                        empresa=empresa_obj
                    )
                except Exception as e:
                    logger.error(f"Erro ao criar Registro C500: {e}")
                    raise SpedException() from e

                for r_c590 in r_c500.get('registroC590', []):
                    try:
                        RegistroEnergiaC590.objects.create(
                            registro_c500=c500_obj,  # 🔥 ligação com C500
                            cst_icms=r_c590.get("cst_icms"),
                            cfop=r_c590.get("cfop"),
                            aliq_icms=r_c590.get("aliq_icms") or 0,
                            vl_opr=r_c590.get("valor_operacao") or 0,
                            vl_bc_icms=r_c590.get("valor_bc_icms") or 0,
                            vl_icms=r_c590.get("valor_icms") or 0,
                            vl_bc_icms_st=r_c590.get("valor_bc_icms_st") or 0,
                            vl_icms_st=r_c590.get("valor_icms_st") or 0,
                            vl_red_bc=r_c590.get("valor_red_bc") or 0,
                            cod_obs=r_c590.get("cod_obs"),
                            data_inicio_sped=c500_obj.data_inicio_sped,
                            data_final_sped=c500_obj.data_final_sped,
                            mes_referencia=mes_ref,
                            empresa=empresa_obj
                        )
                    except Exception as e:
                        logger.error(f"Erro ao criar Registro C590: {e}")
                        raise SpedException() from e

            # Comunicação (D500 -> D590)
            for r_d500 in part.get('registrod500', []):
                try:
                    d500_obj = RegistroComunicacaoD500.objects.create(
                        reg=r_d500.get('registro'),
                        ind_oper=r_d500.get("ind_oper"),
                        ind_emit=r_d500.get("ind_emit"),
                        cod_part=part_obj,  # FK
                        cod_mod=r_d500.get("cod_mod"),
                        cod_sit=r_d500.get("cod_sit"),
                        ser=r_d500.get("ser"),
                        sub=r_d500.get("sub_serie"),
                        num_doc=r_d500.get("numero_doc"),
                        dt_doc=r_d500.get("data_doc"),
                        dt_a_p=r_d500.get("data_entrada_prestacao"),
                        vl_doc=r_d500.get("valor_doc") or 0,
                        vl_desc=r_d500.get("valor_desc") or 0,
                        vl_serv=r_d500.get("valor_servico") or 0,
                        vl_serv_nt=r_d500.get("valor_serv_nt") or 0,
                        vl_terc=r_d500.get("valor_terc") or 0,
                        vl_da=r_d500.get("valor_da") or 0,
                        vl_bc_icms=r_d500.get("valor_bc_icms") or 0,
                        vl_icms=r_d500.get("valor_icms") or 0,
                        cod_inf=r_d500.get("cod_inf"),
                        vl_pis=r_d500.get("valor_pis") or 0,
                        vl_cofins=r_d500.get("valor_cofins") or 0,
                        cod_cta=r_d500.get("cod_cta"),
                        tp_assinante=r_d500.get("tp_assinante"),
                        data_inicio_sped=part_obj.data_inicio_sped,
                        data_final_sped=part_obj.data_fim_sped,
                        mes_referencia=mes_ref,
                        empresa=empresa_obj
                    )
                except Exception as e:
                    logger.error(f"Erro ao criar Registro D500: {e}")
                    raise SpedException() from e

                for r_d590 in r_d500.get('registroD590', []):
                    try:
                        RegistroComunicacaoD590.objects.create(
                            registro_d500=d500_obj,  # 🔥 ligação com D500
                            cst_icms=r_d590.get("cst_icms"),
                            cfop=r_d590.get("cfop"),
                            aliq_icms=r_d590.get("aliq_icms") or 0,
                            vl_opr=r_d590.get("valor_operacao") or 0,
                            vl_bc_icms=r_d590.get("valor_bc_icms") or 0,
                            vl_icms=r_d590.get("valor_icms") or 0,
                            vl_bc_icms_st=r_d590.get("valor_bc_icms_st") or 0,
                            vl_icms_st=r_d590.get("valor_icms_st") or 0,
                            vl_red_bc=r_d590.get("valor_red_bc") or 0,
                            cod_obs=r_d590.get("cod_obs"),
                            data_inicio_sped=d500_obj.data_inicio_sped,
                            data_final_sped=d500_obj.data_final_sped,
                            mes_referencia=mes_ref,
                            empresa=empresa_obj
                        )
                    except Exception as e:
                        logger.error(f"Erro ao criar Registro D590: {e}")
                        raise SpedException() from e

        ValidacaoStatus.objects.create(
                empresa=empresa_obj,
                status='em_andamento',
                progresso=0,
                # data_atualizacao=timezone.now(),
                data_sped=dados.get('data_inicio_sped'),
                sped=True,
                mes_sped=mes_ref,
                tipo_validacao='outros_modelos'
            )

        return {'success': True, 'empresa_obj': empresa_obj}
        