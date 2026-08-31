from tkinter import NONE
from validacao.models.participantes.participantes import Participantes
from validacao.models.mercadorias_nfe.produtos import Produtos_notas
from validacao.models.mercadorias_nfe.notas import Notas_participantes
from django.http import HttpResponse
from metodo_rateio.models.sped import (
    ItensProduzidos230,
    InsumosUsados235,
    ItensProduzidos250,
    InsumosUsados255,
)
from validacao.models.painel_controle.validacao import ValidacaoDataConcluida
from cadastro.models.produtos import Cadastro_itens_sped    
from cadastro.models.empresa import Empresa
from typing import Any, Type    


class ArquivoServices:

    def __init__(self, data):
        self.empresa_id = data.get('empresa_id')
        self.mes = data.get('mes')
        self.tipo_arquivo = data.get('tipo_arquivo')

    def gerar_arquivo(self):

        self.empresa_obj = ValidacaoDataConcluida.objects.filter(empresa_id=self.empresa_id)
        self.registros_5015 = []
        
        if not self.empresa_obj:
            return HttpResponse('Nenhuma movimentação concluída para a empresa.', status=400)
        
        self.mes_obj = ValidacaoDataConcluida.objects.filter(mes_sped=self.mes, empresa_id=self.empresa_id).first()

        if not self.mes_obj:
            return HttpResponse('Nenhuma movimentação concluída para o mês.', status=400)
        
        if not self.tipo_arquivo:
            return HttpResponse('Nenhum informação de qual tipo de arquivo será gerado.', status=400)
        
        if self.tipo_arquivo in ('industrial', 'ambos'):
            
            data_db = self.consultas_bd()

            if data_db:
                return self.industrial_or_industrial_and_comercial()

            return False
        else:
            data_db = self.consultas_bd()

            if data_db:
                return self.comercial()
            
            return False

    def consultas_bd(self):
        try: 
            if self.mes_obj:
                self.data_sped = self.mes_obj.data_sped
                if not self.data_sped:
                    return HttpResponse('Data não encontrada', status=400)
                self.data_sped_part = Participantes.objects.filter(
                    data_inicio_sped=self.data_sped
                ).first()

                self.data_sped_prod = Cadastro_itens_sped.objects.filter(
                    data_inicio_sped=self.data_sped,
                    empresa_id=self.empresa_id
                ).first()

                if not self.data_sped_part:
                    return HttpResponse('Data sped não encontrada na tabela Participantes.', status=400)

                if not self.data_sped_prod:
                    return HttpResponse ('Data não encontrada em cadastro', status=400)

                self.registros_job = None
                if self.empresa_id:
                    self.registros_job = list[Any](
                        Empresa.objects.filter(id=self.empresa_id).values_list(
                                "ladca",
                                "cod_ver",
                                "cod_fin",
                                "razao_social",
                                "cnpj",
                                "inscricao_estadual",
                                "uf",
                                "codigo_municipio",
                                "opc_cred_outorgado",
                                "inscricao_estadual_intima",
                            )
                        )
                self.registro_indicador = None
                if self.empresa_id:
                    self.registro_indicador = list[Any](
                        Empresa.objects.filter(id=self.empresa_id).values_list(
                            "indicador_movimento"
                        )
                    )

                self.registro_part = None
                if self.data_sped_part and self.empresa_id:
                    self.registro_part = list[Any](
                        Participantes.objects.filter(
                            data_inicio_sped=self.data_sped,
                            empresa_id=self.empresa_id
                            ).values_list(
                                "cod_part",
                                "nome",
                                "codigo_pais",
                                "cnpj_cpf",
                                "ie",
                                "codigo_municipio",
                                "suframa",
                                "endereco",
                                "numero",
                                "complemento",
                                "bairro",
                                "phone",
                            )
                        )

                    self.registr_prod = None
                    if self.data_sped_prod and self.empresa_id:
                        self.registro_prod = list[Any](
                            Cadastro_itens_sped.objects.filter(
                                data_inicio_sped=self.data_sped,
                                empresa_id=self.empresa_id
                            ).values_list(
                                "codigo_prod", "descricao_prod", "unidade", "genero"
                            )
                        )

                    self.registro_nota_5015 = None
                    if self.data_sped and self.empresa_id:
                        # Busca todas as notas do período/data_sped, não apenas de importação
                        self.registro_nota_5015 = list[Any](
                            Notas_participantes.objects.filter(
                                data_inicio_sped=self.data_sped,
                                empresa_id=self.empresa_id
                            ).values_list(
                                "id",
                                "data_entrada_saida",
                                "tipo",
                                "numero_nota",
                                "tipo_documento",
                                "serie_documento",
                                "numero_documento",
                                "part_titular",
                            )
                        )

                    mes = self.data_sped.month

                    self.mes_sped = None
                    match mes:
                        case 1:
                            self.mes_sped = "Janeiro"
                        case 2:
                            self.mes_sped = "Fevereiro"
                        case 3:
                            self.mes_sped = "Março"
                        case 4:
                            self.mes_sped = "Abril"
                        case 5:
                            self.mes_sped = "Maio"
                        case 6:
                            self.mes_sped = "Junho"
                        case 7:
                            self.mes_sped = "Julho"
                        case 8:
                            self.mes_sped = "Agosto"
                        case 9:
                            self.mes_sped = "Setembro"
                        case 10:
                            self.mes_sped = "Outubro"
                        case 11:
                            self.mes_sped = "Novembro"
                        case 12:
                            self.mes_sped = "Dezembro"

                    if self.data_sped and self.empresa_id:
                        self.dados_k230 = list[Any](
                            ItensProduzidos230.objects.filter(
                                mes_referencia_k230=self.mes_sped,
                                empresa_id=self.empresa_id
                            ).values_list(
                                "id",
                                "codigo_item",
                                "qtd_producao_acabada",
                                "data_final_op",
                                "cod_ordem_prod",
                                "data_inicial_op",
                            )
                        )

                    if self.data_sped and self.empresa_id:
                        self.dados_k250 = list[Any](
                            ItensProduzidos250.objects.filter(
                                mes_sped=self.mes_sped,
                                empresa_id=self.empresa_id
                            ).values_list(
                                "id",
                                "cod_item",
                                "quantidade",
                            )
                        )
            return True

        except Exception as e:
            return HttpResponse(f'Erro fazer as consulta no banco: {str(e)}', status=500)


    def industrial_or_industrial_and_comercial(self):

        try:
            self.registros_5015.extend(self.registro_nota_5015)

            response = HttpResponse(content_type="text/plain")
            if self.tipo_arquivo == 'industrial':
                response["Content-Disposition"] = (
                    f'attachment; filename="arquivo_ecredac_industrial_de_{self.mes_sped} de {self.data_sped.year}.txt"'
                )
            else:
                response["Content-Disposition"] = (
                    f'attachment; filename="arquivo_ecredac_industrial_comercial_de_{self.mes_sped} de {self.data_sped.year}.txt"'
                )
            for r_job in self.registros_job:
                campo = ["0000"] + list[Any](r_job)
                linha = (
                    "|".join("" if c is None else str(c) for c in campo) + "|"
                )
                response.write(linha + "\n")

            for r_indicador in self.registro_indicador:
                campo = ["0001"] + list[Any](r_indicador)
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                )
                response.write(linha + "\n")

            for r_part in self.registro_part:
                campo = ["0150"] + list[Any](r_part)
                linha = (
                    "|".join("" if c is None else str(c) for c in campo) + "|"
                )
                response.write(linha + "\n")

            for r_prod in self.registro_prod:
                campo = ["0200"] + list[Any](r_prod)
                linha = (
                    "|".join("" if c is None else str(c) for c in campo) + "|"
                )
                response.write(linha + "\n")

            campo = ["5001", "0"] + [None]
            linha = "|" + "|".join("" if c is None else str(c) for c in campo)
            response.write(linha + "\n")

            # FICHA 1A
            try:
                contagem = 0
                for r_5015 in self.registros_5015:

                    campo = ["5010"] + [None] * 8
                    linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                    )
                    response.write(linha + "\n")

                    id_nota = r_5015[0]
                    data = r_5015[1].strftime("%d%m%Y") if r_5015[0] else ""
                    tipo = r_5015[2]
                    nota = r_5015[3]
                    tipo_documento = r_5015[4]
                    serie_documento = r_5015[5]
                    numero_documento = r_5015[6]
                    part_titular = r_5015[7]

                    if self.empresa_id:
                        self.cod_part = (
                            Participantes.objects.filter(id=part_titular, empresa_id=self.empresa_id)
                            .values_list("cod_part", flat=True)
                            .first()
                        )

                    # Busca todos os itens da nota, independente do tipo de nota (importação ou não)
                    if self.data_sped and self.empresa_id:
                        self.itens_nota = Produtos_notas.objects.filter(
                            nota_titular=id_nota, data_inicio_sped=self.data_sped, empresa_id=self.empresa_id
                        ).values_list(
                            "cfop_prod",
                            "tipo_nota",
                            "codigo_prod",
                            "quantidade_prod",
                            "valor_icms",
                            "valor_ipi",
                        )

                    codigos_ja_usados_5015 = set()
                    for item in self.itens_nota:
                        codigo_prod = item[2]
                        chave = (nota, codigo_prod) # 1234, 1-1234
                        if chave not in codigos_ja_usados_5015:
                            codigos_ja_usados_5015.add(chave)
                            cfop = item[0]
                            tipo_nota = item[1]
                            quantidade = f"{float(item[3]):.2f}".replace(".", ",")
                            # Ajuste: só converte valor_icms se não for None, senão retorna string vazia para o campo
                            valor_icms = (
                                "" if item[4] is None else str(item[4]).replace(".", ",")
                            )
                            valor_ipi = str(item[5]).replace(".", ",")
                            
                            # 'tipo_inf' será '0' para entradas, '1' para saídas
                            tipo_inf = "0" if tipo_nota == "Entrada" else "1"

                            concatenacao = f"{tipo}{nota}"

                            campo = [
                                "5015",
                                contagem,
                                data,
                                concatenacao,
                                tipo_documento,
                                serie_documento,
                                nota,
                                cfop,
                                numero_documento,
                                self.cod_part,
                                "",
                                tipo_inf,
                                codigo_prod,
                                quantidade,
                                "",
                                valor_icms,
                            ]
                            linha = (
                                "|".join("" if c is None else str(c) for c in campo)
                            )
                            response.write(linha + "\n")
                            contagem += 1

                            campo = ["5020", valor_ipi, "0"]
                            linha = (
                            "|".join("" if c is None else str(c) for c in campo)
                            )
                            response.write(linha + "\n")
                        else:
                            continue
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 1A: {str(e)}\n")


            # FICHA 1B
            try:
                campo = ["5060"] + [None] * 5
                linha = (
                            "|".join("" if c is None else str(c) for c in campo)
                        )
                response.write(linha + "\n")

                campo = ["5065"] + [None] * 13
                linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                    )
                response.write(linha + "\n")

                campo = ["5070"] + [None] * 2
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                )
                response.write(linha + "\n")
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 1B: {str(e)}\n")


            # FICHA 1C
            try:
                campo = ["5080"] + [None] * 1
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                )
                response.write(linha + "\n")

                campo = ["5085"] + [None] * 15
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                )
                response.write(linha + "\n")

                campo = ["5090"] + [None] * 1
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                )
                response.write(linha + "\n")
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 1C: {str(e)}\n")

            # FICHA 1D
            try:
                campo = ["5100"] + [None] * 3
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                )
                response.write(linha + "\n")

                campo = ["5105"] + [None] * 12
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                )
                response.write(linha + "\n")
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 1D: {str(e)}\n")


            # FICHA 2A
            try:
                codigos_ja_usados_5150 = []
                for r_5150 in self.dados_k230:
                    id = r_5150[0]
                    codigo_item = r_5150[1] # 1234 

                    if not codigo_item in codigos_ja_usados_5150:

                        codigos_ja_usados_5150.append(codigo_item)

                        qtd_producao_acabada = f"{float(r_5150[2]):.2f}".replace(".", ",")

                        dados_insumos = None
                        if self.empresa_id:
                            dados_insumos = InsumosUsados235.objects.filter(
                                item_produzido_id=id,
                                empresa_id=self.empresa_id
                            ).values_list("codigo_insumo", "quantidade")

                        campo = [
                            "5150",
                            codigo_item,
                            "0",
                            "0",
                            "0",
                            "0",
                            qtd_producao_acabada,
                            "0",
                            "0",
                        ]
                        linha = (
                            "|".join("" if c is None else str(c) for c in campo )
                        )
                        response.write(linha + "\n")

                        codigos_ja_usados_r5155 = []
                        for dados in dados_insumos:
                            cod_item = dados[0]
                            if cod_item not in codigos_ja_usados_r5155:
                                
                                codigos_ja_usados_r5155.append(cod_item)
                                
                                qtd = f"{float(dados[1]):.2f}".replace(".", ",")

                                vl_icms = None
                                if self.empresa_id:
                                    vl_icms = (
                                        Produtos_notas.objects.filter(codigo_prod=cod_item)
                                        .values_list("valor_icms", flat=True)
                                        .first()
                                    )

                                vl_icms_float = (
                                    f"{float(vl_icms) if vl_icms is not None else ''}".replace(
                                        ".", ","
                                    )
                                )
                                campo = ["5155", cod_item, qtd, '', vl_icms_float, '', ]
                                linha = (
                                    "|".join("" if c is None else str(c) for c in campo)
                                )
                                response.write(linha + "\n")
                            else:
                                continue
                    else:
                        continue

            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 2A: {str(e)}\n")

            try:
                contagem = 0
                codigos_ja_usados_5160 = []
                for r_5160_produzido in self.dados_k230:
                    # Garante que estamos usando sempre dict para facilitar acesso
                    if not isinstance(r_5160_produzido, dict):
                        # Pegando os dados que estão em tuplas e transformando eles em dict
                        r_5160_produzido = {
                            'id': r_5160_produzido[0] if len(r_5160_produzido) > 0 else None,
                            'codigo_item': r_5160_produzido[1] if len(r_5160_produzido) > 1 else None,
                            'quantidade_produzida': r_5160_produzido[2] if len(r_5160_produzido) > 2 else None,
                            'data_final_operacao': r_5160_produzido[3] if len(r_5160_produzido) > 3 else None,
                            'cod_ordem_op': r_5160_produzido[4] if len(r_5160_produzido) > 4 else None,
                        }
                    
                    qtd_produzida = float(r_5160_produzido.get('quantidade_produzida', 0) or 0)

                    if qtd_produzida > 0:
                        codigo_item = r_5160_produzido.get('codigo_item')

                        if codigo_item not in codigos_ja_usados_5160:
                            
                            codigos_ja_usados_5160.append(codigo_item)

                            id = r_5160_produzido.get('id')
                            data_final_operacao_raw = r_5160_produzido.get('data_final_operacao')
                            data_final_operacao = (
                                data_final_operacao_raw.strftime('%d%m%Y') if data_final_operacao_raw else ''
                            )
                            
                            nota_id = None
                            if self.empresa_id: nota_id = Produtos_notas.objects.filter(codigo_prod=codigo_item, empresa_id=self.empresa_id).values_list('nota_titular', flat=True).first()
                            
                            numero_nota = None
                            if self.empresa_id: numero_nota = Notas_participantes.objects.filter(id=nota_id, empresa_id=self.empresa_id).values_list('numero_nota', flat=True).first()


                            qtd_produzida_fmt = f"{float(qtd_produzida):.2f}".replace(".", ",")

                            campo = [
                                '5160',
                                contagem,
                                data_final_operacao,
                                'Produzido',
                                '',
                                '',
                                numero_nota,
                                '',
                                '',
                                codigo_item,
                                qtd_produzida_fmt,
                                '',
                                ''
                            ]
                            linha = (
                                "|".join("" if c is None else str(c) for c in campo)
                            )
                            response.write(linha + "\n")
                            contagem +=1

                            # Busca os insumos SEM chamar .list (era .values_list, veja contexto)
                            if self.empresa_id:
                                insumos = InsumosUsados235.objects.filter(
                                    item_produzido_id=id,
                                    empresa_id=self.empresa_id
                                ).values_list(
                                    'data_saida_estoque',
                                    'codigo_insumo', 
                                    'quantidade',
                                )
                            for r_5160_insumo in insumos:
                                # r_5160_insumo é tupla por causa do values_list
                                data = r_5160_insumo[0]
                                cod_item = r_5160_insumo[1]
                                qtd = f"{float(r_5160_insumo[2]):.2f}".replace(".", ",")

                                data_final_op = (
                                    data.strftime('%d%m%Y') if data else ''
                                )
                                
                                nota_id = None
                                if self.empresa_id: nota_id = Produtos_notas.objects.filter(codigo_prod=cod_item, empresa_id=self.empresa_id).values_list('nota_titular', flat=True).first()

                                numero_nota = None
                                if self.empresa_id: numero_nota = Notas_participantes.objects.filter(id=nota_id, empresa_id=self.empresa_id).values_list('numero_nota', flat=True).first()

                                campo = [
                                    '5160',
                                    contagem,
                                    data_final_op,
                                    'Insumo',
                                    '',
                                    '',
                                    numero_nota,
                                    '',
                                    '',
                                    cod_item,
                                    qtd,
                                    '',
                                    ''
                                ]
                                linha = (
                                    "|".join("" if c is None else str(c) for c in campo)
                                )
                                response.write(linha + "\n")
                                contagem += 1
                        else:
                            continue
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 2A (cont extra 5160): {str(e)}\n")
            
            # FICHA 2B
            try:
                id_atual = []
                k255_data = []
                codigos_ja_usados_r5165 = []
                for r_5165 in self.dados_k250:
                    id_k250 = r_5165[0]
                    id_atual.append(id_k250)
                    codigo_item_produzido = r_5165[1]
                    if codigo_item_produzido not in codigos_ja_usados_r5165:
                        
                        codigos_ja_usados_r5165.append(codigo_item_produzido)
                        
                        qtd_item_produzido = f"{float(r_5165[2]):.2f}".replace(".", ",")
                        
                        campo = [
                            "5165",
                            codigo_item_produzido,
                            "",
                            "",
                            "",
                            "",
                            qtd_item_produzido,
                            "",
                            "",
                        ]
                        linha = (
                            "|".join("" if c is None else str(c) for c in campo) + "|"
                        )
                        response.write(linha + "\n")
                    else:
                        continue
                    
                    dados_k255 = None
                    if self.empresa_id:
                        dados_k255 = InsumosUsados255.objects.filter(
                            k250_titular=id_k250,
                            empresa_id=self.empresa_id
                        ).values_list(
                            "cod_item",
                            "quantidade",
                        )

                    k255_data.extend(dados_k255)
                    codigos_ja_usados_r5170 = []
                    for r_5170 in dados_k255:
                        codigo_insumo_usado = r_5170[0]
                        if codigo_insumo_usado not in codigos_ja_usados_r5170:
                            
                            codigos_ja_usados_r5170.append(codigo_insumo_usado)

                            qtd_insumo_usado = f"{float(r_5170[1]):.2f}".replace(".", ",")

                            campo = [
                                "5170",
                                codigo_insumo_usado,    
                                qtd_insumo_usado,
                                "",
                                "",
                                "",
                            ]
                            linha = (
                                "|".join("" if c is None else str(c) for c in campo)
                            )
                            response.write(linha + "\n")
                        else:
                            continue

                c = 0
                codigos_ja_usados_r_5175 = []
                for r_5175 in k255_data:
                    cod_insumok255 = r_5175[0] or ''
                    if cod_insumok255 not in codigos_ja_usados_r_5175:
                        codigos_ja_usados_r_5175.append(cod_insumok255)
                        qtd_insumo = f"{float (r_5175[1] or 0):.2f}".replace('.', ',') or ''

                        info_c170 = None
                        if self.empresa_id:
                            info_c170 = Produtos_notas.objects.filter(
                                codigo_prod=cod_insumok255,
                                empresa_id=self.empresa_id
                            ).values_list(
                                'cfop_prod' or '',
                                'valor_icms' or '',
                                'valor_unitario' or '',
                                'nota_titular__part_titular__cod_part' or ''
                            ).first()

                        if not info_c170:
                            continue

                        cfop = info_c170[0] or ''
                        vl_icms = info_c170[1] or ''
                        valor_uni = f"{float(info_c170[2]):.2f}".replace('.', ',') or ''

                        cod_part = info_c170[3] or ''

                        campo = ['5175', 
                            c, 
                            '', 
                            'Insumok255', 
                            cfop, 
                            '', 
                            '', 
                            '', 
                            cod_part, 
                            '', 
                            '',
                            cod_insumok255, 
                            qtd_insumo, 
                            vl_icms, 
                            valor_uni
                        ]

                        linha = (
                            "|".join("" if c is None else str(c) for c in campo)
                        )
                        response.write(linha + "\n")
                        c +=1
                    else:
                        continue
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 2B: {str(e)}\n")

            # FICHA 2C
            try:
                for r_prod in self.registro_prod:

                    codigo_prod = r_prod[0]
                    campo = ["5180", codigo_prod, '', '', '', '']
                    linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                    )
                    
                    response.write(linha + "\n")

                    campo = ["5185"] + [None] * 12
                    linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                    )

                    response.write(linha + "\n")            

                    campo = ["5190"] + [None] * 3
                    linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                    )
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 2C: {str(e)}\n")

            # FICHA 2E
            try:
                campo = ["5210"] + [None] * 1
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                )

                response.write(linha + "\n")  

                campo = ["5215"] + [None] * 13
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                )

                response.write(linha + "\n")  
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 2E: {str(e)}\n")

            # FICHA 3A
            try:
                for r_5310 in self.dados_k230:
                    print('entrou aqui')
                    id_230 = r_5310[0]
                    data_final = r_5310[3]
                    data_inicial = r_5310[5]

                    ano_data_final = data_final.year
                    mes_data_final = data_final.month

                    ano_data_inicial = data_inicial.year
                    mes_data_inicial = data_inicial.month

                    if ano_data_inicial == ano_data_final:
                        if mes_data_inicial == mes_data_final:
                            if self.empresa_id:
                                cod_item_produzido = (
                                    ItensProduzidos230.objects.filter(id=id_230, empresa_id=self.empresa_id)
                                    .values_list("codigo_item", flat=True)
                                    .first()
                                )

                                campo = ["5310", cod_item_produzido, "", "", "", "", "", ""]
                                linha = (
                                    "|".join("" if c is None else str(c) for c in campo)
                                )
                                response.write(linha + "\n")

                                campo = ["5315"] + [None] * 4
                                linha = (
                                    "|".join("" if c is None else str(c) for c in campo)
                                )
                                response.write(linha + "\n")

                                campo = ["5320"] + [None] * 4
                                linha = (
                                    "|".join("" if c is None else str(c) for c in campo)
                                )
                                response.write(linha + "\n")

                                campo = ["5325"] + [None] * 3
                                linha = (
                                    "|".join("" if c is None else str(c) for c in campo)
                                )
                                response.write(linha + "\n")
                        else:
                            continue
                    else:
                        continue
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 3A: {str(e)}\n")

            # FICHA 3B
            try:
                if self.tipo_arquivo == 'ambos':

                    campo = ["5360"] + [None] * 7
                    linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                        )
                    response.write(linha + "\n")

                    campo = ["5365"] + [None] * 17
                    linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                        )
                    response.write(linha + "\n")

                    campo = ["5370"] + [None] * 2
                    linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                        )
                    response.write(linha + "\n")

                    campo = ["5375"] + [None] * 4
                    linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                        )
                    response.write(linha + "\n")

                    campo = ["5380"] + [None] * 3
                    linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                        )
                    response.write(linha + "\n")
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 3B: {str(e)}\n")

            # FICHA 3C
            try:
                campo = ["5410"] + [None] * 7
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                    )
                response.write(linha + "\n")

                campo = ["5415"] + [None] * 16
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                    )
                response.write(linha + "\n")

                campo = ["5420"] + [None] * 4
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                    )
                response.write(linha + "\n")

                campo = ["5425"] + [None] * 3
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                    )
                response.write(linha + "\n")
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 3C: {str(e)}\n")

            # FICHA 5B
            try:
                campo = ["5550"] + [None] * 3
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                    )
                response.write(linha + "\n")

                campo = ["5555"] + [None] * 12
                linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                    )
                response.write(linha + "\n")
            except Exception as e:
                return HttpResponse(f"# Erro na FICHA 5B: {str(e)}\n")

            return response
        except Exception as e:
            return HttpResponse('Erro ao gerar aquivo')

    def comercial(self):
        
        self.registros_5015.extend(self.registro_nota_5015)

        response = HttpResponse(content_type="text/plain")
        response["Content-Disposition"] = (
            f'attachment; filename="arquivo_ecredac_comercial_de_{self.mes_sped} de {self.data_sped.year}.txt"'
        )

        for r_job in self.registros_job:
            campo = ["0000"] + list[Any](r_job)
            linha = (
                "|".join("" if c is None else str(c) for c in campo) + "|"
            )
            response.write(linha + "\n")

        for r_indicador in self.registro_indicador:
            campo = ["0001"] + list[Any](r_indicador)
            linha = (
                "|".join("" if c is None else str(c) for c in campo)
            )
            response.write(linha + "\n")

        for r_part in self.registro_part:
            campo = ["0150"] + list[Any](r_part)
            linha = (
                "|".join("" if c is None else str(c) for c in campo) + "|"
            )
            response.write(linha + "\n")

        for r_prod in self.registro_prod:
            campo = ["0200"] + list[Any](r_prod)
            linha = (
                "|".join("" if c is None else str(c) for c in campo) + "|"
            )
            response.write(linha + "\n")

        campo = ["5001", "0"] + [None]
        linha = "|".join("" if c is None else str(c) for c in campo)
        response.write(linha + "\n")

        # FICHA 1A
        contagem = 0
        for r_5015 in self.registros_5015:

            campo = ["5010"] + [None] * 8
            linha = (
                "|".join("" if c is None else str(c) for c in campo)
            )
            
            response.write(linha + "\n")

            id_nota = r_5015[0]
            data = r_5015[1].strftime("%d%m%Y") if r_5015[0] else ""
            tipo = r_5015[2]
            nota = r_5015[3]
            tipo_documento = r_5015[4]
            serie_documento = r_5015[5]
            numero_documento = r_5015[6]
            part_titular = r_5015[7]

            if self.empresa_id:
                self.cod_part = (
                    Participantes.objects.filter(id=part_titular, empresa_id=self.empresa_id)
                    .values_list("cod_part", flat=True)
                    .first()
                )

            # Busca todos os itens da nota, independente do tipo de nota (importação ou não)
            if self.data_sped and self.empresa_id:
                self.itens_nota = Produtos_notas.objects.filter(
                    nota_titular=id_nota, data_inicio_sped=self.data_sped, empresa_id=self.empresa_id
                ).values_list(
                    "cfop_prod",
                    "tipo_nota",
                    "codigo_prod",
                    "quantidade_prod",
                    "valor_icms",
                    "valor_ipi",
                )

            codigos_ja_usados_5015 = set()
            for item in self.itens_nota:
                codigo_prod = item[2]
                chave = (nota, codigo_prod) # 1234, 1-1234
                if chave not in codigos_ja_usados_5015:
                    codigos_ja_usados_5015.add(chave)
                    cfop = item[0]
                    tipo_nota = item[1]
                    quantidade = f"{float(item[3]):.2f}".replace(".", ",")
                    # Ajuste: só converte valor_icms se não for None, senão retorna string vazia para o campo
                    valor_icms = (
                        "" if item[4] is None else str(item[4]).replace(".", ",")
                    )
                    valor_ipi = str(item[5]).replace(".", ",")
                    
                    # 'tipo_inf' será '0' para entradas, '1' para saídas
                    tipo_inf = "0" if tipo_nota == "Entrada" else "1"

                    concatenacao = f"{tipo}{nota}"

                    campo = [
                        "5015",
                        contagem,
                        data,
                        concatenacao,
                        tipo_documento,
                        serie_documento,
                        nota,
                        cfop,
                        numero_documento,
                        self.cod_part,
                        "",
                        tipo_inf,
                        codigo_prod,
                        quantidade,
                        "",
                        valor_icms,
                    ]
                    linha = (
                        "|".join("" if c is None else str(c) for c in campo)
                    )
                    response.write(linha + "\n")
                    contagem += 1

                    campo = ["5020", valor_ipi, "0"]
                    linha = (
                    "|".join("" if c is None else str(c) for c in campo)
                    )
                    response.write(linha + "\n")
                else:
                    continue

        # FICHA 1C
        campo = ["5080"] + [None] * 1
        linha = (
            "|".join("" if c is None else str(c) for c in campo)
        )
        response.write(linha + "\n")

        campo = ["5085"] + [None] * 15
        linha = (
            "|".join("" if c is None else str(c) for c in campo)
        )
        response.write(linha + "\n")

        campo = ["5090"] + [None] * 1
        linha = (
            "|".join("" if c is None else str(c) for c in campo)
        )
        response.write(linha + "\n")

        # FICHA 1D
        campo = ["5100"] + [None] * 3
        linha = (
            "|".join("" if c is None else str(c) for c in campo)
        )
        response.write(linha + "\n")

        campo = ["5105"] + [None] * 12
        linha = (
            "|".join("" if c is None else str(c) for c in campo)
        )
        response.write(linha + "\n")

        # FICHA 3B
        campo = ["5360"] + [None] * 7
        linha = (
            "|".join("" if c is None else str(c) for c in campo)
            )
        response.write(linha + "\n")

        campo = ["5365"] + [None] * 17
        linha = (
            "|".join("" if c is None else str(c) for c in campo)
            )
        response.write(linha + "\n")

        campo = ["5370"] + [None] * 2
        linha = (
            "|".join("" if c is None else str(c) for c in campo)
            )
        response.write(linha + "\n")

        campo = ["5375"] + [None] * 4
        linha = (
            "|".join("" if c is None else str(c) for c in campo)
            )
        response.write(linha + "\n")

        campo = ["5380"] + [None] * 3
        linha = (
            "|".join("" if c is None else str(c) for c in campo)
            )
        response.write(linha + "\n")

        return response

        
                