# Relatório: Registros 5010, 5015 e 5020 - E-CREDAC

## 1. Visão Geral

Os registros **5010**, **5015** e **5020** fazem parte do **Bloco 5** do arquivo E-CREDAC (Sistema Eletrônico de Gerenciamento do Crédito Acumulado de ICMS). Eles estruturam as informações de documentos fiscais e seus itens para fins de crédito tributário.

---

## 2. Registro 5015

### 2.1 Definição
O **Registro 5015** representa os **itens/detalhes dos documentos fiscais** que compõem a base para o crédito acumulado de ICMS.

### 2.2 Origem dos Dados
- **Modelo**: `Notas_participantes` + `Produtos_notas`
- **Filtro**: Notas com `data_inicio_sped` igual ao período validado
- **Campos utilizados**:
  - `data_entrada_saida` → Data do documento
  - `tipo` → Entrada/Saída
  - `numero_nota` → Número da NF
  - `tipo_documento` → Código do modelo (ex: 55 para NF-e)
  - `serie_documento` → Série do documento
  - `numero_documento` → Número do documento de importação (DI) quando aplicável
  - `cod_part` → Código do participante (fornecedor/cliente)

### 2.3 Estrutura do Registro 5015 (no código)
```
|5015|contagem|data|concatenacao|tipo_documento|serie_documento|nota|cfop|numero_documento|cod_part|''|tipo_inf|codigo_prod|quantidade|''|valor_icms|
```

| Campo | Descrição | Origem |
|-------|-----------|--------|
| contagem | Índice sequencial do item | Incremento por item |
| data | Data entrada/saída (DDMMAAAA) | `Notas_participantes.data_entrada_saida` |
| concatenacao | Tipo + Número da nota | `tipo` + `numero_nota` |
| tipo_documento | Modelo do documento | `Notas_participantes.tipo_documento` |
| serie_documento | Série | `Notas_participantes.serie_documento` |
| nota | Número da nota | `Notas_participantes.numero_nota` |
| cfop | CFOP do item | `Produtos_notas.cfop_prod` |
| numero_documento | Nº documento importação | `Notas_participantes.numero_documento` |
| cod_part | Código participante | `Notas_participantes.cod_part` |
| tipo_inf | 0=Entrada, 1=Saída | Derivado de `Produtos_notas.tipo_nota` |
| codigo_prod | Código do produto | `Produtos_notas.codigo_prod` |
| quantidade | Quantidade do item | `Produtos_notas.quantidade_prod` |
| valor_icms | Valor do ICMS | `Produtos_notas.valor_icms` |

---

## 3. Registro 5020

### 3.1 Definição
O **Registro 5020** armazena o **valor do IPI** (Imposto sobre Produtos Industrializados) de cada item do documento fiscal.

### 3.2 Origem dos Dados
- **Modelo**: `Produtos_notas`
- **Campo**: `valor_ipi`

### 3.3 Estrutura do Registro 5020 (no código)
```
|5020|valor_ipi|''|
```

| Campo | Descrição | Origem |
|-------|-----------|--------|
| valor_ipi | Valor do IPI do item | `Produtos_notas.valor_ipi` |
| '' | Campo complementar vazio | - |

### 3.4 Relação com 5015
O **5020** é sempre gerado **imediatamente após** cada **5015**, formando o par item + IPI. Para cada item da nota há um 5015 seguido de um 5020.

---

## 4. Registro 5010

### 4.1 Definição
O **Registro 5010** atua como **cabeçalho/abertura** do documento fiscal, agrupando os registros 5015 e 5020 que se seguem.

### 4.2 Implementação Atual
No código, o 5010 é escrito com campos vazios (placeholders):
```python
campo = ["5010"] + [None] * 8
```
Ou seja: `|5010|||||||||`

### 4.3 Função
- Marca o início de um novo documento fiscal
- Cada nota fiscal gera **um** registro 5010
- Todos os itens (5015 + 5020) dessa nota ficam hierarquicamente abaixo dele

---

## 5. Hierarquia 5010 → 5015 → 5020

### 5.1 Estrutura Hierárquica

```
5010  ← Cabeçalho da Nota 1
├── 5015  ← Item 1 da Nota 1
│   └── 5020  ← IPI do Item 1
├── 5015  ← Item 2 da Nota 1
│   └── 5020  ← IPI do Item 2
└── ...

5010  ← Cabeçalho da Nota 2
├── 5015  ← Item 1 da Nota 2
│   └── 5020  ← IPI do Item 1
└── ...
```

### 5.2 Fluxo de Geração (gerar_arquivo.py)

1. Para cada nota em `registros_5015` (Notas_participantes):
   - Escreve **5010** (cabeçalho)
   - Para cada item em `Produtos_notas` dessa nota:
     - Escreve **5015** (dados do item)
     - Escreve **5020** (valor IPI do item)

### 5.3 Ordem de Escrita no Arquivo
```
|5010|||||||||
|5015|0|01012024|Entrada123|55|1|123|1102|DI123|PART001||0|PROD001|10,00||150,00|
|5020|25,50|
|5015|1|01012024|Entrada123|55|1|123|1102|DI123|PART001||0|PROD002|5,00||80,00|
|5020|0,00|
|5010|||||||||
...
```

---

## 6. Resumo Rápido

| Registro | Função | Quantidade por Nota | Dados Principais |
|----------|--------|---------------------|------------------|
| **5010** | Cabeçalho do documento fiscal | 1 por nota | Placeholder (campos vazios) |
| **5015** | Item do documento fiscal | 1 por item da nota | CFOP, produto, quantidade, ICMS, participante |
| **5020** | Valor IPI do item | 1 por item (após cada 5015) | valor_ipi |

**Hierarquia**: `5010` agrupa → `5015` (item) + `5020` (IPI do item) → repetido para cada item da nota.

**Fonte**: Dados vêm do SPED (C100, C170, C120) processados em `extract_sped.py` e armazenados em `Notas_participantes` e `Produtos_notas`, utilizados na geração do arquivo E-CREDAC em `gerar_arquivo.py`.
