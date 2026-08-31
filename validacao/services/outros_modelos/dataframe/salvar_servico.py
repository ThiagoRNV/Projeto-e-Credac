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
                cod_part = item.get("cod_part")
                d100_id = item.get("d100_id")
                d190_id = item.get("d190_id")
                c500_id = item.get("c500_id")
                c590_id = item.get("c590_id")
                d500_id = item.get("d500_id")
                d590_id = item.get("d590_id")

                mes_sped = None
                ano_sped = None

                # Atualiza participante (nome / cnpj_cpf)
                if cod_part:
                    try:
                        participante = Participantes.objects.get(empresa_id=self.empresa_id, cod_part=cod_part)
                        dados_part_antigos = {
                            'nome': participante.nome if participante.nome else '',
                            'cnpj_cpf': participante.cnpj_cpf if participante.cnpj_cpf else '',
                        }
                        entidade_titular = 'D100' if d100_id else ('C500' if c500_id else 'D500')
                        list_campo = {'nome': 'Nome', 'cnpj_cpf': 'CNPJ/CPF'}
                        for campo in ["nome", "cnpj_cpf"]:
                            if campo not in item:
                                continue
                            valor_novo = item.get(campo)
                            valor_antigo = dados_part_antigos.get(campo)
                            if valor_antigo != valor_novo:
                                Historico.objects.create(
                                    usuario=user_obj,
                                    empresa=empresa_obj,
                                    nome_empresa=empresa_obj.razao_social,
                                    tela_modificada='movimentacao',
                                    tabela='participantes',
                                    entidade_pai=participante.nome,
                                    entidade_titular=entidade_titular,
                                    campo=list_campo.get(campo),
                                    valor_antigo=valor_antigo,
                                    valor_novo=valor_novo,
                                    mes_sped=mes_sped,
                                    ano_sped=ano_sped,
                                )
                                setattr(participante, campo, item.get(campo))
                                participante.save()
                    except Participantes.DoesNotExist:
                        pass
                    except Exception as e:
                        erros.append(f"Erro ao atualizar participante {cod_part}: {e}")

                # Atualiza D100
                if d100_id:
                    try:
                        d100 = RegistroTransporteD100.objects.get(id=d100_id, empresa_id=self.empresa_id)
                        if d100.data_inicio_sped:
                            ano_sped = str(d100.data_inicio_sped.year)
                            mes_sped = f"{d100.data_inicio_sped.month:02d}"
                        dados_d100_antigos = {
                            'tipo': 'Entrada' if d100.ind_oper == '0' else ('Saida' if d100.ind_oper == '1' else ''),
                            'num_doc': str(d100.num_doc) if d100.num_doc else '',
                            'chv_cte': d100.chv_cte if d100.chv_cte else '',
                            'ser': d100.ser if d100.ser else '',
                            'vl_doc': normalizador_decimal(d100.vl_doc if d100.vl_doc else 0),
                            'vl_serv': normalizador_decimal(d100.vl_serv if d100.vl_serv else 0),
                        }
                        list_para_conversao = ['vl_doc', 'vl_serv']
                        list_campo = {
                            'num_doc': 'Número do documento',
                            'chv_cte': 'Chave CT-e',
                            'ser': 'Série',
                            'vl_doc': 'Valor do documento',
                            'vl_serv': 'Valor do serviço',
                        }
                        for campo in ["num_doc", "chv_cte", "ser", "vl_doc", "vl_serv"]:
                            if campo not in item:
                                continue
                            valor_antigo = dados_d100_antigos.get(campo)
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
                                    tabela='registro_d100',
                                    entidade_pai=d100.cod_part.nome if d100.cod_part else '',
                                    entidade_titular='D100',
                                    campo=list_campo.get(campo),
                                    valor_antigo=valor_antigo,
                                    valor_novo=valor_novo,
                                    mes_sped=mes_sped,
                                    ano_sped=ano_sped,
                                )
                                if campo == 'num_doc' and str(item.get("num_doc")).strip():
                                    try:
                                        d100.num_doc = int(str(item.get("num_doc")).strip())
                                    except (TypeError, ValueError):
                                        pass
                                else:
                                    valor = normalizador_decimal(item.get(campo), max_digits=15) if campo in campos_decimais_d100 else item.get(campo)
                                    if valor is not None:
                                        setattr(d100, campo, valor)
                                d100.save()
                        itens_processados += 1
                    except RegistroTransporteD100.DoesNotExist:
                        erros.append(f"Registro D100 {d100_id} não encontrado")
                    except Exception as e:
                        erros.append(f"Erro ao atualizar D100 {d100_id}: {e}")

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
                                    entidade_pai=item.get('num_doc'),
                                    entidade_filho='D190',
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

                # Atualiza C500 (Energia)
                if c500_id:
                    try:
                        c500 = RegistroEnergiaC500.objects.get(id=c500_id, empresa_id=self.empresa_id)
                        if c500.data_inicio_sped:
                            ano_sped = str(c500.data_inicio_sped.year)
                            mes_sped = f"{c500.data_inicio_sped.month:02d}"
                        dados_c500_antigos = {
                            'tipo': 'Entrada' if c500.ind_oper == '0' else ('Saida' if c500.ind_oper == '1' else ''),
                            'num_doc': str(c500.num_doc) if c500.num_doc else '',
                            'chv_doce': c500.chv_doce if c500.chv_doce else '',
                            'ser': c500.ser if c500.ser else '',
                            'vl_doc': normalizador_decimal(c500.vl_doc if c500.vl_doc else 0),
                            'vl_forn': normalizador_decimal(c500.vl_forn if c500.vl_forn else 0),
                        }
                        list_para_conversao = ['vl_doc', 'vl_forn']
                        list_campo = {
                            'num_doc': 'Número do documento',
                            'chv_doce': 'Chave do documento',
                            'ser': 'Série',
                            'vl_doc': 'Valor do documento',
                            'vl_forn': 'Valor fornecido',
                        }
                        for campo in ["num_doc", "chv_doce", "ser", "vl_doc", "vl_forn"]:
                            if campo not in item:
                                continue
                            valor_antigo = dados_c500_antigos.get(campo)
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
                                    tabela='registro_c500',
                                    entidade_pai=c500.cod_part.nome if c500.cod_part else '',
                                    entidade_titular='C500',
                                    campo=list_campo.get(campo),
                                    valor_antigo=valor_antigo,
                                    valor_novo=valor_novo,
                                    mes_sped=mes_sped,
                                    ano_sped=ano_sped,
                                )
                                if campo == 'num_doc' and str(item.get("num_doc")).strip():
                                    try:
                                        c500.num_doc = int(str(item.get("num_doc")).strip())
                                    except (TypeError, ValueError):
                                        pass
                                else:
                                    valor = normalizador_decimal(item.get(campo), max_digits=15) if campo in campos_decimais_c500 else item.get(campo)
                                    if valor is not None:
                                        setattr(c500, campo, valor)
                                c500.save()
                        itens_processados += 1
                    except RegistroEnergiaC500.DoesNotExist:
                        erros.append(f"Registro C500 {c500_id} não encontrado")
                    except Exception as e:
                        erros.append(f"Erro ao atualizar C500 {c500_id}: {e}")

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
                                    entidade_pai=c590.registro_c500.cod_part.nome if c590.registro_c500 and c590.registro_c500.cod_part else '',
                                    entidade_titular='C590',
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

                # Atualiza D500 (Comunicação)
                if d500_id:
                    try:
                        d500 = RegistroComunicacaoD500.objects.select_related('cod_part').get(id=d500_id, empresa_id=self.empresa_id)
                        if d500.data_inicio_sped:
                            ano_sped = str(d500.data_inicio_sped.year)
                            mes_sped = f"{d500.data_inicio_sped.month:02d}"
                        dados_d500_antigos = {
                            'tipo': 'Entrada' if d500.ind_oper == '0' else ('Saida' if d500.ind_oper == '1' else ''),
                            'num_doc': str(d500.num_doc) if d500.num_doc else '',
                            'ser': d500.ser if d500.ser else '',
                            'vl_doc': normalizador_decimal(d500.vl_doc if d500.vl_doc else 0),
                            'vl_serv': normalizador_decimal(d500.vl_serv if d500.vl_serv else 0),
                        }
                        list_para_conversao = ['vl_doc', 'vl_serv']
                        list_campo = {
                            'num_doc': 'Número do documento',
                            'ser': 'Série',
                            'vl_doc': 'Valor do documento',
                            'vl_serv': 'Valor do serviço',
                        }
                        for campo in ["num_doc", "ser", "vl_doc", "vl_serv"]:
                            if campo not in item:
                                continue
                            valor_antigo = dados_d500_antigos.get(campo)
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
                                    tabela='registro_d500',
                                    entidade_pai=item.get('nome') or (d500.cod_part.nome if d500.cod_part else ''),
                                    entidade_titular='D500',
                                    campo=list_campo.get(campo),
                                    valor_antigo=valor_antigo,
                                    valor_novo=valor_novo,
                                    mes_sped=mes_sped,
                                    ano_sped=ano_sped,
                                )
                                if campo == 'num_doc' and str(item.get("num_doc")).strip():
                                    try:
                                        d500.num_doc = int(str(item.get("num_doc")).strip())
                                    except (TypeError, ValueError):
                                        pass
                                else:
                                    valor = normalizador_decimal(item.get(campo), max_digits=15) if campo in campos_decimais_d500 else item.get(campo)
                                    if valor is not None:
                                        setattr(d500, campo, valor)
                                d500.save()
                        itens_processados += 1
                    except RegistroComunicacaoD500.DoesNotExist:
                        erros.append(f"Registro D500 {d500_id} não encontrado")
                    except Exception as e:
                        erros.append(f"Erro ao atualizar D500 {d500_id}: {e}")

                # Atualiza D590 (Comunicação)
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
                                    entidade_pai=nome_part,
                                    entidade_titular='D590',
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
