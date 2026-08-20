from datetime import datetime
from django.db.models import Q

from metodo_rateio.utils.normalizadores import Normalizadores
from metodo_rateio.models.sped import (
    ItensProduzidos230,
    InsumosUsados235,
    ItensProduzidos250,
    InsumosUsados255,
    analise_k23x,
    analise_k25x,
)
from metodo_rateio.utils.extract_blocok import BlocoKProcessesServices
from cadastro.models.empresa import Empresa
from cadastro.models.produtos import Cadastro_itens_sped


class ProcessamentoServices:

    def __init__(self, sped_file, btns):
        self.sped_file = sped_file
        self.btns = btns

    def processar_bloco_k(self):
        try:
            match self.btns:
                case 'k230_k235':
                    return self._processar_k230_k235()
                case 'k250_k255':
                    return self._processar_k250_k255()
                case 'ambos':
                    return self._processar_ambos()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            return {'erro_inesperado': str(ex)}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalizar_ano(ano):
        if ano is None or ano == '':
            return str(datetime.now().year)
        return str(ano)

    def _carregar_sped(self):
        processor = BlocoKProcessesServices(self.sped_file)
        if not processor.load_sped_file():
            return None, {'failed_load': False}
        return processor, None

    def _obter_empresa(self, cnpj):
        if not cnpj:
            return None, {'cnpj_empresa': False}
        empresa = Empresa.objects.filter(cnpj=cnpj).first()
        if not empresa:
            return None, {'empresa_obj': False}
        return empresa, None

    def _salvar_cadastro_itens(self, empresa, itens):
        for item in itens or []:
            if not isinstance(item, dict):
                continue
            try:
                Cadastro_itens_sped.objects.get_or_create(
                    empresa=empresa,
                    codigo_prod=item.get('codigo_prod'),
                    defaults={
                        'data_inicio_sped': item.get('data_inicio_sped'),
                        'data_fim_sped': item.get('data_fim_sped'),
                        'descricao_prod': item.get('descricao_prod'),
                        'unidade': item.get('unidade'),
                        'tipo_item': item.get('tipo_item'),
                        'ncm': item.get('ncm'),
                        'cest': item.get('cest'),
                        'genero': item.get('cod_gen'),
                        'mes_ref': item.get('mes_referencia'),
                    },
                )
            except Exception as e:
                return {'cadastro': False, 'erro': str(e)}
        return None

    def _obter_analise_k23x(self, empresa):
        analise, _ = analise_k23x.objects.get_or_create(
            empresa=empresa,
            defaults={
                'data_inicio': datetime.now().date(),
                'ano_sped': [],
            },
        )
        return analise

    @staticmethod
    def _anos_como_lista(ano_sped):
        if ano_sped is None or ano_sped == '':
            return []
        if isinstance(ano_sped, list):
            return [str(a) for a in ano_sped]
        return [str(ano_sped)]

    def _ano_ja_processado(self, analise, ano):
        return str(ano) in self._anos_como_lista(analise.ano_sped)

    def _registrar_ano_analise_k23x(self, empresa, ano):
        """get_or_create por empresa; adiciona o ano ao JSONField se ainda não existir."""
        analise = self._obter_analise_k23x(empresa)
        if self._ano_ja_processado(analise, ano):
            return analise, True

        anos = self._anos_como_lista(analise.ano_sped)
        anos.append(str(ano))
        analise.ano_sped = anos
        analise.data_inicio = datetime.now().date()
        analise.save(update_fields=['ano_sped', 'data_inicio'])
        return analise, False

    def _salvar_k230_k235(self, empresa, k230_itens):
        if not k230_itens:
            return

        chaves = []
        for item in k230_itens:
            if not isinstance(item, dict):
                continue
            chaves.append((
                self._normalizar_ano(item.get('ano_sped')),
                item.get('cod_ordem_prod', ''),
                item.get('codigo_prod', ''),
            ))

        existentes = {}
        if chaves:
            q = Q()
            for ano, cod_ordem, codigo_item in chaves:
                q |= Q(
                    empresa=empresa,
                    ano_sped=ano,
                    cod_ordem_prod=cod_ordem,
                    codigo_item=codigo_item,
                )
            for obj in ItensProduzidos230.objects.filter(q):
                existentes[(obj.ano_sped, obj.cod_ordem_prod, obj.codigo_item)] = obj

        para_criar, para_atualizar = [], []
        criados_chaves = set()
        k230s_salvos = {}

        for item in k230_itens:
            if not isinstance(item, dict):
                continue
            try:
                ano = self._normalizar_ano(item.get('ano_sped'))
                cod_ordem = item.get('cod_ordem_prod', '')
                codigo_item = item.get('codigo_prod', '')
                qtd = item.get('qtd_producao_acabada')
                qtd = str(qtd) if qtd is not None else '0'
                chave = (ano, cod_ordem, codigo_item)

                existente = existentes.get(chave)
                if existente:
                    existente.data_inicial_op = item.get('data_inicial_op') or existente.data_inicial_op
                    existente.data_final_op = item.get('data_final_op') or existente.data_final_op
                    existente.qtd_producao_acabada = qtd
                    existente.ano_sped = ano
                    if item.get('mes_referencia_k230'):
                        existente.mes_referencia_k230 = item.get('mes_referencia_k230')
                    if existente not in para_atualizar:
                        para_atualizar.append(existente)
                    k230s_salvos[chave] = existente
                elif chave not in criados_chaves and chave not in k230s_salvos:
                    criados_chaves.add(chave)
                    novo = ItensProduzidos230(
                        empresa=empresa,
                        registro=item.get('registro'),
                        ano_sped=ano,
                        data_inicial_op=item.get('data_inicial_op'),
                        data_final_op=item.get('data_final_op'),
                        cod_ordem_prod=cod_ordem,
                        codigo_item=codigo_item,
                        mes_referencia_k230=item.get('mes_referencia_k230'),
                        qtd_producao_acabada=qtd,
                    )
                    para_criar.append(novo)
                    k230s_salvos[chave] = novo
            except Exception as e:
                print(f"Erro ao preparar K230 do arquivo {self.sped_file.name}: {e}")

        if para_criar:
            for novo in ItensProduzidos230.objects.bulk_create(para_criar, batch_size=500):
                chave = (novo.ano_sped, novo.cod_ordem_prod, novo.codigo_item)
                k230s_salvos[chave] = novo

        if para_atualizar:
            ItensProduzidos230.objects.bulk_update(
                para_atualizar,
                ['data_inicial_op', 'data_final_op', 'qtd_producao_acabada', 'ano_sped', 'mes_referencia_k230'],
                batch_size=500,
            )

        k235s_para_criar = []
        for item in k230_itens:
            if not isinstance(item, dict):
                continue
            try:
                chave = (
                    self._normalizar_ano(item.get('ano_sped')),
                    item.get('cod_ordem_prod', ''),
                    item.get('codigo_prod', ''),
                )
                item_produzido = k230s_salvos.get(chave)
                if not item_produzido:
                    continue

                for k235 in item.get('insumos', []):
                    try:
                        k235s_para_criar.append(InsumosUsados235(
                            item_produzido=item_produzido,
                            empresa=empresa,
                            registro=k235.get('registro'),
                            data_saida_estoque=k235.get('data_final_op'),
                            quantidade=Normalizadores.normalizador_decimal(k235.get('quantidade')),
                            codigo_insumo=k235.get('cod_insumo'),
                            situacao=k235.get('situacao'),
                            verificacao_codigo=k235.get('verificacao_codigo'),
                            ano_sped=self._normalizar_ano(k235.get('ano_sped') or item.get('ano_sped')),
                            mes_referencia_k235=k235.get('mes_referencia_k235'),
                        ))
                    except Exception as e:
                        print(f"Erro ao preparar K235 do arquivo {self.sped_file.name}: {e}")
            except Exception as e:
                print(f"Erro ao processar K235s do arquivo {self.sped_file.name}: {e}")

        if not k235s_para_criar:
            return

        item_ids = {k.item_produzido.id for k in k235s_para_criar if k.item_produzido and k.item_produzido.id}
        if item_ids:
            existentes_set = {
                (k.item_produzido_id, k.empresa_id, k.registro, k.codigo_insumo)
                for k in InsumosUsados235.objects.filter(
                    item_produzido_id__in=item_ids,
                    empresa=empresa,
                )
            }
            novos = [
                k for k in k235s_para_criar
                if (k.item_produzido.id, k.empresa.id, k.registro, k.codigo_insumo) not in existentes_set
            ]
        else:
            novos = k235s_para_criar

        if novos:
            InsumosUsados235.objects.bulk_create(novos, batch_size=500, ignore_conflicts=True)

    def _salvar_k250_k255(self, empresa, k250_itens, ano_sped):
        for item in k250_itens or []:
            if not isinstance(item, dict):
                continue
            try:
                data_const = item.get('data_const')
                cod_item = item.get('codigo_item') or item.get('cod_item') or ''
                if not data_const or not cod_item:
                    continue

                ano_item = self._normalizar_ano(item.get('ano_sped') or ano_sped)
                k250_obj = ItensProduzidos250.objects.create(
                    empresa=empresa,
                    ano_sped=ano_item,
                    registro=item.get('registro'),
                    data_prod=data_const,
                    cod_item=cod_item,
                    quantidade=Normalizadores.normalizador_decimal(item.get('quantidade')) if item.get('quantidade') else None,
                    mes_sped=item.get('mes_const'),
                )

                for k255 in item.get('insumos', []):
                    InsumosUsados255.objects.create(
                        empresa=empresa,
                        registro=k255.get('registro'),
                        ano_sped=self._normalizar_ano(k255.get('ano_sped') or ano_item),
                        data_consumo_insumo=k255.get('data_const') or k255.get('data_consumo_insumo'),
                        cod_item=k255.get('codigo_prod'),
                        quantidade=Normalizadores.normalizador_decimal(k255.get('quantidade')),
                        qtd_perda=k255.get('qtd_perda'),
                        mes_sped=k255.get('mes_consumo_insumo'),
                        k250_titular=k250_obj,
                    )
            except Exception as e:
                print(f"Erro ao preparar K250 do arquivo {self.sped_file.name}: {e}")

    # ------------------------------------------------------------------
    # Fluxos
    # ------------------------------------------------------------------

    def _processar_k230_k235(self):
        try:
            processor, erro = self._carregar_sped()
            if erro:
                return erro

            dados = processor.extract_values_bloco_k_230_235()
            if not dados:
                return {'dados_sped': False}

            empresa, erro = self._obter_empresa(dados.get('cnpj_empresa'))
            if erro:
                return erro

            ano = self._normalizar_ano(dados.get('ano_sped'))
            _, ja_processado = self._registrar_ano_analise_k23x(empresa, ano)
            if ja_processado:
                return {'ano_processado': True, 'ano': ano}

            erro_cad = self._salvar_cadastro_itens(empresa, dados.get('cadastro_itens_sped', []))
            if erro_cad:
                return erro_cad

            self._salvar_k230_k235(empresa, dados.get('k230_itens_produzidos', []))
            return {'sucess': True, 'ano_sped': ano}
        except Exception as e:
            return {'sucess': False, 'error': str(e), 'ano_sped': None}

    def _processar_k250_k255(self):
        try:
            processor, erro = self._carregar_sped()
            if erro:
                return erro

            dados = processor.extract_values_bloco_k_250_255()
            if not dados:
                return {'dados_sped': False}

            empresa, erro = self._obter_empresa(dados.get('cnpj_empresa'))
            if erro:
                return erro

            k250_itens = dados.get('k250_itens_produzidos', [])
            mes = (k250_itens[0].get('mes_const') if k250_itens else None) or dados.get('mes_referencia_arquivo')
            if not mes:
                return {'mes_sped': None, 'error': 'Nenhum registro K250 nem mês de referência encontrado no arquivo'}

            if analise_k25x.objects.filter(empresa=empresa, mes_sped=mes).exists():
                return {'mes_processado': True, 'mes': mes}

            erro_cad = self._salvar_cadastro_itens(empresa, dados.get('cadastro_itens_sped', []))
            if erro_cad:
                return erro_cad

            ano = self._normalizar_ano(dados.get('ano_sped'))
            self._salvar_k250_k255(empresa, k250_itens, ano)

            analise_k25x.objects.create(
                empresa=empresa,
                data_inicio=datetime.now().date(),
                mes_sped=mes,
                ano_sped=ano,
            )
            return {'sucess': True, 'mes_sped': mes}
        except Exception as e:
            return {'sucess': False, 'error': str(e), 'mes_sped': None}

    def _processar_ambos(self):
        try:
            processor, erro = self._carregar_sped()
            if erro:
                return erro

            dados_23x = processor.extract_values_bloco_k_230_235()
            dados_25x = processor.extract_values_bloco_k_250_255()
            if not dados_23x and not dados_25x:
                return {'dados_sped': False}

            cnpj = (dados_23x or {}).get('cnpj_empresa') or (dados_25x or {}).get('cnpj_empresa')
            empresa, erro = self._obter_empresa(cnpj)
            if erro:
                return erro

            k230_itens = (dados_23x or {}).get('k230_itens_produzidos', [])
            k250_itens = (dados_25x or {}).get('k250_itens_produzidos', [])
            ano = self._normalizar_ano(
                (dados_23x or {}).get('ano_sped') or (dados_25x or {}).get('ano_sped')
            )
            mes = (
                (dados_23x or {}).get('mes_referencia_arquivo')
                or (dados_25x or {}).get('mes_referencia_arquivo')
                or (k250_itens[0].get('mes_const') if k250_itens else None)
            )

            analise_23x = self._obter_analise_k23x(empresa)
            ano_ja = self._ano_ja_processado(analise_23x, ano)
            mes_ja = bool(mes and analise_k25x.objects.filter(empresa=empresa, mes_sped=mes).exists())

            if ano_ja and mes_ja:
                return {'bloco_processado': 'ambos', 'ano': ano, 'mes': mes}
            if ano_ja:
                return {'bloco_processado': '23x', 'ano': ano, 'mes': mes}
            if mes_ja:
                return {'bloco_processado': '25x', 'mes': mes, 'ano': ano}

            self._registrar_ano_analise_k23x(empresa, ano)

            cadastro = list((dados_23x or {}).get('cadastro_itens_sped', []))
            cadastro += list((dados_25x or {}).get('cadastro_itens_sped', []))
            erro_cad = self._salvar_cadastro_itens(empresa, cadastro)
            if erro_cad:
                return erro_cad

            self._salvar_k230_k235(empresa, k230_itens)

            if k250_itens:
                self._salvar_k250_k255(empresa, k250_itens, ano)
                mes_25x = k250_itens[0].get('mes_const') or mes
                analise_k25x.objects.create(
                    empresa=empresa,
                    data_inicio=datetime.now().date(),
                    mes_sped=mes_25x,
                    ano_sped=ano,
                )

            return {'sucess': True, 'ano_sped': ano, 'mes_sped': mes}
        except Exception as e:
            return {'sucess': False, 'erro': str(e)}
