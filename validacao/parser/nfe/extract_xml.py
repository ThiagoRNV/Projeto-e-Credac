from typing import List, Dict, Any
import xml.etree.ElementTree as ET
import logging
from validacao.utils.normalizadores import normalizador_decimal
from decimal import Decimal

logger = logging.getLogger(__name__)

class XMLProcesses:

    produtos_xml: List[Dict[str, Any]] = []

    """Métodos para processar arquivos XML e extrair informações específicas"""
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.tree = None
        self.root = None
        self.ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}

    def _read_xml_bytes(self) -> bytes:
        xml_source = self.xml_file
        if hasattr(xml_source, 'read'):
            if hasattr(xml_source, 'seek'):
                xml_source.seek(0)
            data = xml_source.read()
            if hasattr(xml_source, 'seek'):
                xml_source.seek(0)
            if isinstance(data, str):
                return data.encode('utf-8')
            return data
        if isinstance(xml_source, (bytes, bytearray)):
            return bytes(xml_source)
        with open(xml_source, 'rb') as f:
            return f.read()

    def load_xml(self) -> bool:
        """Carrega o arquivo XML (arquivo, upload Django ou conteúdo em bytes)."""
        try:
            content = self._read_xml_bytes()
            if content.startswith(b'\xef\xbb\xbf'):
                content = content[3:]
            self.root = ET.fromstring(content)
            self.tree = ET.ElementTree(self.root)
            logger.info(f"XML carregado com sucesso. Root tag: {self.root.tag}")
            return True
        except ET.ParseError as e:
            logger.error(f"Erro de parsing XML: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao carregar XML: {e}")
            return False

    def extract_generic_values(self, xpath_expressions: Dict[str, str]) -> Dict[str, Any]:
        """
        Extrai valores usando expressões XPath personalizadas, sem usar convert_value
        """
        if not self.root:
            return {}

        values = {}

        for key, xpath in xpath_expressions.items():
            try:
                elements = self.root.findall(xpath, self.ns)
                if not elements:
                    values[key] = None
                elif len(elements) == 1:
                    values[key] = elements[0].text or ''
                else:
                    values[key] = [elem.text or '' for elem in elements]
            except Exception as e:
                logger.error(f"Erro ao extrair {key}: {e}")
                values[key] = None

        return values


    @staticmethod
    def extract_xml_file(file_path: str, extraction_type: str = 'nfe') -> Dict[str, Any]:
            """Processa arquivo NFe (XML). Para cada nota (infNFe) divide os totais da nota igualmente
            entre os itens (det) e retorna a lista de produtos com 'valor_rateado' e 'valor_total'.
            """
            processor = XMLProcesses(file_path)
            if not processor.load_xml():
                return {}

            if extraction_type != 'nfe':
                logger.warning(f"Tipo de extração desconhecido: {extraction_type}")
                return {}

            produtos_list: List[Dict[str, Any]] = []

            # percorre cada bloco infNFe (suporta múltiplas notas por arquivo)
            infs = processor.root.findall('.//ns:infNFe', processor.ns)
            if not infs:
                return {'produtos': produtos_list}

            
            for inf in infs:
                numero_nota = inf.findtext('.//ns:ide/ns:nNF', default='', namespaces=processor.ns).strip()


                numero_id = inf.get('Id') or inf.get('id') if inf is not None else ''

            
                numero_id_formatado = numero_id[3:]


                
                # totais da nota para rateio (frete, seguro, outros, desconto)
                valor_frete_xml = normalizador_decimal(inf.findtext('.//ns:ICMSTot/ns:vFrete', default='', namespaces=processor.ns) or 0)
                valor_seguro_xml = normalizador_decimal(inf.findtext('.//ns:ICMSTot/ns:vSeg', default='', namespaces=processor.ns) or 0)
                valor_outros_xml = normalizador_decimal(inf.findtext('.//ns:ICMSTot/ns:vOutro', default='', namespaces=processor.ns) or 0)
                valor_desconto_xml = normalizador_decimal(inf.findtext('.//ns:ICMSTot/ns:vDesc', default='', namespaces=processor.ns) or 0)
                    
                dets = inf.findall('.//ns:det', processor.ns)
                itens_temp: List[Dict[str, Any]] = []

                for det in dets:
                    qtd_text = det.findtext('.//ns:prod/ns:qCom', default='', namespaces=processor.ns).strip()
                    vprod_text = det.findtext('.//ns:prod/ns:vProd', default='', namespaces=processor.ns).strip()

                    qtd_prod = normalizador_decimal(qtd_text)
                    valor_prod = normalizador_decimal(vprod_text)

                    # Extrair IPI e ST por item (não do total da nota)
                    valor_st_item = normalizador_decimal(det.findtext('.//ns:ICMS/*/ns:vICMSST', default='', namespaces=processor.ns) or 0)
                    valor_ipi_item = normalizador_decimal(det.findtext('.//ns:IPI/ns:IPITrib/ns:vIPI', default='', namespaces=processor.ns) or 0)
                    
                    # Se não encontrou no IPITrib, tenta IPINT
                    if not valor_ipi_item:
                        valor_ipi_item = normalizador_decimal(det.findtext('.//ns:IPI/ns:IPINT/ns:vIPI', default='', namespaces=processor.ns) or 0)

                    orig = det.findtext('.//ns:ICMS/*/ns:orig', default='', namespaces=processor.ns).strip()
                    cst =  det.findtext('.//ns:ICMS/*/ns:CST', default='', namespaces=processor.ns).strip()

                    cst_3digitos = f"{orig}{cst}"

                    # Calcular imposto do item: IPI + ST
                    calculo_imposto_item = round(valor_st_item + valor_ipi_item, 2)

                    prod = {
                        'numero_nota': numero_nota,
                        'numero_id': numero_id_formatado,
                        'chave_nota': inf.findtext('.//ns:protNFe/ns:chNFe', default='', namespaces=processor.ns).strip(),
                        'codigo_prod': det.findtext('.//ns:prod/ns:cProd', default='', namespaces=processor.ns).strip(),
                        'descricao_prod': det.findtext('.//ns:prod/ns:xProd', default='', namespaces=processor.ns).strip(),
                        'unidade': det.findtext('.//ns:prod/ns:uCom', default='', namespaces=processor.ns).strip(),
                        'ncm': det.findtext('.//ns:prod/ns:NCM', default='', namespaces=processor.ns).strip(),
                        'valor_prod': round(valor_prod, 2),
                        'quantidade_prod': qtd_prod,
                        'valor_unitario': round(valor_prod / qtd_prod, 2) if qtd_prod else 0,
                        'cfop': det.findtext('.//ns:prod/ns:CFOP', default='', namespaces=processor.ns).strip(),
                        'cst': cst_3digitos,
                        'cest': det.findtext('.//ns:prod/ns:CEST', default='', namespaces=processor.ns).strip(),
                        'valor_ipi': valor_ipi_item, 
                        'valor_icms': det.findtext('.//ns:ICMS/*/ns:vICMS', default='', namespaces=processor.ns).strip(),
                        'base_icms': det.findtext('.//ns:ICMS/*/ns:vBC', default='', namespaces=processor.ns).strip(),
                        'aliquota_icms': det.findtext('.//ns:ICMS/*/ns:pICMS', default='', namespaces=processor.ns).strip(),
                    }
                    itens_temp.append(prod)

                # calcular valor para rateio (frete + seguro + outros - desconto)
                n = len(itens_temp)
                valor_para_rateio = round(valor_frete_xml + valor_seguro_xml + valor_outros_xml - valor_desconto_xml, 2)

                if n == 0:
                    continue

                if valor_para_rateio == 0:
                    for prod in itens_temp:
                        prod['valor_rateado'] = 0
                        valor_prod = normalizador_decimal(prod.get('valor_prod', 0))
                        calculo_imposto_item = normalizador_decimal(prod.get('calculo_imposto', 0))
                        # valor_total = valor_prod + valor_rateado + (IPI + ST)
                        prod['valor_total'] = round(valor_prod + calculo_imposto_item, 2)
                        produtos_list.append(prod)
                else:
                    base_share = round(valor_para_rateio / n, 2)
                    acumulado = Decimal('0.0')
                    for i, prod in enumerate(itens_temp):
                        if i < n - 1:
                            valor_rateado = base_share
                            acumulado += valor_rateado
                        else:
                            valor_rateado = round(valor_para_rateio - acumulado, 2)

                        prod['valor_rateado'] = valor_rateado
                        valor_prod = normalizador_decimal(prod.get('valor_prod', 0))
                        calculo_imposto_item = normalizador_decimal(prod.get('calculo_imposto', 0))
                        # valor_total = valor_prod + valor_rateado + (IPI + ST)
                        total_calculado = valor_prod + valor_rateado + calculo_imposto_item
                        prod['valor_total'] = round(total_calculado, 2)
                        produtos_list.append(prod)

            return {'produtos': produtos_list}