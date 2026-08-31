from typing import Any, Dict, Optional
from datetime import datetime

from validacao.utils.normalizadores import normalizador_decimal, _norm
from cadastro.models.empresa import EmpresaRegra
from cadastro.models.empresa import Empresa
from regras_companies.validacao import ValidarRegra
from decimal import Decimal

class SPEDProcesses:
    """
    Classe para processar arquivos SPED enviados via formulário (sped_files).
    """

    def __init__(self, sped_file):
        """
        :param sped_file: arquivo enviado via request.FILES['sped_files']
        """
        self.sped_file = sped_file
        self.linhas_sped = []

    def load_sped_file(self) -> bool:
        try:
            self.sped_file.seek(0)  # volta para o início do arquivo
            self.linhas_sped = [
                line.decode("utf-8", errors="ignore").strip() for line in self.sped_file
            ]

            return True
        except Exception as e:
            print(f"Erro ao carregar SPED: {e}") 
            return False

    # Função pra ler, extrair e retornar os dados como Dict (Dicionário)
    def extract_values_sped(self) -> Dict[str, Any]:

        participantes = []
        catalogo_produtos = {}
        produtos_sem_cadastro = []
        cnpj_empresa = []
        nota_atual = None
        participantes_map = {}
        cadastro_itens_sped = []
        # Variáveis para armazenar dados do registro 0000
        # IMPORTANTE: Estas variáveis são atualizadas a cada registro 0000 encontrado
        data_inicio_sped_ok = None
        data_fim_sped_ok = None
        mes_referencia = None
        data_inicio_sped = None
        data_fim_sped = None

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

        for line in self.linhas_sped:
            parts = line.strip().split("|")

            # 0000 -> CNPJ da empresa, data_inicio e data_fim
            # ✅ CRÍTICO: Sempre atualizar as datas quando encontrar um novo registro 0000
            if len(parts) > 1 and parts[1] == "0000":

                cnpj = parts[7] if len(parts) > 7 else None

                cnpj_empresa.append(cnpj)

                empresa_id = Empresa.objects.filter(
                    cnpj=cnpj,
                    status=True,
                ).values_list(
                    'id',
                    flat=True
                ).first()

                empresa_regras = EmpresaRegra.objects.filter(empresa_id=empresa_id, status=True).select_related('regra')

                data_inicio_sped = parts[4] if len(parts) > 4 else None
                data_fim_sped = parts[5] if len(parts) > 5 else None

                # Garatindo que sempre exista
                data_inicio_sped_ok = None

                if data_inicio_sped:
                    try:
                        data_inicio_sped_ok = datetime.strptime(
                            data_inicio_sped, "%d%m%Y"
                        ).date()
                        mes_referencia = list_mes.get(data_inicio_sped[2:4])
                    except (ValueError, TypeError) as e:
                        data_inicio_sped_ok = None
                        mes_referencia = None
                else:
                    data_inicio_sped_ok = None
                    mes_referencia = None

                if data_fim_sped:
                    try:
                        data_fim_sped_ok = datetime.strptime(
                            data_fim_sped, "%d%m%Y"
                        ).date()
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
                        "notas": [],
                    }
                    participantes.append(participante)
                    participantes_map[cod_part] = participante
                nota_atual = None

                
            elif len(parts) > 1 and parts[1] == "0200":

                cod_prod = _norm(parts[2] if len(parts) > 2 else None)    

                codigo_produto = cod_prod

                if empresa_regras:
                    for er in empresa_regras:
                        
                        regra = er.regra
                        
                        v_regra = regra.regra

                        v_regras = ValidarRegra(codigo_produto, v_regra)

                        if regra.tipo == 'prefixo':
                            codigo_produto = v_regras.validar_prefixo()

                        if regra.tipo == 'caractere':
                            codigo_produto = v_regras.validar_caractere()

                        if regra.tipo == 'sufixo':
                            codigo_produto = v_regras.validar_sufixo()

                    codigo_produto = v_regras.codigo_produto

                tipo_item_map = {
                    "01": "Mercadoria para revenda",
                    "02": "Matéria prima",
                    "03": "Produto em elaboração",
                    "04": "Produto acabado",
                    "05": "Subproduto",
                    "06": "Produto intermediário",
                    "07": "Material de uso e consumo",
                    "08": "Ativo imobilizado",
                    "09": "Serviço",
                }
                numero_item = parts[7] if len(parts) > 7 else None
                tipo_item = tipo_item_map.get(numero_item, "Outros")

                cest = parts[13] if len(parts) > 13 else None


                catalogo_produtos[codigo_produto or cod_prod] = {
                    "codigo_prod": codigo_produto or cod_prod,
                    "descricao_prod": _norm(parts[3] if len(parts) > 3 else None),
                    "unidade": _norm(parts[6] if len(parts) > 6 else None),
                    "tipo_item": tipo_item,
                    "ncm": _norm(parts[8] if len(parts) > 8 else None),
                    "cod_gen": _norm(parts[10] if len(parts) > 10 else None),
                    "cest": cest,
                    "status": "S/N",
                    "data_inicio_sped": data_inicio_sped_ok,
                    "data_fim_sped": data_fim_sped_ok,
                    "mes_referencia": mes_referencia,
                }
                cadastro_itens_sped.append(catalogo_produtos[codigo_produto].copy())

            # C100 -> Nota fiscal
            elif len(parts) > 1 and parts[1] == "C100":
                cod_part_c100 = parts[4] if len(parts) > 4 else None
                numero_nota_atual = _norm(parts[8] if len(parts) > 8 else None)

                tipo = {"0": "Entrada", "1": "Saida"}

                valor_frete = normalizador_decimal(
                    parts[17] if len(parts) > 17 else None
                )
                valor_seguro = normalizador_decimal(
                    parts[18] if len(parts) > 18 else None
                )
                despesa_acessoria = normalizador_decimal(
                    parts[19] if len(parts) > 19 else None
                )

                uf_map = {
                    "12": "AC",
                    "27": "AL",
                    "13": "AM",
                    "16": "AP",
                    "29": "BA",
                    "23": "CE",
                    "53": "DF",
                    "32": "ES",
                    "52": "GO",
                    "21": "MA",
                    "31": "MG",
                    "50": "MS",
                    "51": "MT",
                    "15": "PA",
                    "25": "PB",
                    "26": "PE",
                    "22": "PI",
                    "41": "PR",
                    "33": "RJ",
                    "24": "RN",
                    "43": "RS",
                    "11": "RO",
                    "14": "RR",
                    "42": "SC",
                    "28": "SE",
                    "35": "SP",
                    "17": "TO",
                }

                codigo_uf = _norm(parts[9][:2] if len(parts) > 9 else None)
                estado = uf_map.get(codigo_uf, "Sem informação")

                numero_tipo = parts[2] if len(parts) > 2 else None
                tipo_nota = tipo.get(numero_tipo, "Desconhecido")

                data_entrada_saida = parts[11] if len(parts) > 11 else None

                data_entrada_saida_ok = None

                if data_entrada_saida:
                    try:
                        data_entrada_saida_ok = datetime.strptime(
                            data_entrada_saida, "%d%m%Y"
                        ).date()
                    except Exception as e:
                        print(f"Erro ao converter data {e}")
                else:
                    data_entrada_saida = None

                nota_atual = {
                    "tipo": tipo_nota,
                    "numero_nota": numero_nota_atual,
                    "codigo_uf": estado,
                    "tipo_documento": parts[5] if len(parts) > 5 else None,
                    "serie_documento": parts[6] if len(parts) > 6 else None,
                    "chave_nota": _norm(parts[9] if len(parts) > 9 else None),
                    "status": "S/PRODUTO",
                    "data_entrada_saida": data_entrada_saida_ok,
                    "produtos": [],
                    "second_value_total": 0,
                    "produtos_da_nota": [],
                    "valor_frete": valor_frete,
                    "valor_seguro": valor_seguro,
                    "despesa_acessoria": despesa_acessoria,
                    "data_inicio_sped": data_inicio_sped_ok,
                    "data_fim_sped": data_fim_sped_ok,
                    "mes_referencia": mes_referencia,
                    "tipo_operacao": None,  # Será preenchido se for importação
                    "numero_documento": None,  # Número do documento de importação do C120
                }

                if cod_part_c100 and cod_part_c100 in participantes_map:
                    participantes_map[cod_part_c100]["notas"].append(nota_atual)

            elif len(parts) > 1 and parts[1] == "C110" and nota_atual:
                # Garante que a lista existe mesmo com vários C110
                if "informacoes_c110" not in nota_atual:
                    nota_atual["informacoes_c110"] = []
                cod_inf = _norm(parts[2] if len(parts) > 2 else None)
                if cod_inf:
                    nota_atual["informacoes_c110"].append(cod_inf)

            elif len(parts) > 1 and parts[1] == "C120" and nota_atual:
                # Processa C120 mesmo se houver vários C110 antes
                # Pega o número do documento (DI) do C120 - sempre captura se existir
                numero_documento = _norm(parts[3] if len(parts) > 3 else None)

                # Verifica se algum C110 tem 'IMPORT' para determinar tipo de operação
                informacoes_c110 = nota_atual.get("informacoes_c110", [])
                achou_import = any(
                    "IMPORT" in str(info).upper() for info in informacoes_c110
                )

                if achou_import:
                    nota_atual["tipo_operacao"] = "Importação"

                # Sempre captura o número do documento do C120 se existir
                if numero_documento:
                    nota_atual["numero_documento"] = numero_documento

            # C170 -> Produto da nota
            elif len(parts) > 1 and parts[1] == "C170" and nota_atual:
                cod_prod = _norm(parts[3] if len(parts) > 3 else None)

                codigo_produto = cod_prod

                if empresa_regras:
                    for er in empresa_regras:
                        
                        regra = er.regra

                        v_regra = regra.regra

                        v_regras_c170 = ValidarRegra(codigo_produto, v_regra)
                        
                        if regra.tipo == 'prefixo':
                            v_regras_c170.validar_prefixo()

                        if regra.tipo == 'caractere':
                            v_regras_c170.validar_caractere()

                        if regra.tipo == 'sufixo':
                            v_regras_c170.validar_sufixo()

                    codigo_produto = v_regras_c170.codigo_produto

                nota_atual["status"] = "C/PRODUTO"


                if codigo_produto or cod_prod in catalogo_produtos:
                    catalogo_produtos[codigo_produto or cod_prod]["status"] = "C/N"
                    produto_info = catalogo_produtos[codigo_produto or cod_prod].copy()
                else:
                    produto_info = {
                        "codigo_prod": codigo_produto or cod_prod,
                        "descricao_prod": _norm(parts[4] if len(parts) > 4 else None),
                        "unidade": _norm(parts[6] if len(parts) > 6 else None),
                        "ncm": _norm(parts[37] if len(parts) > 37 else None),
                        "aliquota_icms": _norm(parts[32] if len(parts) > 32 else None),
                        "cst": _norm(parts[10] if len(parts) > 10 else None),
                        "cfop": parts[11] if len(parts) > 11 else None,
                        "status": "S/CADASTRO",
                        # ✅ CRÍTICO: Garantir que produtos sem cadastro também tenham a data correta
                        "data_inicio_sped": data_inicio_sped_ok,
                        "data_fim_sped": data_fim_sped_ok,
                        "mes_referencia": mes_referencia,
                    }

                qtd = normalizador_decimal(
                    parts[5] if len(parts) > 5 else None
                )
                produto_info["quantidade"] = qtd

                # Valores originais
                valor_prod = normalizador_decimal(
                    parts[7] if len(parts) > 7 else None
                )
                valor_desconto = normalizador_decimal(
                    parts[8] if len(parts) > 8 else None
                )
                valor_st = normalizador_decimal(
                    parts[18] if len(parts) > 18 else None
                )
                valor_ipi = normalizador_decimal(
                    parts[24] if len(parts) > 24 else None
                )
                valor_icms = normalizador_decimal(
                    parts[15] if len(parts) > 15 else None
                )

                if valor_ipi and valor_st and valor_desconto:
                    valor_imposto_item = valor_ipi + valor_st - valor_desconto
                else:
                    valor_imposto_item = None
                second_value = valor_frete + valor_seguro + despesa_acessoria

                nota_atual["second_value_total"] += second_value

                if valor_imposto_item:
                    produto_info["valor_imposto"] = round(valor_imposto_item, 2)
                else:
                    produto_info["valor_imposto"] = valor_imposto_item

                nota_atual["produtos_da_nota"].append((produto_info, valor_prod))

                # Campos extras
                produto_info["valor_ipi"] = valor_ipi
                produto_info["valor_icms"] = valor_icms
                produto_info["valor_unitario"] = (
                    round(valor_prod / qtd, 2) if qtd else 0
                )
                produto_info["base_icms"] = _norm(
                    parts[13] if len(parts) > 13 else None
                )
                produto_info["aliquota_icms"] = _norm(
                    parts[14] if len(parts) > 14 else None
                )
                produto_info["cfop"] = parts[11] if len(parts) > 11 else None
                produto_info["cst"] = _norm(parts[10] if len(parts) > 10 else None)

        for participante in participantes:
            for nota in participante.get("notas", []):
                produtos = nota.get("produtos_da_nota", [])
                if not produtos:
                    continue

                nota["produtos"] = []

                valor_total_nota = normalizador_decimal(
                    nota.get("second_value_total", 0)
                )
                n = len(produtos)

                if n == 0:
                    continue

                valor_para_rateio = valor_total_nota / n
                # Se não há valor para rateio, apenas soma valor_prod + valor_imposto (por item)
                if valor_para_rateio == 0:
                    for prod_info, valor_prod in produtos:
                        prod_info["valor_rateado"] = 0
                        valor_prod_decimal = normalizador_decimal(
                            valor_prod
                        )
                        imposto = normalizador_decimal(
                            prod_info.get("valor_imposto", 0)
                        )
                        if valor_prod_decimal and imposto:
                            total_calculado = valor_prod_decimal + imposto
                        else:
                            total_calculado = None

                        if total_calculado:
                            prod_info["valor_total"] = round(total_calculado, 2)
                        else:
                            prod_info["valor_total"] = total_calculado

                        nota["produtos"].append(prod_info.copy())
                else:
                    # dividir igualmente o valor_para_rateio entre os itens
                    base_share = round(valor_para_rateio / n, 2)
                    acumulado = Decimal('0.0')
                    for i, (prod_info, valor_prod) in enumerate(produtos):
                        if i < n - 1:
                            valor_rateado = base_share
                            acumulado += valor_rateado
                        else:
                            valor_rateado = round(valor_para_rateio - acumulado, 2)

                        prod_info["valor_rateado"] = valor_rateado
                        valor_prod_decimal = normalizador_decimal(
                            valor_prod
                        )
                        imposto = normalizador_decimal(
                            prod_info.get("valor_imposto", 0)
                        )
                        if valor_prod_decimal and valor_rateado and imposto:
                            total_calculado = valor_prod_decimal + valor_rateado + imposto
                        else:
                            total_calculado = None

                        if total_calculado:
                            prod_info["valor_total"] = round(total_calculado, 2)
                        else:
                            prod_info["valor_total"] = total_calculado

                        nota["produtos"].append(prod_info.copy())

        return {
            "participantes": participantes,
            "cnpj_empresa": cnpj_empresa,
            "data_inicio_sped": data_inicio_sped_ok,
            "data_fim_sped": data_fim_sped_ok,
            "mes_referencia": mes_referencia,
            "cadastro_itens_sped": cadastro_itens_sped,
            'produto_sem_cadastro': produtos_sem_cadastro,
        }
