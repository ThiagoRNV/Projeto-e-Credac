from validacao.models.participantes.participantes import Participantes
from validacao.models.outros_modelos.registrod100 import RegistroTransporteD100
from validacao.models.outros_modelos.registrod190 import RegistroTransporteD190
from validacao.models.outros_modelos.registroc500 import RegistroEnergiaC500
from validacao.models.outros_modelos.registroc590 import RegistroEnergiaC590
from validacao.models.outros_modelos.registrod500 import RegistroComunicacaoD500
from validacao.models.outros_modelos.registrod590 import RegistroComunicacaoD590
from validacao.utils.normalizadores import normalizador_decimal
from historico.models import Historico
from django.contrib.auth.models import User
from decimal import Decimal
from cadastro.models.empresa import Empresa
import json

class SalvarDadosServico:
    def __init__(self, items, empresa_id, user_id) -> None:
        self.items = items
        self.empresa_id = empresa_id
        self.usuario = user_id

    def salvar_services(self):
        print(self.items)
        user_obj = User.objects.get(id=self.usuario)
        empresa_obj = Empresa.objects.get(id=self.empresa_id)

        erros = [] 
        try:
            if not self.empresa_id:
                return {'empresa_id': True}

            if not self.items:
                return {'items': True}

            itens_processados = 0

            campos_decimais_d100 = {"vl_doc", "vl_serv"}
            campos_decimais_d190 = {"aliq_icms", "vl_opr", "vl_bc_icms", "vl_icms", "vl_red_bc"}
            campos_decimais_c500 = {"vl_doc", "vl_forn"}
            campos_decimais_d500 = {"vl_doc", "vl_serv"}
            campos_decimais_analitico_500 = {"aliq_icms", "vl_opr", "vl_bc_icms", "vl_icms", "vl_bc_icms_st", "vl_icms_st", "vl_red_bc"}

            for item in self.items:
                d190_id = item.get("d190_id")
                c590_id = item.get("c590_id")
                d590_id = item.get("d590_id")

                mes_sped = None
                ano_sped = None

                # Atualiza D190
                if d190_id:
                    try:
                        d190 = RegistroTransporteD190.objects.get(id=d190_id, empresa_id=self.empresa_id)
                        if d190.data_inicio_sped:
                            ano_sped = str(d190.data_inicio_sped.year)
                            mes_sped = f"{d190.data_inicio_sped.month:02d}"
                        dados_d190_antigos = {
                            'cfop': d190.cfop if d190.cfop else '',
                            'cst_icms': d190.cst_icms if d190.cst_icms else '',
                            'cod_obs': d190.cod_obs if d190.cod_obs else '',
                            'aliq_icms': normalizador_decimal(d190.aliq_icms if d190.aliq_icms else 0),
                            'vl_opr': normalizador_decimal(d190.vl_opr if d190.vl_opr else 0),
                            'vl_bc_icms': normalizador_decimal(d190.vl_bc_icms if d190.vl_bc_icms else 0),
                            'vl_icms': normalizador_decimal(d190.vl_icms if d190.vl_icms else 0),
                            'vl_red_bc': normalizador_decimal(d190.vl_red_bc if d190.vl_red_bc else 0),
                        }
                        list_para_conversao = ['aliq_icms', 'vl_opr', 'vl_bc_icms', 'vl_icms', 'vl_red_bc']
                        list_campo = {
                            'cfop': 'CFOP',
                            'cst_icms': 'CST',
                            'aliq_icms': 'Alíquota ICMS',
                            'vl_opr': 'Valor da operação',
                            'vl_bc_icms': 'Base ICMS',
                            'vl_icms': 'Valor ICMS',
                            'vl_red_bc': 'Redução BC',
                            'cod_obs': 'Código observação',
                        }
                        for campo in ["cfop", "cst_icms", "cod_obs", "aliq_icms", "vl_opr", "vl_bc_icms", "vl_icms", "vl_red_bc"]:
                            if campo not in item:
                                continue
                            valor_antigo = dados_d190_antigos.get(campo)
                            if campo in list_para_conversao:
                                valor_novo = Decimal(item.get(campo))
                            else:
                                valor_novo = item.get(campo)
                            if valor_antigo != valor_novo:
                                Historico.objects.create(
                                    usuario=user_obj,
                                    empresa=empresa_obj,
                                    nome_empresa=empresa_obj.razao_social,
                                    tela_modificada='movimentacao',
                                    tabela='registro_d190',
                                    part_titular=d190.registro_d100.cod_part.nome if d190.registro_d100 and d190.registro_d100.cod_part else '',
                                    documento=d190.registro_d100.num_doc if d190.registro_d100 and d190.registro_d100.num_doc else '',
                                    serie=d190.registro_d100.ser if d190.registro_d100 and d190.registro_d100.ser else '',
                                    reg_titular='D190',
                                    campo=list_campo.get(campo),
                                    valor_antigo=valor_antigo,
                                    valor_novo=valor_novo,
                                    mes_sped=mes_sped,
                                    ano_sped=ano_sped,
                                )
                                valor = normalizador_decimal(item.get(campo), max_digits=15) if campo in campos_decimais_d190 else item.get(campo)
                                if valor is not None:
                                    setattr(d190, campo, valor)
                                    d190.save()
                        itens_processados += 1
                    except RegistroTransporteD190.DoesNotExist:
                        erros.append(f"Registro D190 {d190_id} não encontrado")
                    except Exception as e:
                        erros.append(f"Erro ao atualizar D190 {d190_id}: {e}")

                # Atualiza C590 (Energia)
                if c590_id:
                    try:
                        c590 = RegistroEnergiaC590.objects.get(id=c590_id, empresa_id=self.empresa_id)
                        if c590.data_inicio_sped:
                            ano_sped = str(c590.data_inicio_sped.year)
                            mes_sped = f"{c590.data_inicio_sped.month:02d}"
                        dados_c590_antigos = {
                            'cfop': c590.cfop if c590.cfop else '',
                            'cst_icms': c590.cst_icms if c590.cst_icms else '',
                            'cod_obs': c590.cod_obs if c590.cod_obs else '',
                            'aliq_icms': normalizador_decimal(c590.aliq_icms if c590.aliq_icms else 0),
                            'vl_opr': normalizador_decimal(c590.vl_opr if c590.vl_opr else 0),
                            'vl_bc_icms': normalizador_decimal(c590.vl_bc_icms if c590.vl_bc_icms else 0),
                            'vl_icms': normalizador_decimal(c590.vl_icms if c590.vl_icms else 0),
                            'vl_bc_icms_st': normalizador_decimal(c590.vl_bc_icms_st if c590.vl_bc_icms_st else 0),
                            'vl_icms_st': normalizador_decimal(c590.vl_icms_st if c590.vl_icms_st else 0),
                            'vl_red_bc': normalizador_decimal(c590.vl_red_bc if c590.vl_red_bc else 0),
                        }
                        list_para_conversao = ['aliq_icms', 'vl_opr', 'vl_bc_icms', 'vl_icms', 'vl_bc_icms_st', 'vl_icms_st', 'vl_red_bc']
                        list_campo = {
                            'cfop': 'CFOP',
                            'cst_icms': 'CST',
                            'aliq_icms': 'Alíquota ICMS',
                            'vl_opr': 'Valor da operação',
                            'vl_bc_icms': 'Base ICMS',
                            'vl_icms': 'Valor ICMS',
                            'vl_bc_icms_st': 'Base ICMS-ST',
                            'vl_icms_st': 'Valor ICMS-ST',
                            'vl_red_bc': 'Redução BC',
                            'cod_obs': 'Código observação',
                        }
                        for campo in ["cfop", "cst_icms", "cod_obs", "aliq_icms", "vl_opr", "vl_bc_icms", "vl_icms", "vl_bc_icms_st", "vl_icms_st", "vl_red_bc"]:
                            if campo not in item:
                                continue
                            valor_antigo = dados_c590_antigos.get(campo)
                            if campo in list_para_conversao:
                                valor_novo = Decimal(item.get(campo))
                            else:
                                valor_novo = item.get(campo)
                            if valor_antigo != valor_novo:
                                Historico.objects.create(
                                    usuario=user_obj,
                                    empresa=empresa_obj,
                                    nome_empresa=empresa_obj.razao_social,
                                    tela_modificada='movimentacao',
                                    tabela='registro_c590',
                                    part_titular=c590.registro_c500.cod_part.nome if c590.registro_c500 and c590.registro_c500.cod_part else '',
                                    documento=c590.registro_c500.num_doc if c590.registro_c500 and c590.registro_c500.num_doc else '',
                                    serie=c590.registro_c500.ser if c590.registro_c500 and c590.registro_c500.ser else '',
                                    reg_titular='C590',
                                    campo=list_campo.get(campo),
                                    valor_antigo=valor_antigo,
                                    valor_novo=valor_novo,
                                    mes_sped=mes_sped,
                                    ano_sped=ano_sped,
                                )
                                valor = normalizador_decimal(item.get(campo), max_digits=15) if campo in campos_decimais_analitico_500 else item.get(campo)
                                if valor is not None:
                                    setattr(c590, campo, valor)
                                    c590.save()
                        itens_processados += 1
                    except RegistroEnergiaC590.DoesNotExist:
                        erros.append(f"Registro C590 {c590_id} não encontrado")
                    except Exception as e:
                        erros.append(f"Erro ao atualizar C590 {c590_id}: {e}")

                if d590_id:
                    try:
                        d590 = RegistroComunicacaoD590.objects.select_related('registro_d500__cod_part').get(id=d590_id, empresa_id=self.empresa_id)
                        if d590.data_inicio_sped:
                            ano_sped = str(d590.data_inicio_sped.year)
                            mes_sped = f"{d590.data_inicio_sped.month:02d}"
                        dados_d590_antigos = {
                            'cfop': d590.cfop if d590.cfop else '',
                            'cst_icms': d590.cst_icms if d590.cst_icms else '',
                            'cod_obs': d590.cod_obs if d590.cod_obs else '',
                            'aliq_icms': normalizador_decimal(d590.aliq_icms if d590.aliq_icms else 0),
                            'vl_opr': normalizador_decimal(d590.vl_opr if d590.vl_opr else 0),
                            'vl_bc_icms': normalizador_decimal(d590.vl_bc_icms if d590.vl_bc_icms else 0),
                            'vl_icms': normalizador_decimal(d590.vl_icms if d590.vl_icms else 0),
                            'vl_bc_icms_st': normalizador_decimal(d590.vl_bc_icms_st if d590.vl_bc_icms_st else 0),
                            'vl_icms_st': normalizador_decimal(d590.vl_icms_st if d590.vl_icms_st else 0),
                            'vl_red_bc': normalizador_decimal(d590.vl_red_bc if d590.vl_red_bc else 0),
                        }
                        list_para_conversao = ['aliq_icms', 'vl_opr', 'vl_bc_icms', 'vl_icms', 'vl_bc_icms_st', 'vl_icms_st', 'vl_red_bc']
                        list_campo = {
                            'cfop': 'CFOP',
                            'cst_icms': 'CST',
                            'aliq_icms': 'Alíquota ICMS',
                            'vl_opr': 'Valor da operação',
                            'vl_bc_icms': 'Base ICMS',
                            'vl_icms': 'Valor ICMS',
                            'vl_bc_icms_st': 'Base ICMS-ST',
                            'vl_icms_st': 'Valor ICMS-ST',
                            'vl_red_bc': 'Redução BC',
                            'cod_obs': 'Código observação',
                        }
                        nome_part = item.get('nome') or ''
                        if not nome_part and d590.registro_d500 and d590.registro_d500.cod_part:
                            nome_part = d590.registro_d500.cod_part.nome or ''
                        if not nome_part:
                            for it in self.items:
                                if str(it.get('d500_id')) == str(d590.registro_d500_id):
                                    nome_part = it.get('nome') or ''
                                    break
                        for campo in ["cfop", "cst_icms", "cod_obs", "aliq_icms", "vl_opr", "vl_bc_icms", "vl_icms", "vl_bc_icms_st", "vl_icms_st", "vl_red_bc"]:
                            if campo not in item:
                                continue
                            valor_antigo = dados_d590_antigos.get(campo)
                            if campo in list_para_conversao:
                                valor_novo = Decimal(item.get(campo))
                            else:
                                valor_novo = item.get(campo)
                            if valor_antigo != valor_novo:
                                Historico.objects.create(
                                    usuario=user_obj,
                                    empresa=empresa_obj,
                                    nome_empresa=empresa_obj.razao_social,
                                    tela_modificada='movimentacao',
                                    tabela='registro_d590',
                                    part_titular=nome_part,
                                    documento=d590.registro_d500.num_doc if d590.registro_d500 and d590.registro_d500.num_doc else '',
                                    serie=d590.registro_d500.ser if d590.registro_d500 and d590.registro_d500.ser else '',
                                    reg_titular='D590',
                                    campo=list_campo.get(campo),
                                    valor_antigo=valor_antigo,
                                    valor_novo=valor_novo,
                                    mes_sped=mes_sped,
                                    ano_sped=ano_sped,
                                )
                                valor = normalizador_decimal(item.get(campo), max_digits=15) if campo in campos_decimais_analitico_500 else item.get(campo)
                                if valor is not None:
                                    setattr(d590, campo, valor)
                                    d590.save()
                        itens_processados += 1
                    except RegistroComunicacaoD590.DoesNotExist:
                        erros.append(f"Registro D590 {d590_id} não encontrado")
                    except Exception as e:
                        erros.append(f"Erro ao atualizar D590 {d590_id}: {e}")

            if erros:
                return {'erros': erros, 'itens_processados': itens_processados}

            return {'success': True, 'itens_processados': itens_processados}
        except json.JSONDecodeError:
            return {'json_invalid': True}
        except Exception:
            import traceback
            traceback.print_exc()
            return {'error': True, 'erros': erros}
