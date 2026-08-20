from validacao.models.participantes.participantes import Participantes
from validacao.models.mercadorias_nfe.notas import Notas_participantes
from validacao.models.mercadorias_nfe.produtos import Produtos_notas
from historico.models import Historico
from django.contrib.auth.models import User
from validacao.utils.normalizadores import normalizador_decimal
import json
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

# Exceptions simples para erros específicos
class ErrorSave(Exception): pass
class JsonInvalid(Exception): pass
class ErrorJson(Exception): pass

class SalvarEdicaoService:
    def __init__(self, items, empresa_id, user_id):
        self.items = items
        self.empresa_id = empresa_id
        self.usuario = user_id


    def process_salvar(self):
        user_obj = User.objects.get(id=self.usuario)
        try:
            if not self.empresa_id:
                logger.error('ID da empresa não recebido')
                raise ErrorSave()
            if not self.items:
                logger.error('Nenhum item foi recebido para salvar')
                raise ErrorSave()

            for item in self.items:

                cod_part = item.get("cod_part")
                data_inicio_sped = item.get("data_inicio_sped")
                mes_sped = None
                ano_sped = None
                if data_inicio_sped and isinstance(data_inicio_sped, str) and len(data_inicio_sped) >= 10:
                    try:
                        ano_sped = data_inicio_sped[:4]
                        mes_sped = data_inicio_sped[5:7]
                    except Exception:
                        mes_sped = None
                        ano_sped = None
           
                
                notas_qs = None
                # Atualiza notas
                part_obj = Participantes.objects.filter(empresa_id=self.empresa_id, data_inicio_sped=data_inicio_sped, cod_part=cod_part).first()
                try:
                    if self.empresa_id and data_inicio_sped:
                        notas_qs = Notas_participantes.objects.filter(empresa_id=self.empresa_id, data_inicio_sped=data_inicio_sped)
                    if cod_part:
                        notas_qs = notas_qs.filter(part_titular__cod_part=cod_part)
                    chave_nota_old = item.get("chave_nota_old")
                    numero_nota_old = item.get("numero_nota_old")
                    if chave_nota_old and chave_nota_old != '--':
                        notas_qs = notas_qs.filter(chave_nota=chave_nota_old)
                    elif numero_nota_old and numero_nota_old != 'S/N':
                        notas_qs = notas_qs.filter(numero_nota=numero_nota_old)
                    
                    dados_notas_antigos = {}
                    for nota in notas_qs:
                        dados_notas_antigos = {
                            'tipo': nota.tipo if nota.tipo else '',
                            'codigo_uf': nota.codigo_uf if nota.codigo_uf else '',
                            'chave_nota': nota.chave_nota if nota.chave_nota else '',
                            'numero_nota': nota.numero_nota if nota.numero_nota else '',
                            'tipo_operacao': nota.tipo_operacao if nota.tipo_operacao else '',
                            'numero_documento': nota.numero_documento if nota.numero_documento else '',
                        }
                        
                   
                        for campo in ["tipo", "codigo_uf", "chave_nota", "numero_nota", "tipo_operacao", "numero_documento"]:
                            valor_novo = item.get(campo)
                            valor_antigo = dados_notas_antigos.get(campo) 

                            list_campo = {
                                'tipo': 'Tipo', 
                                'codigo_uf': 'Código UF',
                                'chave_nota': 'Chave nota',
                                'numero_nota': 'Número nota',
                                'tipo_operacao': 'Tipo de operação',
                                'numero_documento': 'Número do documento'
                            }
                            if valor_antigo != valor_novo:
                                Historico.objects.create(
                                    usuario=user_obj,
                                    tela_modificada='movimentacao',
                                    tabela='notas_participantes', 
                                    entidade_pai=part_obj.nome,
                                    entidade_titular=nota.numero_nota,
                                    campo=list_campo.get(campo), 
                                    valor_antigo=valor_antigo,
                                    valor_novo=valor_novo,
                                    mes_sped=mes_sped,
                                    ano_sped=ano_sped,
                                )
                                setattr(nota, campo, item.get(campo))
                                nota.save()
                except Exception as e:
                    logger.error('Erro ao atualizar nota')
                    raise ErrorSave() from e

                # Atualiza produtos
                try:
                    nota = item.get('numero_nota_old')
                    produtos_qs = Produtos_notas.objects.filter(
                        empresa_id=self.empresa_id,
                        nota_titular__in=notas_qs,
                        data_inicio_sped=data_inicio_sped
                    )
                    codigo_prod_old = item.get("codigo_prod_old")
                    if codigo_prod_old:
                        produtos_qs = produtos_qs.filter(codigo_prod=codigo_prod_old)
                    campos_decimal = {"quantidade_prod","valor_unitario","base_icms","valor_icms","aliquota_icms","valor_total","valor_ipi"}
                    fields = [
                        "cfop_prod", "codigo_prod", "descricao_prod", "ncm", "quantidade_prod",
                        "valor_unitario", "base_icms", "valor_icms", "aliquota_icms", "valor_total",
                        "cst", "cest", "valor_ipi"
                    ]
                    dados_antigos_prod = {}
                    for prod in produtos_qs:
                        dados_antigos_prod = {
                            'cfop_prod': prod.cfop_prod if prod.cfop_prod else '',
                            'codigo_prod': prod.codigo_prod if prod.codigo_prod else '',
                            'descricao_prod': prod.descricao_prod if prod.descricao_prod else '',
                            'ncm': prod.ncm if prod.ncm else '',
                            'quantidade_prod': normalizador_decimal(prod.quantidade_prod if prod.quantidade_prod else 0),
                            'valor_unitario': normalizador_decimal(prod.valor_unitario if prod.valor_unitario else 0), 
                            'base_icms': normalizador_decimal(prod.base_icms if prod.base_icms else 0),
                            'valor_icms': normalizador_decimal(prod.valor_icms if prod.valor_icms else 0),
                            'aliquota_icms': normalizador_decimal(prod.aliquota_icms if prod.aliquota_icms else 0),
                            'valor_total': normalizador_decimal(prod.valor_total if prod.valor_total else 0),
                            'cst': prod.cst if prod.cst else '',
                            'cest': prod.cest if prod.cest else '',
                            'valor_ipi': normalizador_decimal(prod.valor_ipi if prod.valor_ipi else 0),
                        }
                        list_para_conversao = [
                            'quantidade_prod', 'valor_unitario', 'base_icms',
                            'valor_icms', 'valor_icms', 'aliquota_icms', 'valor_total', 'valor_ipi'
                        ]
                        valor_novo = None
                        for campo in fields:
                            valor_antigo = dados_antigos_prod.get(campo)
                            if campo in list_para_conversao:
                                valor_novo = Decimal(item.get(campo))
                            else:
                                valor_novo = item.get(campo)
                            list_campo = {
                                "cfop_prod": 'CFOP', 
                                "codigo_prod": 'Código Produto', 
                                "descricao_prod": 'Descrição Produto', 
                                "ncm": 'NCM',
                                "quantidade_prod": 'Quantidade',
                                "valor_unitario": 'Valor Unitário', 
                                "base_icms": 'Base ICMS', 
                                "valor_icms": 'Valor ICMS', 
                                "aliquota_icms": 'Alíquota ICMS', 
                                "valor_total": 'Valor Total',
                                "cst": 'CST', 
                                "cest": 'CEST', 
                                "valor_ipi": 'Valor IPI'
                            }
                            
                            if valor_antigo != valor_novo:
                                    Historico.objects.create(
                                        usuario=user_obj,
                                        tela_modificada='movimentacao',
                                        tabela='notas_participantes', 
                                        entidade_pai=part_obj.nome,
                                        entidade_titular=nota,
                                        prod_titular=prod.codigo_prod,
                                        campo=list_campo.get(campo), 
                                        valor_antigo=valor_antigo,
                                        valor_novo=valor_novo,
                                        mes_sped=mes_sped,
                                        ano_sped=ano_sped,
                                    )
                                    valor = normalizador_decimal(item.get(campo)) if campo in campos_decimal else item.get(campo)
                                    setattr(prod, campo, valor)
                                    prod.save()
                except Exception as e:
                    logger.error('Erro ao atualizar item')
                    raise ErrorSave() from e

            return {'success': True}

        except json.JSONDecodeError:
            raise JsonInvalid()
        except Exception:
            logger.exception('Erro ao salvar')
            raise ErrorJson()
