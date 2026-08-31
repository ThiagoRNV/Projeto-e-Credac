from datetime import datetime
from typing import List, Dict, Any, Optional
from regras_companies.validacao import ValidarRegra
from cadastro.models.empresa import EmpresaRegra , Empresa 

regras = None
v_regra = None

def varificao_bloco0210(self: List[str]) -> List[Dict[str, Any]]:
    codigos_prod = []
    for line in self:
        parts = line.strip().split('|')
        if len(parts) > 1 and parts[1] == '0210':
            k210 = {
                'codigos_prod': parts[2] if len(parts) > 2 else None,
            }
            codigos_prod.append(k210)

    if not codigos_prod:
        return False
    return codigos_prod  
      
class BlocoKProcessesServices:

    def __init__(self, sped_file):
        self.sped_file = sped_file
        self.mes_referencia = []

    def _registro_k(self, parts, registro: str):
        """Retorna (encontrado, offset) para registros K230/K235/K250/K255."""
        if len(parts) < 2:
            return False, 0
        registro = registro.upper()
        if parts[0].upper() == registro:
            return True, 0
        if parts[1].upper() == registro:
            return True, 1
        return False, 0

    def _extrair_mes_referencia(self, parts, meses_nomes):
        """Extrai o mês de referência a partir do registro 0000."""
        mes_referencia_arquivo = None
        data_inicio_sped = None
        data_fim_sped = None
        ano_sped = None

        if len(parts) > 4 and parts[4]:
            try:
                data_inicio_sped = datetime.strptime(parts[4], '%d%m%Y').date()
                mes_referencia_arquivo = meses_nomes.get(data_inicio_sped.month, '')
                if len(parts[4]) >= 4:
                    ano_sped = parts[4][4:]
            except (ValueError, TypeError):
                mes_referencia_arquivo = None

        if len(parts) > 5 and parts[5]:
            try:
                data_fim_sped = datetime.strptime(parts[5], '%d%m%Y').date()
                mes_referencia_arquivo = meses_nomes.get(data_fim_sped.month, '')
            except (ValueError, TypeError):
                pass

        return mes_referencia_arquivo, data_inicio_sped, data_fim_sped, ano_sped

    def load_sped_file(self) -> bool:
        """
        Carrega o arquivo SPED enviado e armazena cada linha em self.mes_referencia
        """
        try:
            self.sped_file.seek(0)  # volta para o início do arquivo
            self.mes_referencia = [line.decode('utf-8', errors='ignore').strip() for line in self.sped_file]
            return True
        except Exception as e:
            print(f"Erro ao carregar SPED: {e}")
            return False

    def extract_values_bloco_k_230_235(self):
     
        k230_itens_produzidos = []
        k235_insumos_usados = []
        cadastro_itens_sped = []
        cnpj_empresa = None
        data_inicio_sped = None
        data_fim_sped = None
        ano_sped = None
        empresa_regras = EmpresaRegra.objects.none()
        k230_atual = None
        
        def _norm(value: Optional[str]) -> Optional[str]:
            if value is None:
                return None
            v = str(value).strip()
            return v if v else None

        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        mes_referencia_arquivo = None
        
        for line in self.mes_referencia:
            parts = line.strip().split('|')


            if len(parts) > 1 and parts[1] == '0000':
                cnpj_empresa = parts[7] if len(parts) > 7 else None

                empresa_id = Empresa.objects.filter(
                    cnpj=cnpj_empresa
                ).values_list(
                    'id', 
                    flat=True
                ).first()

                empresa_regras = EmpresaRegra.objects.filter(empresa_id=empresa_id, status=True).select_related('regra')

                mes_ref, data_inicio_sped, data_fim_sped, ano_sped = self._extrair_mes_referencia(parts, meses_nomes)
                mes_referencia_arquivo = mes_ref

            elif len(parts) > 1 and parts[1] == '0200':
               
                cod_prod = _norm(parts[2] if len(parts) > 2 else None)    

                codigo_produto = cod_prod

                v_regras = ValidarRegra(codigo_produto or '', '')

                for er in empresa_regras:
                    
                    # er ta chamando a tabela regra
                    regra = er.regra

                    # a variavel "regra" está chamando a coluna 
                    v_regra = regra.regra

                    v_regras = ValidarRegra(codigo_produto, v_regra)
                    
                    if regra.tipo == 'prefixo':
                       v_regras.validar_prefixo()

                    if regra.tipo == 'caractere':
                       v_regras.validar_caractere()

                    if regra.tipo == 'sufixo':
                       v_regras.validar_sufixo()

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


                cadastro = {
                    "codigo_prod": codigo_produto,
                    "descricao_prod": _norm(parts[3] if len(parts) > 3 else None),
                    "unidade": _norm(parts[6] if len(parts) > 6 else None),
                    "tipo_item": tipo_item,
                    "ncm": _norm(parts[8] if len(parts) > 8 else None),
                    "cod_gen": _norm(parts[10] if len(parts) > 10 else None),
                    "cest": cest,
                    "status": "S/N",
                    "data_inicio_sped": data_inicio_sped,
                    "data_fim_sped": data_fim_sped,
                    "mes_referencia": mes_referencia_arquivo,
                }
                cadastro_itens_sped.append(cadastro.copy())

            elif len(parts) > 1:
                encontrado_k230, offset = self._registro_k(parts, 'K230')

                if encontrado_k230:

                    def get(idx):
                        return parts[idx] if len(parts) > idx else None

                    codigo_item_produzido = get(4 + offset)
                    
                    codigo_produto = codigo_item_produzido

                    v_regras = ValidarRegra(codigo_produto or '', '')

                    for er in empresa_regras:
                        
                        # er ta chamando a tabela regra
                        regra = er.regra

                        # a variavel "regra" está chamando a coluna 
                        v_regra = regra.regra

                        v_regras = ValidarRegra(codigo_produto, v_regra)
                        
                        if regra.tipo == 'prefixo':
                            v_regras.validar_prefixo()

                        if regra.tipo == 'caractere':
                            v_regras.validar_caractere()

                        if regra.tipo == 'sufixo':
                            v_regras.validar_sufixo()

                    codigo_produto = v_regras.codigo_produto

                    data_inicial_op = get(1 + offset)

                    if data_inicial_op:
                        data_inicial_op_ok = datetime.strptime(data_inicial_op, '%d%m%Y').date()
                    else:
                        data_inicial_op_ok = None
                    data_final_op = get(2 + offset)
                    if data_final_op:
                        data_final_op_ok = datetime.strptime(data_final_op, '%d%m%Y').date()
                    else:
                        data_final_op_ok = None

                    data_para_mes = data_final_op_ok or data_inicial_op_ok
                    if data_para_mes:
                        mes_ref = meses_nomes.get(data_para_mes.month, '')
                    else:
                        mes_ref = mes_referencia_arquivo or ''

                    k230 = {
                        'registro': get(0 + offset),
                        'ano_sped': ano_sped,
                        'data_inicial_op': data_inicial_op_ok,
                        'data_final_op': data_final_op_ok,
                        'cod_ordem_prod': get(3 + offset),
                        'codigo_prod': codigo_produto,
                        'qtd_producao_acabada': get(5 + offset),
                        'mes_referencia_k230': mes_ref,
                        'insumos': []
                    }
                    k230_itens_produzidos.append(k230)
                    k230_atual = k230

                encontrado_k235, offset = self._registro_k(parts, 'K235')

                if encontrado_k235:
                    def get(idx):
                        return parts[idx] if len(parts) > idx else None

                    codigo_prod = get(2 + offset)

                    codigo_produto = codigo_prod

                    v_regras = ValidarRegra(codigo_produto or '', '')

                    for er in empresa_regras:
                        
                        # er ta chamando a tabela regra
                        regra = er.regra

                        # a variavel "regra" está chamando a coluna 
                        v_regra = regra.regra

                        v_regras = ValidarRegra(codigo_produto, v_regra)
                        
                        if regra.tipo == 'prefixo':
                            v_regras.validar_prefixo()

                        if regra.tipo == 'caractere':
                            v_regras.validar_caractere()

                        if regra.tipo == 'sufixo':
                            v_regras.validar_sufixo()

                    codigo_produto = v_regras.codigo_produto

                    
                    mes_referencia_235 = None
                    data_final_op = get(1 + offset)

                    if data_final_op:
                        data_final_op_ok = datetime.strptime(data_final_op, '%d%m%Y').date()
                        mes_referencia_235 = meses_nomes.get(data_final_op_ok.month, '')
                    else:
                        data_final_op_ok = None

                    k235 = {
                        'registro': get(0 + offset),
                        'ano_sped': ano_sped,
                        'data_final_op': data_final_op_ok,
                        'quantidade': get(3 + offset),
                        'cod_insumo': codigo_produto,
                        'situacao': None,
                        'mes_referencia_k235': mes_referencia_235,
                        'verificacao_codigo': None
                    }
                    if k230_atual and isinstance(k230_atual, dict):
                        k230_atual['insumos'].append(k235)
                    k235_insumos_usados.append(k235)
        
        k235_lista_plana = []
        for k230 in k230_itens_produzidos:
            for insumo in k230.get('insumos', []):
                k235_lista_plana.append(insumo)
        
        return {
            'cnpj_empresa': cnpj_empresa,
            'k230_itens_produzidos': k230_itens_produzidos,
            'k235_insumos_usados': k235_lista_plana,
            'mes_referencia_arquivo': mes_referencia_arquivo,
            'ano_sped': ano_sped,
            'cadastro_itens_sped': cadastro_itens_sped,
        }


    def extract_values_bloco_k_250_255(self):
        print('extract_values_bloco_k_250_255')
        cadastro_itens_sped = []
        k250_itens_produzidos = []
        k255_insumos_usados = []
        k250_atual = None 
        cnpj_empresa = None
        data_inicio_sped = None
        data_fim_sped = None
        ano_sped = None


        def _norm(value: Optional[str]) -> Optional[str]:
            if value is None:
                return None
            v = str(value).strip()
            return v if v else None

        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        mes_referencia_arquivo = None
        
        for line in self.mes_referencia:
            parts = line.strip().split('|')


            if len(parts) > 1 and parts[1] == '0000':
                cnpj_empresa = parts[7] if len(parts) > 7 else None

                empresa_id = Empresa.objects.filter(
                    cnpj=cnpj_empresa
                ).values_list(
                    'id', 
                    flat=True
                ).first()

                empresa_regras = EmpresaRegra.objects.filter(empresa_id=empresa_id, status=True).select_related('regra')

                mes_ref, data_inicio_sped, data_fim_sped, ano_sped = self._extrair_mes_referencia(parts, meses_nomes)
                mes_referencia_arquivo = mes_ref

            elif len(parts) > 1 and parts[1] == '0200':
                
                cod_prod = _norm(parts[2] if len(parts) > 2 else None)    

                codigo_produto = cod_prod

                v_regras = ValidarRegra(codigo_produto or '', '')
                for er in empresa_regras:
                    
                    regra = er.regra
                    v_regra = regra.regra

                    v_regras = ValidarRegra(codigo_produto, v_regra)
                    
                    if regra.tipo == 'prefixo':
                       v_regras.validar_prefixo()

                    if regra.tipo == 'caractere':
                       v_regras.validar_caractere()

                    if regra.tipo == 'sufixo':
                       v_regras.validar_sufixo()

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


                cadastro = {
                    "codigo_prod": codigo_produto,
                    "descricao_prod": _norm(parts[3] if len(parts) > 3 else None),
                    "unidade": _norm(parts[6] if len(parts) > 6 else None),
                    "tipo_item": tipo_item,
                    "ncm": _norm(parts[8] if len(parts) > 8 else None),
                    "cod_gen": _norm(parts[10] if len(parts) > 10 else None),
                    "cest": cest,
                    "status": "S/N",
                    "data_inicio_sped": data_inicio_sped,
                    "data_fim_sped": data_fim_sped,
                    "mes_referencia": mes_referencia_arquivo,
                }
                cadastro_itens_sped.append(cadastro.copy())

            elif len(parts) > 1:
                encontrado_k250, offset = self._registro_k(parts, 'K250')

                if encontrado_k250:
                    def get(idx):
                        return parts[idx] if len(parts) > idx else None

                    codigo_item_produzido = get(2 + offset)

                    codigo_produto = codigo_item_produzido

                    v_regras = ValidarRegra(codigo_produto or '', '')

                    for er in empresa_regras:
                        
                        # er ta chamando a tabela regra
                        regra = er.regra

                        # a variavel "regra" está chamando a coluna 
                        v_regra = regra.regra

                        v_regras = ValidarRegra(codigo_produto, v_regra)
                        
                        if regra.tipo == 'prefixo':
                            v_regras.validar_prefixo()

                        if regra.tipo == 'caractere':
                            v_regras.validar_caractere()

                        if regra.tipo == 'sufixo':
                            v_regras.validar_sufixo()

                    codigo_produto = v_regras.codigo_produto

                    data_const = get(1 + offset)
                    quantidade = get(3 + offset)

                    mes_const_str = mes_referencia_arquivo or ''
                    data_const_ok = None
                    if data_const:
                        try:
                            data_const_ok = datetime.strptime(data_const, '%d%m%Y').date()
                            mes_const_str = meses_nomes.get(data_const_ok.month, '') or mes_const_str
                        except (ValueError, TypeError):
                            data_const_ok = None
             
                    k250 = {
                        'registro': get(0 + offset),
                        'ano_sped': ano_sped,
                        'data_const': data_const_ok,    
                        'codigo_item': codigo_produto,
                        'cod_item': codigo_produto,
                        'quantidade': quantidade,
                        'mes_const': mes_const_str,
                        'insumos': []
                    }
                    k250_itens_produzidos.append(k250)
                    k250_atual = k250

                encontrado_k255, offset = self._registro_k(parts, 'K255')
                if encontrado_k255:
                        def get(idx):
                            return parts[idx] if len(parts) > idx else None

                        codigo_prod = get(2 + offset)

                        codigo_produto = codigo_prod

                        v_regras = ValidarRegra(codigo_produto or '', '')

                        for er in empresa_regras:
                            
                            # er ta chamando a tabela regra
                            regra = er.regra

                            # a variavel "regra" está chamando a coluna 
                            v_regra = regra.regra

                            v_regras = ValidarRegra(codigo_produto, v_regra)
                            
                            if regra.tipo == 'prefixo':
                                v_regras.validar_prefixo()

                            if regra.tipo == 'caractere':
                                v_regras.validar_caractere()

                            if regra.tipo == 'sufixo':
                                v_regras.validar_sufixo()

                        codigo_produto = v_regras.codigo_produto

                        qtd_perda = get(4 + offset)
                        data_consumo_insumo = get(1 + offset)
                        mes_sped_str = None
                        data_consumo_insumo_ok = None

                        if data_consumo_insumo:
                            try:
                                data_consumo_insumo_ok = datetime.strptime(data_consumo_insumo, '%d%m%Y').date()
                                mes_sped_str = meses_nomes.get(data_consumo_insumo_ok.month, '')
                            except (ValueError, TypeError):
                                data_consumo_insumo_ok = None
                        k255 = {
                            'registro': get(0 + offset),
                            'ano_sped': ano_sped,
                            'data_const': data_consumo_insumo_ok,
                            'codigo_prod': codigo_produto,
                            'quantidade': get(3 + offset),
                            'qtd_perda': qtd_perda,
                            'situacao': None,
                            'mes_consumo_insumo': mes_sped_str,
                        }
                        if k250_atual and isinstance(k250_atual, dict):
                            k250_atual['insumos'].append(k255)
                        k255_insumos_usados.append(k255)

        k255_lista_plana = []
        for k250 in k250_itens_produzidos:
            for insumo in k250.get('insumos', []):
                k255_lista_plana.append(insumo)
        
        return {
            'cnpj_empresa': cnpj_empresa,
            'k250_itens_produzidos': k250_itens_produzidos,
            'k255_insumos_usados': k255_lista_plana,
            'mes_referencia_arquivo': mes_referencia_arquivo,
            'ano_sped': ano_sped,
            'cadastro_itens_sped': cadastro_itens_sped
        }