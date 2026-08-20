# Documentação técnica — SG-ECREDAC

> **Complemento do README.** A visão geral, instalação, rotas atuais e estrutura de pastas estão no `[README.md](../README.md)` na raiz do repositório. Este arquivo aprofunda arquitetura, fluxos e classes.  
> **Versão:** 3.0  
> **Atualizado em:** agosto de 2026

---

## 🎯 ÍNDICE DETALHADO

1. [Visão Geral e Objetivos](#1-visão-geral-e-objetivos)
2. [Arquitetura do Sistema](#2-arquitetura-do-sistema)
3. [Estrutura de Diretórios](#3-estrutura-de-diretórios)
4. [Módulos e Funcionalidades Detalhadas](#4-módulos-e-funcionalidades-detalhadas)
5. [Modelos de Dados Completos](#5-modelos-de-dados-completos)
6. [Processamento de Arquivos - Detalhado](#6-processamento-de-arquivos---detalhado)
7. [Configurações e Requisitos](#7-configurações-e-requisitos)
8. [Rotas e URLs Completas](#8-rotas-e-urls-completas)
9. [Fluxos de Trabalho Detalhados](#9-fluxos-de-trabalho-detalhados)
10. [Classes e Métodos Principais](#10-classes-e-métodos-principais)
11. [Tecnologias e Dependências](#11-tecnologias-e-dependências)
12. [Banco de Dados e Relacionamentos](#12-banco-de-dados-e-relacionamentos)
13. [Processamento SPED - Detalhado](#13-processamento-sped---detalhado)
14. [Processamento XML - Detalhado](#14-processamento-xml---detalhado)
15. [Sistema de Validação](#15-sistema-de-validação)
16. [Interface e JavaScript](#16-interface-e-javascript)
17. [Troubleshooting e Problemas Comuns](#17-troubleshooting-e-problemas-comuns)
18. [Checklist de Manutenção](#18-checklist-de-manutenção)

---



## 1. VISÃO GERAL E OBJETIVOS



### 1.1 O que é o SG-ECREDAC?

O **SG-ECREDAC** (Sistema de Gestão E-CREDAC) é uma aplicação web desenvolvida em **Django 5.2** para gerenciamento, validação e processamento de dados fiscais brasileiros. O sistema foi projetado para:

- Processar arquivos **SPED Fiscal** (Sistema Público de Escrituração Digital)
- Processar arquivos **XML de Notas Fiscais Eletrônicas (NFe)**
- Realizar **validação cruzada** entre dados SPED e XML
- Gerenciar **cadastro de empresas e produtos**
- Processar **planilhas de custo** para rateio
- Gerar **relatórios em Excel** para análise
- Controlar **validações por data** de forma independente



### 1.2 Principais Funcionalidades



#### ✅ Cadastro e Gestão

- **Empresas**: Cadastro manual ou automático via SPED
- **Produtos**: Cadastro manual ou extração do SPED (bloco 0200)
- **Participantes**: Fornecedores e clientes extraídos do SPED (bloco 0150)



#### ✅ Processamento de Arquivos

- **SPED (.txt)**: Extração de participantes, notas fiscais, produtos e impostos
- **XML (NFe)**: Extração completa de dados de notas fiscais eletrônicas
- **Planilhas Excel**: Processamento de planilhas de custo para rateio
- **Bloco K SPED**: Processamento de produção (K230/K235, K250/K255)



#### ✅ Validação e Análise

- **Validação por Data**: Sistema permite validar movimentações por data SPED independentemente
- **Classificação de Produtos**: 
  - `C/N` - Com Nota (produto aparece em nota fiscal)
  - `S/N` - Sem Nota (produto cadastrado mas não aparece em nota)
  - `S/CADASTRO` - Sem Cadastro (produto em nota mas não cadastrado)
- **Status de Notas**:
  - `C/PRODUTO` - Nota com produtos processados
  - `S/PRODUTO` - Nota sem produtos



#### ✅ Edição e Exportação

- **Edição Inline**: Edição direta de dados na tabela
- **Filtros Avançados**: Filtros por múltiplos campos simultaneamente
- **Exportação Excel**: Relatórios completos formatados
- **Paginação**: 100 registros por página com totais



### 1.3 Tecnologias Principais

- **Backend**: Django 5.2 (Python)
- **Banco de Dados**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Bibliotecas**: pandas, openpyxl, xml.etree.ElementTree
- **Interface Admin**: Jazzmin (tema Django Admin)

---



## 2. ARQUITETURA DO SISTEMA



### 2.1 Estrutura de Aplicações Django

O sistema é composto por **10 aplicações Django** e pelo módulo `regras_jobs` (lógica de regras de código, sem `apps.py`).

#### Aplicações

1. `accounts` — Login (`CustomLoginView`) e redirecionamento para home ou admin.
2. `cadastro` — Empresas (`Empresa`), regras (`Regra`, `EmpresaRegra`) e produtos do SPED (`Cadastro_itens_sped`). Extração em `cadastro/utils/extract_sped.py`.
3. `validacao` — Processamento SPED/XML/DUE e outros modelos.
  - **Modelos:** `Participantes`, `Notas_participantes`, `Produtos_notas`, `ValidacaoStatus`, `ValidacaoDataConcluida`, registros C500/C590, D100/D190, D500/D590.
  - **Catálogo 0200:** `cadastro.models.produtos.Cadastro_itens_sped` (saiu desta app).
  - **Parsers:** `validacao/parser/nfe/extract_sped.py` (`SPEDProcesses`), `extract_xml.py`, `extract_planilhaDue.py`; `validacao/parser/outros_modelos/`.
  - **Serviços:** `validacao/services/nfe/` e `validacao/services/outros_modelos/`.
  - **Normalização:** `validacao/utils/normalizadores.py`.
4. `metodo_rateio` — Planilha de custo e Bloco K (K230/K235, K250/K255). Parser em `metodo_rateio/utils/extract_blocok.py`.
5. `gerar_arquivo` — Montagem do arquivo texto E-CREDAC (`gerar_arquivo/services/gerar_arquivo.py`).
6. `gerar_fichas` — Fichas 1 a 6 (insumos, produção, estoques, rateios, demonstrativos, crédito acumulado).
7. `historico` — Auditoria campo a campo das alterações nas telas.
8. `home` — Dashboard e modelo `Permissions` (controle de menu por usuário).
9. `help` — Página de ajuda.
10. `pendencias` — Tela de pendências do processo.



### 2.2 Banco de Dados



#### Configuração PostgreSQL

Credenciais vêm do arquivo `.env` (veja o README). Nunca versionar senha no código nem nesta documentação.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```



#### Características

- **SGBD**: PostgreSQL
- **Encoding**: UTF-8
- **Timezone**: America/Sao_Paulo (`TIME_ZONE` em `project/settings.py`)



### 2.3 Estrutura de Pastas do Projeto

```
RNV_ECREDAC/
├── accounts/                 # Login e redirecionamento
├── cadastro/                 # Empresas, produtos e regras de código
├── validacao/                # Upload, parse e validação fiscal
├── metodo_rateio/            # Bloco K (SPED) e planilha de custo
├── gerar_arquivo/            # Montagem do arquivo E-CREDAC
├── gerar_fichas/             # Fichas 1 a 6 de controle de custos
├── historico/                # Auditoria de alterações nas telas
├── home/                     # Dashboard e permissões por usuário
├── help/                     # Página de ajuda
├── pendencias/               # Tela de pendências
├── regras_jobs/              # Lógica de validação de regras de código (não é app Django)
├── project/                  # settings, urls, wsgi, asgi
├── templates/                # Templates globais (base.html fica em home/)
├── static/                   # CSS, JS e imagens globais
├── docs/                     # Manuais e relatórios técnicos
├── logs/                     # django.log
├── manage.py
├── requirements.txt
└── .env                      # credenciais locais (não versionar)

---



## 📦 MÓDULOS E FUNCIONALIDADES



### 1. **ACCOUNTS** - Autenticação



#### Funcionalidades:

- Login personalizado com redirecionamento
- Suporte para acesso admin e usuário comum
- Integração com Django Admin e a Biblioteca(Jazzmin)



#### Arquivos Principais:

- `views.py`: `CustomLoginView` - View de login personalizada
- `templates/login.html`: Template de login



#### Rotas:

- `/login/` - Página de login
- `/logout/` - Logout do sistema
- `/admin/` - Painel administrativo Django



### 2. **CADASTRO** - Cadastro de Empresas e Produtos



#### Funcionalidades:



##### **Empresas:**

- Cadastro manual de empresas
- Cadastro automático via arquivo SPED
- Listagem, edição e exclusão de empresas
- Campos: Razão Social, CNPJ, Inscrição Estadual, UF, Endereço, Telefone, Email, Método de Rateio



##### **Produtos:**

- Cadastro manual de produtos
- Listagem de produtos do SPED
- Listagem de produtos cadastrados manualmente
- Edição e exclusão de produtos
- Campos: Código, Descrição, NCM, CEST, Unidade, Tipo, Gênero, Saldos Iniciais



#### Modelos: ( Tabelas )

`Empresa`:

```python
- razao_social (CharField)
- cnpj (CharField)
- inscricao_estadual (CharField)
- uf (CharField)
- indicador_atividade (CharField)
- configuracao (CharField)
- codigo_municipio (CharField)
- nome_fantasia (CharField)
- cep, endereco, numero_endereco, bairro (CharField)
- telefone (CharField)
- metodo_rateio (CharField)
- email (EmailField)
```

`Produtos` (Cadastro):

```python
- empresa (CharField)
- codigo_prod (CharField)
- descricao_prod (CharField)
- unidade (CharField)
- tipo_produto (CharField)
- genero (CharField)
- ncm (CharField)
- descricao_complementar (CharField)
- codigo_cest (CharField)
- saldo_inicial_prod (DecimalField)
- saldo_inicial_icms (DecimalField)
```



#### Rotas:

- `/cadastro/lista_empresas/` - Lista de empresas
- `/cadastro/nova/` - Adicionar empresa manualmente
- `/cadastro/empresa/cadastrar_empresa/` - Cadastrar via SPED
- `/cadastro/empresa/editar/<id>/` - Editar empresa
- `/cadastro/empresa/excluir/<id>/` - Excluir empresa
- `/cadastro/lista_produtosSped/` - Lista produtos do SPED
- `/cadastro/lista_produtosManual/` - Lista produtos cadastrados
- `/cadastro/produto/cadastro_produtos/` - Cadastrar produto
- `/cadastro/produto/editar/<id>/` - Editar produto
- `/cadastro/produto/excluir/<id>/` - Excluir produto



#### Processamento SPED de Cadastro:

- Classe `SPEDcadastro` em `cadastro/utils.py`
- Extrai dados do bloco `0000` (dados da empresa)
- Extrai dados do bloco `0005` (dados complementares)

---



### 3. **VALIDAÇÃO** - Processamento e Validação de Dados



#### Funcionalidades:



##### **Upload de Movimentações:**

- Upload de arquivo SPED (.txt)
- Upload de múltiplos arquivos XML (até 1000 arquivos)
- Upload de pasta completa com XMLs
- Processamento em lote
- Validação de tipos e tamanhos de arquivo
- **Interface Melhorada:**
  - Card XML aparece automaticamente ao selecionar arquivos XML
  - Card XML aparece quando SPED é selecionado
  - Exibição dinâmica de informações de arquivos selecionados
  - Botão de processar aparece automaticamente quando SPED e XML estão selecionados
  - Suporte a drag-and-drop para arquivos e pastas
  - Feedback visual durante o processamento
  - Verificação inicial ao carregar a página para arquivos já selecionados



##### **Processamento SPED:**

- Extração de participantes (bloco 0150)
- Extração de notas fiscais (bloco C100)
- Extração de produtos (bloco C170 e 0200)
- Classificação de produtos:
  - `C/N` - Com Nota
  - `S/N` - Sem Nota
  - `S/CADASTRO` - Sem Cadastro
- Rateio de valores (frete, seguro, despesas acessórias)



##### **Processamento XML:**

- Extração de dados de notas fiscais eletrônicas (NFe)
- Extração de produtos por item
- Cálculo de impostos (ICMS, IPI, ST)
- Rateio de valores totais da nota entre itens
- Correspondência com notas do SPED



##### **Visualização e Edição:**

- Tabela interativa com dados de movimentações
- Filtros avançados por múltiplos campos
- Edição inline de dados
- Paginação (100 registros por página)
- Totais por página (valor_total, IPI, ICMS)



##### **Validação de Dados:**

- Listagem de movimentações por empresa e data
- Status de validação (Pendente, Em Andamento, Concluído)
- Finalização de movimentações por data
- Limpeza de dados concluídos
- **Sistema de Validação por Data:**
  - Validação independente por data SPED
  - Múltiplas validações simultâneas para diferentes períodos
  - Finalização seletiva por data de referência
  - Separação entre validações concluídas e em andamento
  - Controle de progresso por empresa e data



##### **Exportação:**

- Exportação para Excel (.xlsx)
- Relatório completo de movimentações
- Formatação automática de colunas



#### Modelos:

`Participantes`:

```python
- empresa (ForeignKey -> Empresa)
- data_sped (DateField)
- cod_part (CharField)
- nome (CharField)
- cnpj_cpf (CharField)
- ie (CharField)
- endereco, numero, complemento, bairro (CharField)
```

`Notas`:

```python
- empresa (ForeignKey -> Empresa)
- tipo (CharField) - 'Entrada' ou 'Saida'
- data_sped (DateField)
- cod_part (CharField)
- numero_nota (CharField)
- codigo_uf (CharField)
- numero_id_nota (CharField)
- status (CharField) - 'S/PRODUTO', 'C/PRODUTO'
```

`Produtos` (Validação):

```python
- empresa (ForeignKey -> Empresa)
- tipo_nota (CharField)
- cod_part (CharField)
- numero_nota (CharField)
- data_sped (DateField)
- codigo_prod (CharField)
- descricao_prod (TextField)
- unidade (CharField)
- quantidade_prod (DecimalField)
- valor_unitario (DecimalField)
- valor_total (DecimalField)
- cfop_prod (CharField)
- ncm (CharField)
- cest (CharField)
- cst (CharField)
- aliquota_icms (DecimalField)
- base_icms (DecimalField)
- valor_ipi (DecimalField)
- valor_pis (DecimalField)
- valor_icms (DecimalField)
- tipo_item (CharField)
- status (CharField) - 'C/N', 'S/N', 'S/CADASTRO'
```

`ValidacaoStatus`:

```python
- empresa (ForeignKey -> Empresa)
- status (CharField) - 'pendente', 'em_andamento', 'concluido'
- progresso (PositiveIntegerField) - 0 a 100
- data_inicio (DateTimeField)
- data_atualizacao (DateTimeField)
- data_arquivo (DateField)
```

`ValidacaoDataConcluida`:

```python
- empresa (ForeignKey -> Empresa)
- data_sped (DateField)
- criado_em (DateTimeField)
- unique_together: (empresa, data_sped)
```

`Cadastro_itens_sped`:

```python
- empresa (ForeignKey -> Empresa)
- mes_referencia (CharField)
- data_inicio_sped (DateField)
- data_fim_sped (DateField)
- codigo_prod (CharField)
- descricao_prod (CharField)
- unidade (CharField)
- tipo_item (CharField)
- ncm (CharField)
- cest (CharField)
```



#### Rotas:

- `/validacao/upload_movimentacoes/` - Upload de arquivos
- `/validacao/processar_arquivos/` - Processar arquivos enviados
- `/validacao/movimentacoes/` - Visualizar dados
- `/validacao/validacao_dados/` - Lista de validações
- `/validacao/finalizar_movimentacao/` - Finalizar movimentação
- `/validacao/validacao/salvar_edicoes` - Salvar edições inline
- `/validacao/atualizar_progresso/` - Atualizar progresso (API)
- `/validacao/exportar-sped/` - Exportar relatório Excel



#### Classes de Processamento:

`SPEDProcesses` (`validacao/utils.py`):

- `load_sped_file()`: Carrega arquivo SPED
- `extract_values_sped()`: Extrai dados do SPED
  - Processa blocos: 0000, 0150, 0200, C100, C170
  - Classifica produtos
  - Calcula rateios

`XMLProcesses` (`validacao/utils.py`):

- `load_xml()`: Carrega arquivo XML
- `extract_generic_values()`: Extrai valores via XPath
- `process_xml_file()`: Processa NFe completa
  - Extrai dados da nota
  - Extrai itens (produtos)
  - Calcula impostos por item
  - Rateia valores totais

`Normalizadores` (`validacao/utils.py`):

- `normalizador_decimal()`: Converte strings numéricas para float
  - Suporta formatos: "2000,00" → 2000.0
  - Trata valores nulos/vazios



#### Arquivos JavaScript:

`upload_movimentacoes.js` (`validacao/static/js/`):

- Gerenciamento de interface de upload
- Controle de visibilidade de cards (SPED e XML)
- Função `updateProcessButton()`: Controla exibição do botão de processar
- Função `setupDropZone()`: Configura drag-and-drop
- Event listeners para inputs de arquivo
- Verificação inicial ao carregar página
- Tratamento de eventos de mudança de arquivos

---



### 4. **MÉTODO RATEIO** - Processamento de Planilhas de Custo



#### Funcionalidades:



##### **Upload de Planilha:**

- Upload de planilha Excel (.xlsx)
- Processamento de dados de custo
- Associação com empresa e data de referência



##### **Análise de Planilha:**

- Visualização de dados processados
- Agrupamento por categoria e descrição
- Cálculo de totais (valor_total, valor_alocado, ICMS passível de crédito)
- Filtros por categoria (ex: Serviço)



#### Modelo:

`PlanilhaCusto`:

```python
- empresa (CharField)
- data_referencia (DateField)
- categoria (CharField)
- centro_custo (CharField)
- descricao (TextField)
- documento_fiscal (CharField)
- fornecedor (CharField)
- conta_contabil (CharField)
- valor_total (DecimalField)
- percentual_aplicado (DecimalField)
- valor_alocado (DecimalField)
- icms_passivel_credito (DecimalField)
```



#### Rotas:

- `/rateio/tela_menu/` - Menu de rateio
- `/rateio/processamento_planilha/` - Processar planilha
- `/rateio/view_analisePlanilha/` - Visualizar análise



#### Classes:

`extractPlanilhaCusto` (`metodo_rateio/utils.py`):

- `load_planilha_custo()`: Carrega arquivo Excel
- `extract_values_planilha()`: Extrai dados da planilha
  - Lê a partir da linha 2
  - Extrai colunas: categoria, centro_custo, descricao, etc.

---



### 5. **CONVERSÃO** - Geração de Arquivos



#### Funcionalidades:

- Geração de arquivos E-CREDAC
- Upload de arquivos XML e TXT
- Seleção de empresa e mês de referência



#### Modelos:

- `Empresa` (gerar_arquivo)
- `NotaFiscal`
- `ItemNotaFiscal`
- `MetodoRateio`



#### Rotas:

- `/gerarArquivo/` - Gerar arquivo E-CREDAC

---



### 6. **HISTÓRICO** - Histórico de Operações



#### Funcionalidades:

- Visualização de histórico de operações do sistema



#### Rotas:

- `/historico/` - Página de histórico

---



### 7. **HOME** - Dashboard



#### Funcionalidades:

- Página inicial do sistema
- Dashboard com métricas
- Menu de navegação



#### Rotas:

- `/home/` - Página inicial

---



## 💾 MODELOS DE DADOS



### Relacionamentos:

```
Empresa (cadastro)
├── Participantes (validacao) - ForeignKey
├── Notas (validacao) - ForeignKey
├── Produtos (validacao) - ForeignKey
├── ValidacaoStatus (validacao) - ForeignKey
└── ValidacaoDataConcluida (validacao) - ForeignKey
```



### Estrutura de Dados SPED:

```
SPED (.txt)
├── Bloco 0000: Dados da Empresa
├── Bloco 0005: Dados Complementares
├── Bloco 0150: Participantes
├── Bloco 0200: Cadastro de Produtos
├── Bloco C100: Notas Fiscais
└── Bloco C170: Itens das Notas
```



### Estrutura de Dados XML:

```
NFe (XML)
├── infNFe
│   ├── ide: Dados da Nota
│   ├── emit: Emitente
│   ├── dest: Destinatário
│   ├── det: Itens (produtos)
│   └── total: Totais (ICMSTot)
└── protNFe: Protocolo
```

---



## 13. PROCESSAMENTO SPED - DETALHADO



### 13.1 Classe SPEDProcesses

**Localização**: `validacao/utils/extract_sped.py`

**Métodos Principais**:

```python
class SPEDProcesses:
    def __init__(self, sped_file)
    def load_sped_file(self) -> bool
    def extract_values_sped(self) -> Dict[str, Any]
```



### 13.2 Fluxo Completo de Processamento



#### Passo 1: Carregamento do Arquivo

```python
def load_sped_file(self) -> bool:
    # Lê arquivo linha por linha
    # Decodifica em UTF-8 com tratamento de erros
    # Armazena em self.mes_referencia (lista de strings)
```



#### Passo 2: Extração de Dados

O método `extract_values_sped()` processa linha por linha, identificando blocos pelo código na posição `parts[1]`:

```python
for line in self.mes_referencia:
    parts = line.strip().split('|')
    bloco = parts[1]  # Código do bloco
```



### 13.3 Blocos Processados - Detalhamento Completo



#### **Bloco 0000 - Dados da Empresa**

**Formato da linha**: `|0000|...|CNPJ|...|DATA_INICIO|DATA_FIM|...|`

**Campos Extraídos**:

- `parts[7]` → CNPJ da empresa
- `parts[4]` → Data início (formato: DDMMYYYY)
- `parts[5]` → Data fim (formato: DDMMYYYY)
- `parts[6]` → Razão Social

**Processamento**:

```python
if parts[1] == '0000':
    cnpj_empresa = parts[7]
    data_inicio_str = parts[4]  # Ex: "01012024"
    data_inicio_sped = datetime.strptime(data_inicio_str, '%d%m%Y').date()
    
    # Extração do mês de referência
    mes_numero = int(data_inicio_str[2:4])  # Extrai MM
    meses_map = {
        '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março',
        '04': 'Abril', '05': 'Maio', '06': 'Junho',
        '07': 'Julho', '08': 'Agosto', '09': 'Setembro',
        '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
    }
    mes_referencia = meses_map.get(data_inicio_str[2:4])
```

**Dados Armazenados**:

- `cnpj_empresa`: Lista com dict contendo CNPJ
- `data_inicio_sped`: Objeto date
- `data_fim_sped`: Objeto date
- `mes_referencia`: String com nome do mês

---



#### **Bloco 0150 - Participantes (Fornecedores/Clientes)**

**Formato da linha**: `|0150|COD_PART|NOME|COD_PAIS|CNPJ_CPF|IE|COD_MUN|...|END|NUM|COMPL|BAIRRO|...|`

**Campos Extraídos**:

- `parts[2]` → Código do participante (`cod_part`)
- `parts[3]` → Nome
- `parts[5]` → CNPJ/CPF
- `parts[6]` → Inscrição Estadual (IE)
- `parts[10]` → Endereço
- `parts[11]` → Número
- `parts[12]` → Complemento
- `parts[13]` → Bairro

**Estrutura de Dados**:

```python
participante = {
    'cod_part': parts[2],
    'mes_referencia': mes_referencia,  # Do bloco 0000
    'data_inicio_sped': data_inicio_sped_ok,
    'data_fim_sped': data_fim_sped_ok,
    'nome': parts[3],
    'cnpj_cpf': parts[5],
    'ie': parts[6],
    'endereco': parts[10],
    'numero': parts[11],
    'complemento': parts[12],
    'bairro': parts[13],
    'notas': []  # Lista de notas deste participante
}
```

**Armazenamento**:

- Usa `participantes_map` (dict) para evitar duplicatas por `cod_part`
- Cada participante mantém lista de notas (`notas: []`)

---



#### **Bloco 0200 - Cadastro de Produtos**

**Formato da linha**: `|0200|COD_ITEM|DESCR_ITEM|COD_BARRA|COD_ANT_ITEM|UNID|TIPO_ITEM|NCM|...|CEST|...|`

**Campos Extraídos**:

- `parts[2]` → Código do produto (`codigo_prod`)
- `parts[3]` → Descrição
- `parts[6]` → Unidade (UN, KG, etc.)
- `parts[7]` → Tipo de item (01-09)
- `parts[8]` → NCM
- `parts[13]` → CEST

**Mapeamento de Tipo de Item**:

```python
tipo_item_map = {
    '01': "Mercadoria para revenda",
    '02': "Matéria prima",
    '03': "Produto em elaboração",
    '04': "Produto acabado",
    '05': "Subproduto",
    '06': "Produto intermediário",
    '07': "Material de uso e consumo",
    '08': "Ativo imobilizado",
    '09': "Serviço"
}
```

**Estrutura de Dados**:

```python
catalogo_produtos[cod_prod] = {
    'codigo_prod': cod_prod,
    'descricao_prod': parts[3],
    'unidade': parts[6],
    'tipo_item': tipo_item_map.get(parts[7], 'Outros'),
    'ncm': parts[8],
    'cest': parts[13],
    'status': 'S/N',  # Inicialmente "Sem Nota"
    'data_inicio_sped': data_inicio_sped_ok,
    'data_fim_sped': data_fim_sped_ok,
    'mes_referencia': mes_referencia
}
```

**Importante**: 

- Produtos do bloco 0200 começam com status `'S/N'` (Sem Nota)
- Status muda para `'C/N'` (Com Nota) quando aparecem no bloco C170
- Produtos do 0200 são salvos em `Cadastro_itens_sped`

---



#### **Bloco C100 - Nota Fiscal**

**Formato da linha**: `|C100|IND_OPER|IND_EMIT|COD_PART|COD_MOD|COD_SIT|SER|NUM_DOC|DT_DOC|DT_E_S|VL_DOC|...|VL_FRT|VL_SEG|VL_DA|...|COD_UF|...|`

**Campos Extraídos**:

- `parts[2]` → Indicador de operação (0=Entrada, 1=Saída)
- `parts[4]` → Código do participante (`cod_part`)
- `parts[8]` → Número da nota (`numero_nota`)
- `parts[9]` → Número ID da nota (chave de acesso sem prefixo)
- `parts[9][:2]` → Código UF (primeiros 2 dígitos)
- `parts[17]` → Valor do frete
- `parts[18]` → Valor do seguro
- `parts[19]` → Despesas acessórias

**Mapeamento de Tipo**:

```python
tipo = {'0': 'Entrada', '1': 'Saida'}
tipo_nota = tipo.get(parts[2], 'Desconhecido')
```

**Mapeamento de UF**:

```python
uf_map = {
    '12': 'AC', '27': 'AL', '13': 'AM', '16': 'AP', '29': 'BA',
    '23': 'CE', '53': 'DF', '32': 'ES', '52': 'GO', '21': 'MA',
    '31': 'MG', '50': 'MS', '51': 'MT', '15': 'PA', '25': 'PB',
    '26': 'PE', '22': 'PI', '41': 'PR', '33': 'RJ', '24': 'RN',
    '43': 'RS', '11': 'RO', '14': 'RR', '42': 'SC', '28': 'SE',
    '35': 'SP', '17': 'TO'
}
codigo_uf = parts[9][:2] if len(parts) > 9 else None
estado = uf_map.get(codigo_uf, 'Sem informação')
```

**Normalização de Valores**:

```python
valor_frete = Normalizadores.normalizador_decimal(parts[17])
valor_seguro = Normalizadores.normalizador_decimal(parts[18])
despesa_acessoria = Normalizadores.normalizador_decimal(parts[19])
```

**Estrutura de Dados**:

```python
nota_atual = {
    'tipo': tipo_nota,  # 'Entrada' ou 'Saida'
    'numero_nota': numero_nota_atual,
    'codigo_uf': estado,  # Sigla do estado
    'numero_id_nota': parts[9],
    'status': 'S/PRODUTO',  # Inicialmente sem produtos
    'produtos': [],  # Lista de produtos da nota
    'produtos_da_nota': [],  # Lista temporária durante processamento
    'second_value_total': 0,  # Acumula frete+seguro+despesas
    'valor_frete': valor_frete,
    'valor_seguro': valor_seguro,
    'despesa_acessoria': despesa_acessoria
}
```

**Vinculação com Participante**:

```python
if cod_part_c100 in participantes_map:
    participantes_map[cod_part_c100]['notas'].append(nota_atual)
```

---



#### **Bloco C170 - Itens da Nota (Produtos)**

**Formato da linha**: `|C170|NUM_ITEM|COD_ITEM|DESCR_COMPL|QTD|UNID|VL_ITEM|VL_DESC|CFOP|CST_ICMS|...|VL_BC_ICMS|ALIQ_ICMS|VL_ICMS|...|VL_ST|...|VL_IPI|...|`

**Campos Extraídos**:

- `parts[3]` → Código do produto (`codigo_prod`)
- `parts[4]` → Descrição complementar
- `parts[5]` → Quantidade
- `parts[6]` → Unidade
- `parts[7]` → Valor do produto
- `parts[8]` → Valor do desconto
- `parts[10]` → CST (Código de Situação Tributária)
- `parts[11]` → CFOP
- `parts[13]` → Base de cálculo do ICMS
- `parts[14]` → Alíquota do ICMS
- `parts[15]` → Valor do ICMS
- `parts[18]` → Valor da ST (Substituição Tributária)
- `parts[24]` → Valor do IPI
- `parts[37]` → NCM (se não estiver no catálogo)

**Classificação do Produto**:

```python
cod_prod = parts[3]

if cod_prod in catalogo_produtos:
    # Produto está cadastrado no bloco 0200
    catalogo_produtos[cod_prod]['status'] = 'C/N'  # Com Nota
    produto_info = catalogo_produtos[cod_prod].copy()
else:
    # Produto não está cadastrado
    produto_info = {
        'codigo_prod': cod_prod,
        'descricao_prod': parts[4],
        'unidade': parts[6],
        'ncm': parts[37],
        'status': 'S/CADASTRO'  # Sem Cadastro
    }
```

**Cálculo de Impostos do Item**:

```python
valor_prod = Normalizadores.normalizador_decimal(parts[7])
valor_desconto = Normalizadores.normalizador_decimal(parts[8])
valor_st = Normalizadores.normalizador_decimal(parts[18])
valor_ipi = Normalizadores.normalizador_decimal(parts[24])
valor_icms = Normalizadores.normalizador_decimal(parts[15])

# Imposto do item = IPI + ST - Desconto
valor_imposto_item = valor_ipi + valor_st - valor_desconto
```

**Atualização do Status da Nota**:

```python
nota_atual['status'] = 'C/PRODUTO'  # Nota agora tem produtos
```

**Cálculo de Valor Unitário**:

```python
qtd = Normalizadores.normalizador_decimal(parts[5])
valor_unitario = round(valor_prod / qtd, 2) if qtd else 0
```

---



### 13.4 Rateio de Valores - Algoritmo Detalhado



#### **Cálculo do Valor para Rateio**

Para cada nota fiscal, após processar todos os itens (C170):

```python
# Soma todos os valores a ratear da nota
valor_total_nota = valor_frete + valor_seguro + despesa_acessoria
n = len(produtos)  # Quantidade de itens na nota

if n == 0:
    continue  # Pula se não houver produtos

valor_para_rateio = valor_total_nota / n
```



#### **Distribuição Igualitária com Tratamento de Arredondamento**

**Problema**: Divisão pode resultar em valores com muitas casas decimais.

**Solução**: Distribui igualmente, mas o último item recebe o restante para evitar diferenças de arredondamento:

```python
if valor_para_rateio == 0:
    # Sem valores para ratear
    for prod_info, valor_prod in produtos:
        prod_info['valor_rateado'] = 0
        valor_total = valor_prod + imposto
        prod_info['valor_total'] = round(valor_total, 2)
else:
    # Com valores para ratear
    base_share = round(valor_para_rateio / n, 2)  # Valor base por item
    acumulado = 0.0
    
    for i, (prod_info, valor_prod) in enumerate(produtos):
        if i < n - 1:
            # Itens anteriores: recebem valor base
            valor_rateado = base_share
            acumulado += valor_rateado
        else:
            # Último item: recebe o restante
            valor_rateado = round(valor_para_rateio - acumulado, 2)
        
        prod_info['valor_rateado'] = valor_rateado
        valor_prod_decimal = Normalizadores.normalizador_decimal(valor_prod)
        imposto = Normalizadores.normalizador_decimal(prod_info.get('valor_imposto', 0))
        
        # Valor total = Valor produto + Valor rateado + Impostos
        total_calculado = valor_prod_decimal + valor_rateado + imposto
        prod_info['valor_total'] = round(total_calculado, 2)
```

**Exemplo Prático**:

```
Nota com 3 itens:
- Frete: R$ 300,00
- Seguro: R$ 150,00
- Despesas: R$ 50,00
Total para ratear: R$ 500,00

Divisão: R$ 500,00 / 3 = R$ 166,6666...

Distribuição:
- Item 1: R$ 166,66 (base_share)
- Item 2: R$ 166,66 (base_share)
- Item 3: R$ 500,00 - (166,66 + 166,66) = R$ 166,68 (restante)

Total: R$ 166,66 + R$ 166,66 + R$ 166,68 = R$ 500,00 ✓
```

---



### 13.5 Persistência no Banco de Dados

Após processar o SPED, os dados são salvos em:

1. `Participantes`: Um registro por participante único (`cod_part` + `empresa`)
2. `Notas_participantes`: Um registro por nota
3. `Produtos_notas`: Um registro por produto de cada nota
4. `Cadastro_itens_sped`: Um registro por produto do bloco 0200

**Código de Persistência** (em `validacao/views.py`):

```python
# Participantes
for part in dados_sped.get('participantes', []):
    participante_obj, _ = Participantes.objects.get_or_create(
        cod_part=part.get('cod_part'),
        empresa=empresa_obj,
        defaults={...}
    )
    
    # Notas
    for nota in part.get('notas', []):
        nota_obj = Notas_participantes.objects.create(...)
        
        # Produtos
        for prod in nota.get('produtos', []):
            Produtos_notas.objects.create(...)

# Cadastro de itens SPED
for itens in dados_sped.get('cadastro_itens_sped', []):
    Cadastro_itens_sped.objects.create(...)
```



## 14. PROCESSAMENTO XML - DETALHADO



### 14.1 Classe XMLProcesses

**Localização**: `validacao/utils/extract_xml.py`

**Métodos Principais**:

```python
class XMLProcesses:
    def __init__(self, xml_file_path: str)
    def load_xml(self) -> bool
    def extract_generic_values(self, xpath_expressions: Dict[str, str]) -> Dict[str, Any]

def process_xml_file(file_path: str, extraction_type: str = 'nfe') -> Dict[str, Any]
```



### 14.2 Namespace XML

**Importante**: NFe usa namespace específico que deve ser declarado:

```python
self.ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}
```

**Uso em XPath**:

```python
# Sem namespace (errado)
numero_nota = root.find('.//nNF')

# Com namespace (correto)
numero_nota = root.find('.//ns:nNF', self.ns)
```



### 14.3 Estrutura de uma NFe XML

```
<NFe>
  <infNFe Id="NFe35241234567890123456789012345678901234567890">
    <ide>
      <nNF>123456</nNF>  <!-- Número da nota -->
      <dhEmi>2024-01-15T10:30:00-03:00</dhEmi>
    </ide>
    <emit>
      <!-- Dados do emitente -->
    </emit>
    <dest>
      <!-- Dados do destinatário -->
    </dest>
    <det nItem="1">
      <prod>
        <cProd>001</cProd>  <!-- Código do produto -->
        <xProd>Produto Exemplo</xProd>  <!-- Descrição -->
        <NCM>12345678</NCM>
        <CFOP>5102</CFOP>
        <uCom>UN</uCom>  <!-- Unidade -->
        <qCom>10.0000</qCom>  <!-- Quantidade -->
        <vProd>1000.00</vProd>  <!-- Valor do produto -->
      </prod>
      <imposto>
        <ICMS>
          <ICMS00>
            <orig>0</orig>
            <CST>000</CST>
            <vBC>1000.00</vBC>  <!-- Base de cálculo ICMS -->
            <pICMS>18.00</pICMS>  <!-- Alíquota ICMS -->
            <vICMS>180.00</vICMS>  <!-- Valor ICMS -->
            <vICMSST>0.00</vICMSST>  <!-- Valor ST -->
          </ICMS00>
        </ICMS>
        <IPI>
          <IPITrib>
            <vIPI>50.00</vIPI>  <!-- Valor IPI -->
          </IPITrib>
        </IPI>
      </imposto>
    </det>
    <total>
      <ICMSTot>
        <vFrete>100.00</vFrete>  <!-- Frete total -->
        <vSeg>50.00</vSeg>  <!-- Seguro total -->
        <vOutro>25.00</vOutro>  <!-- Outros valores -->
        <vDesc>10.00</vDesc>  <!-- Desconto total -->
      </ICMSTot>
    </total>
    <infProt>
      <chNFe>35241234567890123456789012345678901234567890</chNFe>
    </infProt>
  </infNFe>
</NFe>
```



### 14.4 Fluxo Completo de Processamento



#### Passo 1: Carregamento do XML

```python
def load_xml(self) -> bool:
    try:
        self.tree = ET.parse(self.xml_file_path)
        self.root = self.tree.getroot()
        return True
    except ET.ParseError as e:
        logger.error(f"Erro de parsing XML: {e}")
        return False
```



#### Passo 2: Processamento da NFe

A função `process_xml_file()` processa cada `infNFe` encontrado no arquivo:

```python
# Suporta múltiplas notas por arquivo
infs = processor.root.findall('.//ns:infNFe', processor.ns)

for inf in infs:
    # Processa cada nota
    ...
```



### 14.5 Extração de Dados da Nota



#### Dados Básicos da Nota

```python
# Número da nota
numero_nota = inf.findtext('.//ns:ide/ns:nNF', default='', namespaces=processor.ns).strip()

# ID da nota (chave de acesso sem prefixo "NFe")
numero_id = inf.get('Id') or inf.get('id') or ''
numero_id_formatado = numero_id[3:]  # Remove "NFe" do início

# Chave de acesso completa
chave_nota = inf.findtext('.//ns:protNFe/ns:chNFe', default='', namespaces=processor.ns).strip()
```



#### Totais da Nota (para Rateio)

```python
# Valores totais da nota (ICMSTot)
valor_frete_xml = Normalizadores.normalizador_decimal(
    inf.findtext('.//ns:ICMSTot/ns:vFrete', default='', namespaces=processor.ns) or 0
)
valor_seguro_xml = Normalizadores.normalizador_decimal(
    inf.findtext('.//ns:ICMSTot/ns:vSeg', default='', namespaces=processor.ns) or 0
)
valor_outros_xml = Normalizadores.normalizador_decimal(
    inf.findtext('.//ns:ICMSTot/ns:vOutro', default='', namespaces=processor.ns) or 0
)
valor_desconto_xml = Normalizadores.normalizador_decimal(
    inf.findtext('.//ns:ICMSTot/ns:vDesc', default='', namespaces=processor.ns) or 0
)
```

**Cálculo do Valor para Rateio**:

```python
valor_para_rateio = valor_frete_xml + valor_seguro_xml + valor_outros_xml - valor_desconto_xml
```



### 14.6 Extração de Dados dos Itens (Produtos)



#### Estrutura de um Item (det)

Cada item é um elemento `<det>` dentro de `<infNFe>`:

```python
dets = inf.findall('.//ns:det', processor.ns)

for det in dets:
    # Extrai dados de cada item
    ...
```



#### Dados do Produto

```python
# Código e descrição
codigo_prod = det.findtext('.//ns:prod/ns:cProd', default='', namespaces=processor.ns).strip()
descricao_prod = det.findtext('.//ns:prod/ns:xProd', default='', namespaces=processor.ns).strip()

# Quantidade e valores
qtd_text = det.findtext('.//ns:prod/ns:qCom', default='', namespaces=processor.ns).strip()
vprod_text = det.findtext('.//ns:prod/ns:vProd', default='', namespaces=processor.ns).strip()

qtd_prod = Normalizadores.normalizador_decimal(qtd_text)
valor_prod = Normalizadores.normalizador_decimal(vprod_text)

# Valor unitário
valor_unitario = round(valor_prod / qtd_prod, 2) if qtd_prod else 0

# NCM, CFOP, CEST
ncm = det.findtext('.//ns:prod/ns:NCM', default='', namespaces=processor.ns).strip()
cfop = det.findtext('.//ns:prod/ns:CFOP', default='', namespaces=processor.ns).strip()
cest = det.findtext('.//ns:prod/ns:CEST', default='', namespaces=processor.ns).strip()
```



#### Impostos por Item

**ICMS**:

```python
# Base de cálculo e alíquota
base_icms = det.findtext('.//ns:ICMS/*/ns:vBC', default='', namespaces=processor.ns).strip()
aliquota_icms = det.findtext('.//ns:ICMS/*/ns:pICMS', default='', namespaces=processor.ns).strip()
valor_icms = det.findtext('.//ns:ICMS/*/ns:vICMS', default='', namespaces=processor.ns).strip()

# Substituição Tributária (ST)
valor_st_item = Normalizadores.normalizador_decimal(
    det.findtext('.//ns:ICMS/*/ns:vICMSST', default='', namespaces=processor.ns) or 0
)

# Origem e CST
orig = det.findtext('.//ns:ICMS/*/ns:orig', default='', namespaces=processor.ns).strip()
cst = det.findtext('.//ns:ICMS/*/ns:CST', default='', namespaces=processor.ns).strip()
cst_3digitos = f"{orig}{cst}"  # Concatena origem + CST (ex: "0000")
```

**IPI**:

```python
# Tenta primeiro IPITrib (tributado)
valor_ipi_item = Normalizadores.normalizador_decimal(
    det.findtext('.//ns:IPI/ns:IPITrib/ns:vIPI', default='', namespaces=processor.ns) or 0
)

# Se não encontrou, tenta IPINT (não tributado)
if not valor_ipi_item:
    valor_ipi_item = Normalizadores.normalizador_decimal(
        det.findtext('.//ns:IPI/ns:IPINT/ns:vIPI', default='', namespaces=processor.ns) or 0
    )
```

**Cálculo do Imposto do Item**:

```python
calculo_imposto_item = round(valor_st_item + valor_ipi_item, 2)
```



### 14.7 Rateio de Valores no XML

**Algoritmo Idêntico ao SPED**:

```python
n = len(itens_temp)  # Quantidade de itens

if n == 0:
    continue

valor_para_rateio = round(
    valor_frete_xml + valor_seguro_xml + valor_outros_xml - valor_desconto_xml, 
    2
)

if valor_para_rateio == 0:
    # Sem valores para ratear
    for prod in itens_temp:
        prod['valor_rateado'] = 0
        prod['valor_total'] = round(valor_prod + calculo_imposto_item, 2)
else:
    # Com valores para ratear
    base_share = round(valor_para_rateio / n, 2)
    acumulado = 0.0
    
    for i, prod in enumerate(itens_temp):
        if i < n - 1:
            valor_rateado = base_share
            acumulado += valor_rateado
        else:
            valor_rateado = round(valor_para_rateio - acumulado, 2)
        
        prod['valor_rateado'] = valor_rateado
        valor_prod = Normalizadores.normalizador_decimal(prod.get('valor_prod', 0))
        calculo_imposto_item = Normalizadores.normalizador_decimal(prod.get('calculo_imposto', 0))
        
        # Valor total = Valor produto + Valor rateado + (IPI + ST)
        total_calculado = valor_prod + valor_rateado + calculo_imposto_item
        prod['valor_total'] = round(total_calculado, 2)
```



### 14.8 Correspondência com SPED



#### Critérios de Correspondência

O sistema tenta encontrar a nota do SPED correspondente ao XML usando:

1. **Número da Nota** (`numero_nota`)
2. **Número ID da Nota** (`numero_id_nota` no SPED = `numero_id_formatado` no XML)
3. **Empresa** (deve ser a mesma)

**Código**:

```python
notas_participantes_saida = Notas_participantes.objects.filter(
    numero_nota=numero_nota,      # Do XML
    numero_id_nota=numero_id,      # Do XML (sem prefixo "NFe")
    empresa=empresa_obj
).first()
```



#### Comportamento quando Encontra Correspondência

```python
if notas_participantes_saida:
    # Atualiza status da nota
    notas_participantes_saida.status = 'C/PRODUTO'
    notas_participantes_saida.save()
    
    # Verifica se produto já existe
    existing_prod = Produtos_notas.objects.filter(
        empresa=empresa_obj,
        numero_nota=numero_nota,
        codigo_prod=produtos.get('codigo_prod')
    ).first()
    
    if existing_prod:
        # ATUALIZA produto existente (preserva valor_total do SPED se presente)
        existing_prod.descricao_prod = produtos.get('descricao_prod') or existing_prod.descricao_prod
        existing_prod.ncm = produtos.get('ncm') or existing_prod.ncm
        # ... outros campos
        existing_prod.save()
    else:
        # CRIA novo produto
        produto_obj = Produtos_notas.objects.create(...)
```



#### Comportamento quando NÃO Encontra Correspondência

```python
else:
    # Cria nota e produto do zero (nota XML sem correspondência no SPED)
    notas_participantes_obj = Notas_participantes.objects.create(
        tipo='Saida',
        numero_nota=numero_nota,
        cod_part='---',  # Sem participante
        empresa=empresa_obj,
        status='C/PRODUTO'
    )
    
    produto_obj = Produtos_notas.objects.create(
        tipo_nota='Saida',
        cod_part='---',
        empresa=empresa_obj,
        numero_nota=numero_nota,
        # ... outros campos do XML
    )
```



### 14.9 Tratamento de Múltiplos Arquivos XML

O sistema processa **até 1000 arquivos XML** por vez:

```python
folder_files = request.FILES.getlist('folder_input')

for i, xml_file in enumerate(folder_files):
    # Validações
    if not xml_file.name.lower().endswith('.xml'):
        erros.append(f"'{xml_file.name}' não é um arquivo XML válido")
        continue
    
    if xml_file.size > 10 * 1024 * 1024:  # 10MB
        erros.append(f"'{xml_file.name}' é muito grande (máximo 10MB)")
        continue
    
    # Salva temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml', mode='wb') as temp_file:
        for chunk in xml_file.chunks():
            temp_file.write(chunk)
        temp_file_path = temp_file.name
    
    # Processa
    result = process_xml_file(temp_file_path)
    
    # Remove arquivo temporário
    os.unlink(temp_file_path)
```



### 14.10 Estrutura de Retorno

A função `process_xml_file()` retorna:

```python
return {
    'produtos': produtos_list  # Lista de dicts, um por item
}
```

Cada produto no retorno contém:

```python
{
    'numero_nota': '123456',
    'numero_id': '35241234567890123456789012345678901234567890',
    'chave_nota': '35241234567890123456789012345678901234567890',
    'codigo_prod': '001',
    'descricao_prod': 'Produto Exemplo',
    'ncm': '12345678',
    'valor_prod': 1000.00,
    'quantidade_prod': 10.0,
    'valor_unitario': 100.00,
    'cfop': '5102',
    'cst': '0000',
    'cest': '',
    'valor_ipi': 50.00,
    'valor_icms': '180.00',
    'base_icms': '1000.00',
    'aliquota_icms': '18.00',
    'valor_rateado': 166.66,  # Calculado no rateio
    'valor_total': 1216.66     # valor_prod + valor_rateado + (IPI + ST)
}
```



### 3. Processamento Planilha de Custo



#### Fluxo:

1. Upload de arquivo Excel (.xlsx)
2. Leitura usando `openpyxl`
3. Extração a partir da linha 2
4. Validação de linhas vazias
5. Normalização de valores decimais
6. Persistência no banco



#### Estrutura Esperada:


| Coluna | Campo                 |
| ------ | --------------------- |
| B      | categoria             |
| C      | centro_custo          |
| D      | descricao             |
| E      | documento_fiscal      |
| F      | fornecedor            |
| G      | conta_contabil        |
| H      | valor_total           |
| I      | percentual_aplicado   |
| J      | valor_alocado         |
| K      | icms_passivel_credito |


---



## 🔧 CONFIGURAÇÕES E REQUISITOS



### Configurações Django (`project/settings.py`):



#### Banco de Dados:

Valores vêm do `.env` (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`). Ver README.

#### Limites de Upload:

```python
DATA_UPLOAD_MAX_NUMBER_FILES = 2000  # até 2000 arquivos
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # 10000 campos
MAX_UPLOAD_SIZE = 52428800  # 50MB
```



#### Internacionalização:

```python
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
```



#### Autenticação:

```python
LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/'
```



#### Interface Admin (Jazzmin):

- Tema personalizado
- Logo customizado
- Configurações de UI



### Aplicações Instaladas:

```python
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gerar_arquivo',
    'cadastro',
    'historico',
    'home',
    'metodo_rateio',
    'validacao',
    'accounts',
    'django_extensions'
]
```



### Dependências Python (Principais):

- Django 5.2
- PostgreSQL (psycopg2)
- pandas
- openpyxl
- xml.etree.ElementTree (built-in)

---



## 🛣️ ROTAS E URLs



### URLs Principais (`project/urls.py`):

```python
/                          → Redireciona para /login/
/login/                    → Página de login
/logout/                    → Logout
/admin/                     → Painel administrativo Django
/home/                      → Dashboard (inclui home.urls)
/gerarArquivo/              → Conversão (inclui gerar_arquivo.urls)
/historico/                 → Histórico (inclui historico.urls)
/cadastro/                  → Cadastro (inclui cadastro.urls)
/rateio/                    → Rateio (inclui metodo_rateio.urls)
/validacao/                 → Validação (inclui validacao.urls)
```



### URLs de Cadastro:

```
/cadastro/lista_empresas/
/cadastro/nova/
/cadastro/empresa/cadastrar_empresa/
/cadastro/empresa/editar/<id>/
/cadastro/empresa/excluir/<id>/
/cadastro/lista_produtosSped/
/cadastro/lista_produtosManual/
/cadastro/produto/cadastro_produtos/
/cadastro/produto/editar/<id>/
/cadastro/produto/excluir/<id>/
/cadastro/produto_sped/editar/<id>/
/cadastro/produto_sped/excluir/<id>/
```



### URLs de Validação:

```
/validacao/upload_movimentacoes/
/validacao/processar_arquivos/
/validacao/movimentacoes/
/validacao/validacao_dados/
/validacao/finalizar_movimentacao/
/validacao/validacao/salvar_edicoes
/validacao/atualizar_progresso/
/validacao/exportar-sped/
```



### URLs de Rateio:

```
/rateio/tela_menu/
/rateio/processamento_planilha/
/rateio/view_analisePlanilha/
```

---



## 🔄 FLUXOS DE TRABALHO



### 1. Fluxo de Cadastro de Empresa

```
1. Usuário acessa /cadastro/lista_empresas/
2. Clica em "Nova Empresa" ou "Cadastrar via SPED"
3a. Manual: Preenche formulário → Salva
3b. SPED: Faz upload do arquivo SPED → Sistema extrai dados → Salva
4. Empresa aparece na lista
```



### 2. Fluxo de Validação de Movimentações

```
1. Usuário acessa /validacao/upload_movimentacoes/
2. Interface mostra card SPED (sempre visível)
3. Usuário seleciona arquivo SPED (.txt):
   - Card XML aparece automaticamente
   - Informação do arquivo SPED é exibida
4. Usuário seleciona arquivos XML (múltiplos ou pasta):
   - Card XML permanece visível
   - Contador de arquivos XML é exibido
   - Botão "Processar Arquivos" aparece automaticamente
5. Usuário clica em "Processar Arquivos"
6. Sistema processa:
   a. SPED: Extrai participantes, notas, produtos, cadastro de itens
   b. XML: Extrai dados das notas e produtos
   c. Faz correspondência entre SPED e XML
   d. Atualiza ou cria registros conforme correspondência
   e. Calcula rateios e impostos
7. Dados são salvos no banco
8. Status de validação é atualizado
9. Usuário acessa /validacao/validacao_dados/ para ver movimentações
10. Usuário pode finalizar movimentação por data específica
11. Usuário acessa /validacao/movimentacoes/ para visualizar e editar
12. Pode editar dados inline
13. Pode exportar relatório Excel
```



### 3. Fluxo de Processamento de Planilha de Custo

```
1. Usuário acessa /rateio/tela_menu/
2. Seleciona empresa e data de referência
3. Faz upload da planilha Excel (.xlsx)
4. Sistema processa planilha:
   - Lê dados a partir da linha 2
   - Valida linhas vazias
   - Normaliza valores decimais
   - Salva no banco
5. Usuário acessa /rateio/view_analisePlanilha/
6. Visualiza dados processados
7. Vê totais agrupados por categoria/descrição
```



### 4. Fluxo de Edição de Dados

```
1. Usuário acessa /validacao/movimentacoes/
2. Aplica filtros se necessário
3. Edita dados diretamente na tabela
4. Clica em "Salvar Alterações"
5. Sistema atualiza:
   - Participantes
   - Notas
   - Produtos
6. Dados são persistidos no banco
```

---



## 🛠️ TECNOLOGIAS UTILIZADAS



### Backend:

- **Django 5.2** - Framework web Python
- **PostgreSQL** - Banco de dados relacional
- **Python 3.11+** - Linguagem de programação



### Bibliotecas Python:

- **pandas** - Manipulação de dados e DataFrames
- **openpyxl** - Leitura/escrita de arquivos Excel
- **xml.etree.ElementTree** - Processamento de XML
- **psycopg2** - Driver PostgreSQL



### Frontend:

- **HTML5/CSS3** - Estrutura e estilização
- **JavaScript (ES6+)** - Interatividade e manipulação de DOM
  - Event listeners para upload de arquivos
  - Controle dinâmico de visibilidade de elementos
  - Suporte a drag-and-drop
  - Validação no lado do cliente
- **Bootstrap/Jazzmin** - Framework CSS e tema admin



### Ferramentas:

- **Django Admin (Jazzmin)** - Interface administrativa
- **Django Extensions** - Extensões úteis

---



## 📊 ESTRUTURA DE ARQUIVOS

```
ecredac-main/
├── accounts/              # Autenticação
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── cadastro/              # Cadastro
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── utils.py
│   └── templates/
├── validacao/             # Validação
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── utils.py
│   ├── services.py
│   └── templates/
├── metodo_rateio/         # Rateio
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── utils.py
│   └── templates/
├── gerar_arquivo/         # Conversão
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── historico/             # Histórico
│   ├── views.py
│   └── urls.py
├── home/                   # Dashboard
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── project/                # Configurações
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── static/                 # Arquivos estáticos
│   ├── css/
│   └── img/
├── manage.py
└── sg-ecredac_documentacao.md
```

---



## 🔐 SEGURANÇA E VALIDAÇÕES



### Validações Implementadas:

1. **Upload de Arquivos:**
  - Verificação de extensão (.txt, .xml, .xlsx)
  - Limite de tamanho (10MB por arquivo XML)
  - Limite de quantidade (até 2000 arquivos)
2. **Dados:**
  - Normalização de valores decimais
  - Tratamento de valores nulos/vazios
  - Validação de formatos de data
3. **Autenticação:**
  - Login obrigatório para áreas protegidas
  - Redirecionamento após login/logout
  - Suporte a usuários admin e comuns



### Recomendações de Segurança:

⚠️ **IMPORTANTE**: O sistema está em modo `DEBUG = True` e possui `SECRET_KEY` exposta. Para produção:

1. Alterar `DEBUG = False`
2. Configurar `SECRET_KEY` via variável de ambiente
3. Configurar `ALLOWED_HOSTS`
4. Implementar HTTPS
5. Configurar CSRF adequadamente
6. Implementar rate limiting
7. Validar e sanitizar todas as entradas

---



## 📝 NOTAS IMPORTANTES



### Status de Produtos:

- `C/N` - Com Nota: Produto aparece em uma nota fiscal
- `S/N` - Sem Nota: Produto cadastrado (bloco 0200) mas não aparece em nota
- `S/CADASTRO` - Sem Cadastro: Produto aparece em nota mas não está cadastrado



### Status de Notas:

- `S/PRODUTO` - Sem Produto: Nota sem itens processados
- `C/PRODUTO` - Com Produto: Nota com itens processados



### Status de Validação:

- `pendente` - Aguardando processamento
- `em_andamento` - Processamento em andamento
- `concluido` - Processamento concluído



### Normalização de Valores:

O sistema converte valores no formato brasileiro para decimal:

- `"2000,00"` → `2000.0`
- `"1.234,56"` → `1234.56`
- Valores nulos/vazios → `0.0`

---



## 🆕 MELHORIAS E ATUALIZAÇÕES RECENTES



### Versão 1.1 - Melhorias de Interface e Funcionalidades



#### 1. **Interface de Upload Melhorada**

- **Correção do Bug do Card XML:**
  - O card XML agora aparece automaticamente ao selecionar arquivos XML
  - O card XML também aparece quando o arquivo SPED é selecionado
  - Verificação inicial ao carregar a página para arquivos já selecionados
  - Melhor gerenciamento de visibilidade dos elementos da interface
- **Melhorias de UX:**
  - Botão de processar aparece automaticamente quando SPED e XML estão prontos
  - Feedback visual imediato ao selecionar arquivos
  - Contador de arquivos XML selecionados
  - Informações de arquivo exibidas dinamicamente



#### 2. **Sistema de Validação por Data**

- Validação independente por data SPED
- Múltiplas validações simultâneas para diferentes períodos
- Finalização seletiva por data de referência
- Separação visual entre validações concluídas e em andamento
- Controle de progresso granular por empresa e data



#### 3. **Processamento XML Aprimorado**

- Melhor correspondência entre notas SPED e XML
- Tratamento de notas XML sem correspondência no SPED
- Criação automática de registros para notas XML isoladas
- Atualização inteligente de produtos existentes
- Cálculo aprimorado de impostos por item



#### 4. **JavaScript e Interatividade**

- Função `updateProcessButton()` para controle centralizado
- Verificações de segurança para elementos DOM
- Tratamento robusto de eventos de upload
- Suporte aprimorado para drag-and-drop
- Validação de arquivos no lado do cliente



#### 5. **Cadastro de Itens SPED**

- Novo modelo `Cadastro_itens_sped` para catalogação de produtos
- Extração automática do bloco 0200 do SPED
- Armazenamento de informações completas de produtos
- Suporte para múltiplos tipos de item

---



## 🚀 PRÓXIMOS PASSOS E MELHORIAS SUGERIDAS

1. **Testes:**
  - Implementar testes unitários
  - Testes de integração
  - Testes de performance
2. **Documentação de API:**
  - Documentar endpoints JSON/API
  - Swagger/OpenAPI
3. **Melhorias de Performance:**
  - Cache de consultas frequentes
  - Processamento assíncrono para arquivos grandes
  - Otimização de queries SQL
4. **Funcionalidades:**
  - Dashboard com gráficos
  - Relatórios personalizados
  - Exportação em múltiplos formatos
  - Histórico de alterações (auditoria)
5. **Interface:**
  - Melhorias de UX/UI
  - Responsividade mobile
  - Feedback visual de processamento

---



## 📞 SUPORTE

Para dúvidas ou problemas:

1. Verificar logs do Django
2. Verificar logs do PostgreSQL
3. Consultar documentação do Django
4. Verificar configurações de upload

---

**Documentação gerada em:** 2024  
**Versão do Sistema:** 1.1  
**Última atualização:** Dezembro 2024 - Inclui melhorias de interface, correção do bug do card XML, sistema de validação por data e processamento XML aprimorado

---



## 17. TROUBLESHOOTING E PROBLEMAS COMUNS



### 17.1 Problemas de Upload de Arquivos



#### Erro: "Nenhum arquivo SPED enviado"

**Causa**: Arquivo SPED não foi selecionado ou não chegou ao servidor.
**Solução**:

1. Verificar se o arquivo foi selecionado corretamente
2. Verificar tamanho do arquivo (máximo configurado)
3. Verificar permissões de escrita no servidor
4. Verificar logs do Django para erros específicos



#### Erro: "Arquivo muito grande"

**Causa**: Arquivo XML excede 10MB.
**Solução**:

- Dividir arquivos grandes em múltiplos uploads
- Verificar configuração `MAX_UPLOAD_SIZE` em `settings.py`
- Aumentar limite se necessário (cuidado com memória)



#### Erro: "Empresa não cadastrada"

**Causa**: CNPJ extraído do SPED não existe no banco.
**Solução**:

1. Verificar se empresa foi cadastrada antes do processamento
2. Verificar se CNPJ no SPED está correto (sem formatação)
3. Cadastrar empresa manualmente ou via SPED de cadastro



### 17.2 Problemas de Processamento SPED



#### Erro: "Erro ao carregar arquivo SPED"

**Causa**: Problema de encoding ou formato do arquivo.
**Solução**:

1. Verificar se arquivo está em UTF-8
2. Verificar se arquivo não está corrompido
3. Verificar se formato está correto (delimitador `|`)



#### Produtos aparecem como "S/CADASTRO"

**Causa**: Produto está no bloco C170 mas não no bloco 0200.
**Solução**:

- Normal: Produto foi adicionado diretamente na nota sem cadastro prévio
- Se necessário, cadastrar produto manualmente ou verificar SPED original



#### Valores de rateio incorretos

**Causa**: Algoritmo de rateio ou valores de frete/seguro incorretos.
**Solução**:

1. Verificar valores de frete, seguro e despesas no bloco C100
2. Verificar se quantidade de itens está correta
3. Revisar algoritmo de rateio em `extract_sped.py` (linha ~241)



### 17.3 Problemas de Processamento XML



#### Erro: "Erro de parsing XML"

**Causa**: XML malformado ou namespace incorreto.
**Solução**:

1. Validar XML com validador online
2. Verificar se namespace está correto: `http://www.portalfiscal.inf.br/nfe`
3. Verificar se XML não está corrompido



#### Notas XML não correspondem ao SPED

**Causa**: Número da nota ou número ID diferente.
**Solução**:

1. Verificar se `numero_nota` do XML corresponde ao SPED
2. Verificar se `numero_id_nota` (chave sem prefixo "NFe") corresponde
3. Verificar se empresa é a mesma
4. Notas XML sem correspondência são criadas automaticamente com `cod_part='---'`



#### Impostos não extraídos corretamente

**Causa**: Estrutura XML diferente ou campos ausentes.
**Solução**:

1. Verificar estrutura do XML (ICMS pode estar em diferentes tags: ICMS00, ICMS10, etc.)
2. Verificar se IPI está em IPITrib ou IPINT
3. Ajustar XPath em `extract_xml.py` se necessário



### 17.4 Problemas de Banco de Dados



#### Erro: "relation does not exist"

**Causa**: Tabelas não foram criadas (migrations não aplicadas).
**Solução**:

```bash
python manage.py makemigrations
python manage.py migrate
```



#### Erro: "duplicate key value violates unique constraint"

**Causa**: Tentativa de criar registro duplicado com constraint unique.
**Solução**:

- Verificar se registro já existe antes de criar
- Usar `get_or_create()` em vez de `create()`
- Verificar constraints únicas nos modelos



#### Performance lenta em queries

**Causa**: Falta de índices ou queries não otimizadas.
**Solução**:

1. Adicionar índices em campos frequentemente filtrados
2. Usar `select_related()` e `prefetch_related()` para evitar N+1 queries
3. Analisar queries com `connection.queries` em DEBUG mode



### 17.5 Problemas de Interface



#### Card XML não aparece

**Causa**: JavaScript não carregou ou erro no código.
**Solução**:

1. Verificar console do navegador para erros JavaScript
2. Verificar se `upload_movimentacoes.js` está carregado
3. Verificar função `updateProcessButton()` e event listeners



#### Botão "Processar" não aparece

**Causa**: Condições JavaScript não atendidas.
**Solução**:

1. Verificar se SPED foi selecionado
2. Verificar se XML foi selecionado
3. Verificar função `updateProcessButton()` em `upload_movimentacoes.js`



#### Edições inline não salvam

**Causa**: Erro no endpoint de salvamento ou CSRF token.
**Solução**:

1. Verificar console do navegador
2. Verificar se CSRF token está presente
3. Verificar endpoint `/validacao/validacao/salvar_edicoes`
4. Verificar logs do Django



### 17.6 Comandos Úteis para Debug

```bash
# Verificar logs do Django
python manage.py runserver --verbosity 2

# Verificar conexão com banco
python manage.py dbshell

# Limpar cache
python manage.py clear_cache

# Verificar migrations pendentes
python manage.py showmigrations

# Shell interativo do Django
python manage.py shell
```



### 17.7 Logs e Monitoramento

**Localização dos Logs**:

- Django: Console onde `runserver` está rodando
- PostgreSQL: Logs do PostgreSQL (configurável)
- Erros: Verificar `settings.py` para configuração de logging

**Como Ativar Logging Detalhado**:

```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'validacao': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}
```

---



## 18. CHECKLIST DE MANUTENÇÃO



### 18.1 Checklist Diário

- [ ] Verificar logs de erro do Django
- [ ] Verificar espaço em disco do servidor
- [ ] Verificar se banco de dados está acessível
- [ ] Verificar se uploads estão funcionando



### 18.2 Checklist Semanal

- [ ] Verificar performance de queries (usar `connection.queries`)
- [ ] Verificar se migrations estão atualizadas
- [ ] Limpar arquivos temporários se houver
- [ ] Verificar backups do banco de dados



### 18.3 Checklist Mensal

- [ ] Revisar logs de erro acumulados
- [ ] Verificar espaço em disco
- [ ] Otimizar banco de dados (VACUUM, ANALYZE no PostgreSQL)
- [ ] Revisar e atualizar documentação se necessário
- [ ] Verificar dependências Python por vulnerabilidades



### 18.4 Checklist Antes de Deploy

- [ ] Executar testes (se houver)
- [ ] Verificar `DEBUG = False` em produção
- [ ] Configurar `SECRET_KEY` via variável de ambiente
- [ ] Configurar `ALLOWED_HOSTS`
- [ ] Configurar HTTPS
- [ ] Fazer backup do banco de dados
- [ ] Aplicar migrations: `python manage.py migrate`
- [ ] Coletar arquivos estáticos: `python manage.py collectstatic`
- [ ] Verificar permissões de arquivos



### 18.5 Comandos de Manutenção do Banco

```sql
-- PostgreSQL: Verificar tamanho das tabelas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- PostgreSQL: Otimizar tabelas
VACUUM ANALYZE validacao_produtos_notas;
VACUUM ANALYZE validacao_notas_participantes;
VACUUM ANALYZE validacao_participantes;

-- PostgreSQL: Verificar índices
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```



### 18.6 Backup e Restauração



#### Backup do Banco de Dados

```bash
# Backup completo
pg_dump -U postgres -d ecredac > backup_$(date +%Y%m%d).sql

# Backup apenas estrutura
pg_dump -U postgres -d ecredac --schema-only > schema_backup.sql

# Backup apenas dados
pg_dump -U postgres -d ecredac --data-only > data_backup.sql
```



#### Restauração

```bash
# Restaurar backup completo
psql -U postgres -d ecredac < backup_20241201.sql

# Cuidado: Isso substitui todos os dados!
```



### 18.7 Atualização de Dependências

```bash
# Verificar dependências desatualizadas
pip list --outdated

# Atualizar dependências (cuidado!)
pip install --upgrade django
pip install --upgrade pandas
# etc.

# Verificar compatibilidade antes de atualizar
# Sempre testar em ambiente de desenvolvimento primeiro
```



### 18.8 Limpeza de Dados



#### Limpar Validações Concluídas (se necessário)

```python
# No shell do Django
from validacao.models import ValidacaoDataConcluida
ValidacaoDataConcluida.objects.all().delete()
```



#### Limpar Produtos Duplicados (se necessário)

```python
# Cuidado: Sempre fazer backup antes!
from validacao.models import Produtos_notas
from django.db.models import Count

# Identificar duplicados
duplicados = Produtos_notas.objects.values(
    'empresa', 'numero_nota', 'codigo_prod'
).annotate(
    count=Count('id')
).filter(count__gt=1)
```

---

