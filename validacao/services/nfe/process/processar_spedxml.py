from datetime import datetime, timezone
from cadastro.urls import empresa
from validacao.models.painel_controle.validacao import ValidacaoStatus
from validacao.models.mercadorias_nfe.produtos import Produtos_notas
from validacao.models.mercadorias_nfe.notas import Notas_participantes
from validacao.models.participantes.participantes import Participantes
from cadastro.models.produtos import Cadastro_itens_sped
from validacao.utils.normalizadores import normalizador_decimal
from validacao.parser.nfe.extract_sped import SPEDProcesses
from validacao.parser.nfe.extract_xml import XMLProcesses
from cadastro.models.empresa import Empresa
import logging
logger = logging.getLogger(__name__)

""" Tratamentos de exceções """
class SpedXmlException(Exception):
    pass

class SpedXmlTypeError(SpedXmlException):
    def __init__(self, message='O arquivo deve ser .txt') -> None:
        super().__init__(message)

class EmptyListNfe(SpedXmlException):
    def __init__(self, message='Não é possível fazer o processamento. Empresa está inativa') -> None:
        super().__init__(message)

class NotCompainer(SpedXmlException):
    def __init__(self, message='Empresa não cadastrada') -> None:
        super().__init__(message)


class ProcessSpedXml:
    

    def __init__(self, sped_file, folder_xml) -> None:
        self.sped_file = sped_file
        # UploadedFile é iterável por linhas; um único arquivo não pode ser
        # percorrido diretamente senão cada chunk vira um "XML" inválido.
        if folder_xml is None:
            self.folder_xml = []
        elif isinstance(folder_xml, (list, tuple)):
            self.folder_xml = list(folder_xml)
        else:
            self.folder_xml = [folder_xml]

    erro = False
    def process(self):

        if not self.sped_file:
            logger.error("Nenhum arquivo SPED enviado")
            raise SpedXmlException()

        if not self.sped_file.name.endswith('.txt'):
            raise SpedXmlTypeError()

        sped_processor = SPEDProcesses(self.sped_file)

        if not sped_processor.load_sped_file():
            logger.error("Erro ao carregar o arquivo SPED.")
            raise SpedXmlException()

        dados_sped = sped_processor.extract_values_sped()

        ver_list_cnpj_empresa = dados_sped.get('cnpj_empresa', [])

        if not ver_list_cnpj_empresa:
            raise EmptyListNfe()

        cnpj_empresa = None
        if ver_list_cnpj_empresa:
            cnpj_empresa = dados_sped.get('cnpj_empresa', [])[0]

        empresa_obj = Empresa.objects.filter(cnpj=cnpj_empresa).first()

        if not empresa_obj:
            raise NotCompainer()

        for part in dados_sped.get('participantes', []):
            participante_obj, created = Participantes.objects.update_or_create(
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

            for nota in part.get('notas', []):
                nota_data_inicio = nota.get('data_inicio_sped') or participante_obj.data_inicio_sped
                nota_data_fim = nota.get('data_fim_sped') or participante_obj.data_fim_sped

                nota_obj = Notas_participantes.objects.create(
                    part_titular=participante_obj,
                    numero_nota=nota.get('numero_nota'),
                    tipo=nota.get('tipo'), # 'Entrada' ou 'Saida'
                    data_inicio_sped=nota_data_inicio,
                    data_fim_sped=nota_data_fim,
                    empresa=empresa_obj,
                    chave_nota=nota.get('chave_nota'),
                    codigo_uf=nota.get('codigo_uf'),
                    status=nota.get('status'),
                    tipo_operacao=nota.get('tipo_operacao'),  # 'Importação' se houver C110 com IMPORT
                    numero_documento=nota.get('numero_documento'),  # Número do documento de importação do C120
                    mes_sped=nota.get('mes_referencia'),
                    data_entrada_saida=nota.get('data_entrada_saida'),
                    tipo_documento=nota.get('tipo_documento'),
                    serie_documento=nota.get('serie_documento'), 
                )
                for prod in nota.get('produtos', []):

                    prod_data_inicio = prod.get('data_inicio_sped') or nota_data_inicio
                    prod_data_fim = prod.get('data_fim_sped') or nota_data_fim
                    codigo_prod = prod.get('codigo_prod')
                    cfop = prod.get('cfop')
                    tipo = nota_obj.tipo

                    try:
                        if tipo == 'Entrada' and cfop in ('1102', '2102', '2102'):
                            tipo_movimento = 'Compras'
                            cod_lancamento = '100' 
                        elif tipo == 'Saida' and cfop in ('5101', '5102', '6101', '6102'):
                            tipo_movimento = 'Vendas'
                            cod_lancamento =  '101'
                        elif tipo == 'Entrada' and cfop in ('1152', '2152'):
                            tipo_movimento = 'Transferencias'
                            cod_lancamento = '102'
                        elif tipo == 'Saida' and cfop in ('1152', '2152'): 
                            tipo_movimento = 'Transferencias'
                            cod_lancamento = '220'
                        elif tipo == 'Entrada' and cfop in ('1202', '2202'): 
                            tipo_movimento = 'Devolucoes'
                            cod_lancamento = '101'
                        elif tipo == 'Saida' and cfop in ('1202', '2202'):
                            tipo_movimento = 'Devolucoes'
                            cod_lancamento = '210'
                        elif tipo == 'Entrada' and cfop in ('5901', '6901'):
                            tipo_movimento = 'Producao propria'
                            cod_lancamento = '120'
                        else:
                            tipo_movimento = None
                            cod_lancamento = None
                    except Exception as e:
                        print(f'Erro ao fazer as comparações: {e}')

                    Produtos_notas.objects.create(
                        tipo_nota=nota_obj.tipo,
                        nota_titular=nota_obj,
                        data_inicio_sped=prod_data_inicio,
                        data_fim_sped=prod_data_fim,
                        empresa=empresa_obj,
                        codigo_prod=prod.get('codigo_prod'),
                        descricao_prod=prod.get('descricao_prod'),
                        unidade=prod.get('unidade'),
                        tipo_item=prod.get('tipo_item'),
                        ncm=prod.get('ncm'),
                        cfop_prod=prod.get('cfop'),
                        cest=prod.get('cest'),
                        cst=prod.get('cst'),
                        valor_ipi=normalizador_decimal(prod.get('valor_ipi')),
                        valor_icms=normalizador_decimal(prod.get('valor_icms')),
                        base_icms=normalizador_decimal(prod.get('base_icms')),
                        aliquota_icms=normalizador_decimal(prod.get('aliquota_icms')),
                        quantidade_prod=normalizador_decimal(prod.get('quantidade')),
                        valor_unitario=normalizador_decimal(prod.get('valor_unitario')),
                        valor_total=normalizador_decimal(prod.get('valor_total')),
                        status='C/N', # ✅ Define status padrão (Com Nota)
                        tipo_movimento=tipo_movimento,
                        cod_lancamento=cod_lancamento,
                    )

        data_fim_sped = None
        for item in dados_sped.get('cadastro_itens_sped', []):
            data_fim_sped = item.get('data_fim_sped')
            if not isinstance(item, dict):
                continue
            cod_prod = item.get('codigo_prod')
            prod_obj = Produtos_notas.objects.filter(
                codigo_prod=cod_prod
            ).first()
            try:
                Cadastro_itens_sped.objects.get_or_create(
                    empresa=empresa_obj,
                    codigo_prod=cod_prod,
                    defaults={
                        'produto_titular': prod_obj if prod_obj else None,
                        'data_inicio_sped': item.get('data_inicio_sped'),
                        'data_fim_sped': data_fim_sped,
                        'descricao_prod': item.get('descricao_prod'),
                        'unidade': item.get('unidade'),
                        'tipo_item': item.get('tipo_item'),
                        'ncm': item.get('ncm'),
                        'cest': item.get('cest'),
                        'genero': item.get('cod_gen'),
                        'mes_ref':nota_obj.mes_sped,
                        'ano_sped': item.get('data_inicio_sped').year
                    },
                )
            except Exception as e:
                logger.error(f'Erro ao criar cadastro de itens SPED: {str(e)}')
                continue

        # ===================== PROCESSAMENTO XML =====================
        
        data_sped_atual = dados_sped.get('data_inicio_sped')
        if not data_sped_atual and dados_sped.get('participantes'):
            data_sped_atual = dados_sped.get('participantes', [{}])[0].get('data_inicio_sped')
        
        if self.folder_xml:
            produtos_criados = []
            notas_participantes_xml = []
            produtos_xml = []
            erros = []

            for xml_file in self.folder_xml:
                xml_name = getattr(xml_file, 'name', '')
                if not xml_name.lower().endswith('.xml'):
                    continue
                try:
                    dados_xml = XMLProcesses.extract_xml_file(xml_file)
                    xml_data = dados_xml.get('produtos', [])

                    if not xml_data:
                        logger.error('Erro ao extrair info produtos do XML.')
                        raise SpedXmlException()

                    for produtos in xml_data:
                        if not isinstance(produtos, dict):
                            logger.error(f"Produto do XML não é dict: {produtos}")
                            raise SpedXmlException()

                        numero_nota = produtos.get('numero_nota', '').strip()

                        if not numero_nota:
                            logger.warning(f"Arquivo '{xml_file.name}' sem número de nota.")
                            continue

                        notas_query = Notas_participantes.objects.filter(
                            numero_nota=numero_nota,    
                            empresa=empresa_obj
                        )

                        cod_prod = produtos.get('codigo_prod')
                        cadastro_itens = dados_sped.get('cadastro_itens_sped', [])

                        codigos_cadastrados = set()
                        for item in cadastro_itens:
                            codigo_item = item.get('codigo_prod')
                            if codigo_item:
                                codigos_cadastrados.add(codigo_item)
                   
               

                        if data_sped_atual:
                            notas_query = notas_query.filter(data_inicio_sped=data_sped_atual)
                        notas_participantes_saida = notas_query.first()


                        mes = {
                            '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
                            '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
                            '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'

                        }

                        data = str(data_sped_atual)
                        if '-' in data:
                            mes_number = data[5:7]
                        else:
                            mes_number = data[4:6]

                        mes_ref = mes.get(mes_number)

                        if notas_participantes_saida: 
                            notas_participantes_saida.status = 'C/PRODUTO'
                            notas_participantes_saida.tipo = 'Saida'
                            notas_participantes_saida.save()

                            if cod_prod not in codigos_cadastrados:
                                try:
                                    Cadastro_itens_sped.objects.get_or_create(
                                        empresa=empresa_obj,
                                        codigo_prod=cod_prod,
                                        defaults = {
                                            'data_inicio_sped':data_sped_atual,
                                            'data_fim_sped':data_fim_sped,
                                            'descricao_prod':produtos.get('descricao_prod'),
                                            'unidade':produtos.get('unidade'),
                                            'ncm':produtos.get('ncm'),
                                            'cest':produtos.get('cest'),
                                            'mes_ref':mes_ref,
                                        }
                                    )
                                except Exception as e:
                                    logger.error(f'Erro ao criar cadastro de itens SPED: {str(e)}')
                                    continue

                            produto_obj = Produtos_notas.objects.create(
                                tipo_nota='Saida',
                                empresa=empresa_obj,
                                nota_titular=notas_participantes_saida,
                                data_inicio_sped=data_sped_atual,
                                codigo_prod=cod_prod,
                                descricao_prod=produtos.get('descricao_prod'),
                                ncm=produtos.get('ncm'),
                                cfop_prod=produtos.get('cfop'),
                                unidade=produtos.get('unidade'),
                                cst=produtos.get('cst'),
                                quantidade_prod=normalizador_decimal(produtos.get('quantidade_prod')),
                                valor_total=normalizador_decimal(produtos.get('valor_total')),
                                valor_unitario=normalizador_decimal(produtos.get('valor_unitario')),
                                base_icms=normalizador_decimal(produtos.get('base_icms')),
                                valor_ipi=normalizador_decimal(produtos.get('valor_ipi')),
                                valor_icms=normalizador_decimal(produtos.get('valor_icms')),
                                valor_pis=normalizador_decimal(produtos.get('valor_pis')),
                                cest=produtos.get('cest'),
                                aliquota_icms=normalizador_decimal(produtos.get('aliquota_icms')),
                                tipo_item=produtos.get('numero_item'),
                                status='C/N',
                            )
                            produtos_criados.append(produto_obj)
                            logger.info(
                                f"Produto {produto_obj.codigo_prod} da nota {numero_nota} criado via XML (sem dedupe)."
                            )

                        else:
                            # ✅ CRÍTICO: Usa sempre a data do SPED atual para notas e produtos criados a partir de XMLs
                            notas_participantes_obj = Notas_participantes.objects.create(
                                tipo='Saida',
                                chave_nota=produtos.get('chave_nota'),
                                nota_titular=None,
                                cod_part='---',
                                codigo_uf=None,
                                empresa=empresa_obj,
                                data_inicio_sped=data_sped_atual,
                                status='C/PRODUTO',
                            )

                            if cod_prod not in codigos_cadastrados:
                                try:
                                    Cadastro_itens_sped.objects.get_or_create(
                                        empresa=empresa_obj,
                                        codigo_prod=cod_prod,
                                        defaults = {
                                            'data_inicio_sped':data_sped_atual,
                                            'data_fim_sped':data_fim_sped,
                                            'descricao_prod':produtos.get('descricao_prod'),
                                            'unidade':produtos.get('unidade'),
                                            'ncm':produtos.get('ncm'),
                                            'cest':produtos.get('cest'),
                                            'mes_ref':mes_ref,
                                        }
                                    )
                                except Exception as e:
                                    logger.error(f'Erro ao criar cadastro de itens SPED: {str(e)}')
                                    continue

                            notas_participantes_xml.append(notas_participantes_obj)

                            produto_obj = Produtos_notas.objects.create(
                                tipo_nota='Saida',
                                nota_titular=notas_participantes_obj,
                                empresa=empresa_obj,
                                data_inicio_sped=data_sped_atual,
                                codigo_prod=produtos.get('codigo_prod'),
                                descricao_prod=produtos.get('descricao_prod'),
                                ncm=produtos.get('ncm'),
                                cfop_prod=produtos.get('cfop'),
                                unidade=produtos.get('unidade'),
                                cst=produtos.get('cst'),
                                quantidade_prod=normalizador_decimal(produtos.get('quantidade_prod')),
                                valor_total=normalizador_decimal(produtos.get('valor_total') or produtos.get('valor_total_bruto') or produtos.get('valor_prod')),
                                valor_unitario=normalizador_decimal(produtos.get('valor_unitario')),
                                base_icms=normalizador_decimal(produtos.get('base_icms')),
                                valor_ipi=normalizador_decimal(produtos.get('valor_ipi')),
                                valor_pis=normalizador_decimal(produtos.get('valor_pis')),
                                valor_icms=normalizador_decimal(produtos.get('valor_icms')),
                                cest=produtos.get('cest'),
                                aliquota_icms=normalizador_decimal(produtos.get('aliquota_icms')),
                                tipo_item=produtos.get('numero_item'),
                                status='C/N',
                            )

                            produtos_xml.append(produto_obj)

                except Exception as e:
                    logger.error(f"Erro ao processar {getattr(xml_file, 'name', 'UNKNOWN')}: {e}") 
                    erros.append(f"Erro ao processar '{getattr(xml_file, 'name', 'UNKNOWN')}': {str(e)}")

            # ✅ CRÍTICO: Usa a data do SPED atual processado, não de participantes antigos
            data_sped_validacao = data_sped_atual or dados_sped.get('data_inicio_sped')
            if not data_sped_validacao and dados_sped.get('participantes'):
                data_sped_validacao = dados_sped.get('participantes', [{}])[0].get('data_inicio_sped')

            ValidacaoStatus.objects.create(
                empresa=empresa_obj,
                status='em_andamento',
                progresso=0,
                # data_atualizacao=timezone.now(),
                data_sped=data_sped_validacao,
                sped=True,
                xml=True,
                mes_sped=dados_sped.get('mes_sped'),
                tipo_validacao='nfe'
            )

        return {'success': True}