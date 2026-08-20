from typing import Dict, Any
from validacao.utils.normalizadores import normalizador_decimal, format_date
from cadastro.models.empresa import Empresa, EmpresaRegra
import datetime

class SPEDCampoDsProcess:

    def __init__(self, sped_file):
        self.sped_file = sped_file
        self.linhas_sped = []
        
    def load_sped_file(self) -> bool:
        try:
            self.sped_file.seek(0) # volta para o inicio do arquivo
            self.linhas_sped = [line.decode("utf-8", errors="ignore").strip() for line in self.sped_file]
            return True
        except Exception as e:
            print(f'Erro ao carregar SPED: {e}')
            return False
    
    def extract_camposDs(self) -> Dict[str, Any]:

        registo_D100 = []
        registro = d190 = []
        cnpj_empresa = []
        participantes_map = {}
        participantes = []

        list_mes = {
            "01": "Janeiro",
            "02": "Fevereiro",
            "03": "Março",
            "04": "Abril",
            "05": "Maio",
            "06": "Junho",
            "07": "Julho",
            "08": "Agosto",
            "09": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro",
        }

        data_inicio_para_retorno = None
        data_fim_para_retorno = None
        mes_ref_para_retorno = None

        data_inicio_sped_ok = None
        data_fim_sped_ok = None
        mes_referencia = None
        d100_atual = None
        c500_atual = None
        d500_atual = None

        try:
            for line in self.linhas_sped:
                parts = line.strip().split("|")

                if len(parts) > 1 and parts[1] == "0000":
                    cnpj = parts[7] if len(parts) > 7 else None
                    cnpj_empresa.append(cnpj)

                    empresa_id = Empresa.objects.filter(
                        cnpj=cnpj
                    ).values_list(
                        'id',
                        flat=True
                    ).first()

                    data_inicio_sped = parts[4] if len(parts) > 4 else None
                    data_fim_sped = parts[5] if len(parts) > 5 else None

                    if data_inicio_sped:
                        try:
                            data_inicio_sped_ok = format_date(data_inicio_sped)
                            data_inicio_para_retorno = data_inicio_sped_ok
                            mes_referencia = list_mes.get(data_inicio_sped[2:4])
                            mes_ref_para_retorno = mes_referencia
                        except (ValueError, TypeError) as e:
                            data_inicio_sped_ok = None
                            mes_referencia = None
                    else:
                        data_inicio_sped_ok = None
                        mes_referencia = None
                    if data_fim_sped:
                        try:
                            data_fim_sped_ok = format_date(data_fim_sped)
                            data_fim_para_retorno = data_fim_sped_ok
                        except (ValueError, TypeError) as e:
                            print(
                                f"⚠️ Erro ao processar data_fim_sped '{data_fim_sped}': {e}"
                            )
                            data_fim_sped_ok = None
                    else:
                        data_fim_sped_ok = None

                # 0150 -> Participante
                elif len(parts) > 1 and parts[1] == "0150":
                    cod_part = parts[2] if len(parts) > 2 else None
                    if cod_part not in participantes_map:
                        participante = {
                            "cod_part": cod_part,
                            "mes_referencia": mes_referencia,
                            "data_inicio_sped": data_inicio_sped_ok,
                            "data_fim_sped": data_fim_sped_ok,
                            "nome": parts[3] if len(parts) > 3 else None,
                            "codigo_pais": parts[4] if len(parts) > 4 else None,
                            "cnpj_cpf": parts[5] if len(parts) > 5 else None,
                            "ie": parts[6] if len(parts) > 6 else None,
                            "codigo_municipio": parts[7] if len(parts) > 7 else None,
                            "suframa": parts[8] if len(parts) > 8 else None,
                            "endereco": parts[10] if len(parts) > 10 else None,
                            "numero": parts[11] if len(parts) > 11 else None,
                            "complemento": parts[12] if len(parts) > 12 else None,
                            "bairro": parts[13] if len(parts) > 13 else None,
                            "phone": parts[14] if len(parts) > 14 else None,
                            "registrod100": [],
                            "registroc500": [],
                            "registrod500": [],
                        }
                        participantes.append(participante)
                        participantes_map[cod_part] = participante
                    nota_atual = None

                elif len(parts) > 1 and parts[1] == "D100":
                    cod_part = parts[4] if len(parts) > 4 else None
                    d100_atual = {
                        "registro": "D100",
                        "ind_oper": parts[2] if len(parts) > 2 else None,
                        "ind_emit": parts[3] if len(parts) > 3 else None,
                        "cod_mod": parts[5] if len(parts) > 5 else None,
                        "cod_sit": parts[6] if len(parts) > 6 else None,
                        "ser": parts[7] if len(parts) > 7 else None, 
                        "sub_serie": parts[8] if len(parts) > 8 else None,
                        "numero_doc": parts[9] if len(parts) > 9 else None,
                        "chave_cte": parts[10] if len(parts) > 10 else None, 
                        "data_cod": format_date(parts[11] if len(parts) > 11 else None),
                        "data_entrada": format_date(parts[12] if len(parts) > 12 else None),
                        "tipo_cte": parts[13] if len(parts) > 13 else None,
                        "chv_cte_rfe": parts[14] if len(parts) > 14 else None,
                        "valor_doc": normalizador_decimal(parts[15] if len(parts) > 15 else None),
                        "indicador_frete": parts[16] if len(parts) > 16 else None,
                        "valor_servico": normalizador_decimal(parts[17] if len(parts) > 17 else None), 
                        "valor_bc_icms": normalizador_decimal(parts[18] if len(parts) > 18 else None),
                        "valor_icms": normalizador_decimal(parts[19] if len(parts) > 19 else None),
                        "valor_ntributado": normalizador_decimal(parts[20] if len(parts) > 20 else None), 
                        "cod_inf": parts[21] if len(parts) > 21 else None,
                        "cod_cta": parts[22] if len(parts) > 22 else None,
                        "cod_mun_orig": parts[23] if len(parts) > 23 else None,
                        "cod_mun_dest": parts[24] if len(parts) > 24 else None,
                        "registroD190": []
                    }

                    if cod_part and cod_part in participantes_map:
                        participantes_map[cod_part]['registrod100'].append(d100_atual)

                elif len(parts) > 1 and parts[1] == "D190":
                    d190 = {
                        "registro": "D190",
                        "cst_icms": parts[2] if len(parts) > 2 else None,
                        "cfop": parts[3] if len(parts) > 3 else None,
                        "aliq_icms": normalizador_decimal(parts[4] if len(parts) > 4 else None),
                        "valor_operacao": normalizador_decimal(parts[5] if len(parts) > 5 else None),
                        "valor_bc_icms": normalizador_decimal(parts[6] if len(parts) > 6 else None),
                        "valor_icms": normalizador_decimal(parts[7] if len(parts) > 7 else None),
                        "valor_red_bc": normalizador_decimal(parts[8] if len(parts) > 8 else None),
                        "cod_obs": parts[9] if len(parts) > 9 else None
                    }

                    if d100_atual:
                        d100_atual['registroD190'].append(d190)

                # C500 -> Energia elétrica / água / gás
                elif len(parts) > 1 and parts[1] == "C500":
                    cod_part = parts[4] if len(parts) > 4 else None
                    c500_atual = {
                        "registro": "C500",
                        "ind_oper": parts[2] if len(parts) > 2 else None,
                        "ind_emit": parts[3] if len(parts) > 3 else None,
                        "cod_mod": parts[5] if len(parts) > 5 else None,
                        "cod_sit": parts[6] if len(parts) > 6 else None,
                        "ser": parts[7] if len(parts) > 7 else None,
                        "sub_serie": parts[8] if len(parts) > 8 else None,
                        "cod_cons": parts[9] if len(parts) > 9 else None,
                        "numero_doc": (parts[10] if len(parts) > 10 else None) or None,
                        "data_doc": format_date(parts[11] if len(parts) > 11 else None),
                        "data_entrada_saida": format_date(parts[12] if len(parts) > 12 else None),
                        "valor_doc": normalizador_decimal(parts[13] if len(parts) > 13 else None),
                        "valor_desc": normalizador_decimal(parts[14] if len(parts) > 14 else None),
                        "valor_forn": normalizador_decimal(parts[15] if len(parts) > 15 else None),
                        "valor_serv_nt": normalizador_decimal(parts[16] if len(parts) > 16 else None),
                        "valor_terc": normalizador_decimal(parts[17] if len(parts) > 17 else None),
                        "valor_da": normalizador_decimal(parts[18] if len(parts) > 18 else None),
                        "valor_bc_icms": normalizador_decimal(parts[19] if len(parts) > 19 else None),
                        "valor_icms": normalizador_decimal(parts[20] if len(parts) > 20 else None),
                        "valor_bc_icms_st": normalizador_decimal(parts[21] if len(parts) > 21 else None),
                        "valor_icms_st": normalizador_decimal(parts[22] if len(parts) > 22 else None),
                        "cod_inf": parts[23] if len(parts) > 23 else None,
                        "valor_pis": normalizador_decimal(parts[24] if len(parts) > 24 else None),
                        "valor_cofins": normalizador_decimal(parts[25] if len(parts) > 25 else None),
                        "tp_ligacao": parts[26] if len(parts) > 26 else None,
                        "cod_grupo_tensao": parts[27] if len(parts) > 27 else None,
                        "chv_doce": parts[28] if len(parts) > 28 else None,
                        "fin_doce": parts[29] if len(parts) > 29 else None,
                        "chv_doce_ref": parts[30] if len(parts) > 30 else None,
                        "ind_dest": parts[31] if len(parts) > 31 else None,
                        "cod_mun_dest": parts[32] if len(parts) > 32 else None,
                        "cod_cta": parts[33] if len(parts) > 33 else None,
                        "cod_mod_doc_ref": parts[34] if len(parts) > 34 else None,
                        "hash_doc_ref": parts[35] if len(parts) > 35 else None,
                        "ser_doc_ref": parts[36] if len(parts) > 36 else None,
                        "num_doc_ref": parts[37] if len(parts) > 37 else None,
                        "mes_doc_ref": parts[38] if len(parts) > 38 else None,
                        "ener_injet": normalizador_decimal(parts[39] if len(parts) > 39 else None),
                        "outras_ded": normalizador_decimal(parts[40] if len(parts) > 40 else None),
                        "registroC590": []
                    }

                    if cod_part and cod_part in participantes_map:
                        participantes_map[cod_part]['registroc500'].append(c500_atual)

                elif len(parts) > 1 and parts[1] == "C590":
                    c590 = {
                        "registro": "C590",
                        "cst_icms": parts[2] if len(parts) > 2 else None,
                        "cfop": parts[3] if len(parts) > 3 else None,
                        "aliq_icms": normalizador_decimal(parts[4] if len(parts) > 4 else None),
                        "valor_operacao": normalizador_decimal(parts[5] if len(parts) > 5 else None),
                        "valor_bc_icms": normalizador_decimal(parts[6] if len(parts) > 6 else None),
                        "valor_icms": normalizador_decimal(parts[7] if len(parts) > 7 else None),
                        "valor_bc_icms_st": normalizador_decimal(parts[8] if len(parts) > 8 else None),
                        "valor_icms_st": normalizador_decimal(parts[9] if len(parts) > 9 else None),
                        "valor_red_bc": normalizador_decimal(parts[10] if len(parts) > 10 else None),
                        "cod_obs": parts[11] if len(parts) > 11 else None
                    }

                    if c500_atual:
                        c500_atual['registroC590'].append(c590)

                # D500 -> Comunicação / telecomunicação
                elif len(parts) > 1 and parts[1] == "D500":
                    cod_part = parts[4] if len(parts) > 4 else None
                    d500_atual = {
                        "registro": "D500",
                        "ind_oper": parts[2] if len(parts) > 2 else None,
                        "ind_emit": parts[3] if len(parts) > 3 else None,
                        "cod_mod": parts[5] if len(parts) > 5 else None,
                        "cod_sit": parts[6] if len(parts) > 6 else None,
                        "ser": parts[7] if len(parts) > 7 else None,
                        "sub_serie": parts[8] if len(parts) > 8 else None,
                        "numero_doc": (parts[9] if len(parts) > 9 else None) or None,
                        "data_doc": format_date(parts[10] if len(parts) > 10 else None),
                        "data_entrada_prestacao": format_date(parts[11] if len(parts) > 11 else None),
                        "valor_doc": normalizador_decimal(parts[12] if len(parts) > 12 else None),
                        "valor_desc": normalizador_decimal(parts[13] if len(parts) > 13 else None),
                        "valor_servico": normalizador_decimal(parts[14] if len(parts) > 14 else None),
                        "valor_serv_nt": normalizador_decimal(parts[15] if len(parts) > 15 else None),
                        "valor_terc": normalizador_decimal(parts[16] if len(parts) > 16 else None),
                        "valor_da": normalizador_decimal(parts[17] if len(parts) > 17 else None),
                        "valor_bc_icms": normalizador_decimal(parts[18] if len(parts) > 18 else None),
                        "valor_icms": normalizador_decimal(parts[19] if len(parts) > 19 else None),
                        "cod_inf": parts[20] if len(parts) > 20 else None,
                        "valor_pis": normalizador_decimal(parts[21] if len(parts) > 21 else None),
                        "valor_cofins": normalizador_decimal(parts[22] if len(parts) > 22 else None),
                        "cod_cta": parts[23] if len(parts) > 23 else None,
                        "tp_assinante": parts[24] if len(parts) > 24 else None,
                        "registroD590": []
                    }

                    if cod_part and cod_part in participantes_map:
                        participantes_map[cod_part]['registrod500'].append(d500_atual)

                elif len(parts) > 1 and parts[1] == "D590":
                    d590 = {
                        "registro": "D590",
                        "cst_icms": parts[2] if len(parts) > 2 else None,
                        "cfop": parts[3] if len(parts) > 3 else None,
                        "aliq_icms": normalizador_decimal(parts[4] if len(parts) > 4 else None),
                        "valor_operacao": normalizador_decimal(parts[5] if len(parts) > 5 else None),
                        "valor_bc_icms": normalizador_decimal(parts[6] if len(parts) > 6 else None),
                        "valor_icms": normalizador_decimal(parts[7] if len(parts) > 7 else None),
                        "valor_bc_icms_st": normalizador_decimal(parts[8] if len(parts) > 8 else None),
                        "valor_icms_st": normalizador_decimal(parts[9] if len(parts) > 9 else None),
                        "valor_red_bc": normalizador_decimal(parts[10] if len(parts) > 10 else None),
                        "cod_obs": parts[11] if len(parts) > 11 else None
                    }

                    if d500_atual:
                        d500_atual['registroD590'].append(d590)

            return {
                "participantes": participantes,
                "cnpj_empresa": cnpj_empresa,
                "data_inicio_sped": data_inicio_para_retorno,
                "data_fim_sped": data_fim_para_retorno,
                "mes_referencia": mes_ref_para_retorno,
            }
        except Exception as e:
            print(f"Erro ao processar linhas do SPED: {e}")
            return {
                "participantes": [],
                "cnpj_empresa": [],
                "data_inicio_sped": None,
                "data_fim_sped": None,
                "mes_referencia": None,
            }
 




        