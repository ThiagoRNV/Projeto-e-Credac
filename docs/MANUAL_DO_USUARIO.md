# Manual do usuário — SG-ECREDAC

Este manual explica o uso do **Sistema de Gestão E-CREDAC** no dia a dia: cadastro, upload de arquivos, conferência, rateio, fichas e geração do arquivo.

A instalação técnica (Python, PostgreSQL, `.env`) está no [`README.md`](../README.md) da raiz do projeto.

**Atualizado em:** agosto de 2026

---

## Índice

1. [Primeiros Passos](#primeiros-passos)
2. [Mapa do menu](#mapa-do-menu)
3. [Cadastro de Empresas](#cadastro-de-empresas)
4. [Cadastro de Produtos](#cadastro-de-produtos)
5. [Validação de Movimentações](#validação-de-movimentações)
6. [Como Funcionam os Cálculos](#como-funcionam-os-cálculos)
7. [Processamento de Planilhas de Custo](#processamento-de-planilhas-de-custo)
8. [Visualização e Edição de Dados](#visualização-e-edição-de-dados)
9. [Exportação de Relatórios](#exportação-de-relatórios)
10. [Dúvidas Frequentes](#dúvidas-frequentes)

---

## 🚀 PRIMEIROS PASSOS

### Acessando o Sistema

1. Abra seu navegador e acesse o endereço do sistema
2. Você será redirecionado para a tela de **Login**
3. Digite seu **usuário** e **senha**
4. Clique em **"Entrar"**

### Tipos de Acesso

- **Usuário comum**: acessa as telas liberadas para o seu usuário (cadastro, movimentação, rateio, fichas, gerar arquivo).
- **Administrador**: além do sistema, acessa o painel `/admin/` (empresas, permissões, usuários).

Na tela de login é possível escolher se o destino será o **sistema** ou o **admin**.

O que cada pessoa vê no menu é definido em **Permissões** no Admin (`home.Permissions`). Se um item não aparecer, peça ao administrador para habilitar a tela no seu usuário.

---

## Mapa do menu

A barra superior (depois do login) organiza o trabalho assim:

| Menu | Para que serve |
|------|----------------|
| **Home** | Painel inicial |
| **Gerar arquivo** | Baixa o arquivo E-CREDAC da empresa/mês já validados |
| **Histórico** | Mostra quem alterou o quê (campo, valor antigo e novo) |
| **Cadastro** | Empresas, produtos (bloco 0200) e regras de código de lançamento |
| **Método de rateio** | Planilha de custo e Bloco K do SPED (produção K230/K235 e industrialização K250/K255) |
| **Movimentações** | Upload SPED/XML e DUE; NF-es em andamento; outros modelos (energia, CT-e, comunicação) |
| **Fichas** | Fichas 1 a 6 de controle de custos |
| **Pendências** | Acompanhamento de pendências |
| **Ajuda** | Orientações de uso |
| **Sair** | Encerra a sessão |

Ordem sugerida de trabalho: cadastrar a empresa → conferir produtos → subir SPED/XML (e DUE, se houver) → concluir a movimentação no painel → rateio/Bloco K → fichas → gerar arquivo.

---

## Cadastro de Empresas

### Como Cadastrar uma Empresa

Você pode cadastrar empresas de **duas formas**:

#### **Opção 1: Cadastro Manual**

1. Acesse o menu **"Cadastro"** → **"Empresas"** → **"Nova Empresa"**
2. Preencha os campos:
   - **Razão Social** (obrigatório)
   - **CNPJ** (obrigatório)
   - **Inscrição Estadual**
   - **UF** (Estado)
   - **Endereço completo**
   - **Telefone** e **E-mail**
   - **Método de Rateio** (se aplicável)
3. Clique em **"Salvar"**

#### **Opção 2: Cadastro via Arquivo SPED**

1. Acesse **"Cadastro"** → **"Empresas"** → **"Cadastrar via SPED"**
2. Selecione o arquivo SPED (.txt) da empresa
3. O sistema extrairá automaticamente:
   - Razão Social
   - CNPJ
   - Inscrição Estadual
   - UF
   - Endereço completo
   - Telefone e E-mail
4. Clique em **"Processar"**
5. A empresa será cadastrada automaticamente

### Editar ou Excluir Empresa

- **Editar**: Clique no botão de edição ao lado da empresa na lista
- **Excluir**: Clique no botão de exclusão (cuidado: esta ação não pode ser desfeita!)

---

## 📦 CADASTRO DE PRODUTOS

### Cadastro Manual de Produtos

1. Acesse **"Cadastro"** → **"Produtos"** → **"Cadastrar Produto"**
2. Preencha os dados:
   - **Empresa** (selecione da lista)
   - **Código do Produto**
   - **Descrição**
   - **Unidade** (UN, KG, M, etc.)
   - **NCM** (Nomenclatura Comum do Mercosul)
   - **CEST** (Código Especificador da Substituição Tributária)
   - **Tipo de Produto**
   - **Saldo Inicial** (se aplicável)
3. Clique em **"Salvar"**

### Visualizar Produtos

- **Produtos do SPED**: Produtos extraídos automaticamente dos arquivos SPED
- **Produtos Cadastrados**: Produtos cadastrados manualmente

---

## ✅ VALIDAÇÃO DE MOVIMENTAÇÕES

Esta é uma das funcionalidades mais importantes do sistema! Aqui você processa os arquivos fiscais e valida os dados.

### Passo 1: Upload de Arquivos

No menu, o caminho atual é **Movimentações**. Há três entradas de upload/conferência:

| Caminho no menu | Quando usar |
|-----------------|-------------|
| Movimentações → Upload → **SPED/XML** | Mercadorias (NF-e): arquivo SPED `.txt` + XMLs |
| Movimentações → Upload → **DUE** | Exportação: planilha da Declaração Única de Exportação |
| Movimentações → **NF-es em andamento** | Acompanhar e concluir o processamento de mercadorias |
| Movimentações → **Outros modelos em andamento** | Energia (C500), transporte/CT-e (D100) e comunicação (D500) |

Para NF-e:

1. Acesse **Movimentações** → **Upload** → **SPED/XML**
2. Selecione a **empresa**
3. Envie os arquivos:

   **Arquivo SPED (.txt)**  
   Arquivo da escrituração digital da empresa (extensão `.txt`).

   **Arquivos XML (NF-e)**  
   Arquivos avulsos ou uma pasta inteira. O sistema aceita um grande volume no mesmo envio (configuração atual: até 2000 arquivos).

4. Clique em **Processar arquivos**

Depois do processamento, abra **NF-es em andamento** (ou **Outros modelos em andamento**) para conferir o progresso, editar o que for necessário e **finalizar** o período. Só depois disso o mês entra como concluído e pode ser usado em **Gerar arquivo**.

### Passo 2: Processamento Automático

O sistema irá:

1. **Ler o arquivo SPED** e extrair:
   - Dados dos participantes (fornecedores/clientes)
   - Notas fiscais (entrada e saída)
   - Produtos e seus valores
   - Impostos (ICMS, IPI, etc.)

2. **Ler os arquivos XML** e extrair:
   - Dados completos das notas fiscais
   - Detalhes de cada produto/item
   - Valores de impostos por item

3. **Fazer a correspondência** entre SPED e XML:
   - O sistema compara as notas do SPED com as notas dos XMLs
   - Atualiza os dados quando encontra correspondência
   - Cria novos registros quando necessário

4. **Calcular valores**:
   - Rateia valores de frete, seguro e despesas entre os itens
   - Calcula o valor total de cada produto
   - Soma impostos corretamente

### Passo 3: Visualizar Resultados

1. Após o processamento, acesse **"Validação"** → **"Movimentações"**
2. Você verá uma tabela com todos os dados processados
3. Use os **filtros** para encontrar informações específicas
4. Os dados podem ser **editados diretamente na tabela**

---

## 🧮 COMO FUNCIONAM OS CÁLCULOS

Esta seção explica **detalhadamente** como o sistema realiza os cálculos. É importante entender para validar os resultados!

### 1. CÁLCULO DO VALOR UNITÁRIO

**Fórmula:**
```
Valor Unitário = Valor do Produto ÷ Quantidade
```

**Exemplo:**
- Valor do Produto: R$ 1.000,00
- Quantidade: 10 unidades
- **Valor Unitário = R$ 1.000,00 ÷ 10 = R$ 100,00**

---

### 2. CÁLCULO DE IMPOSTOS POR ITEM (SPED)

Quando o sistema processa um arquivo SPED, ele calcula os impostos de cada item da nota:

**Fórmula:**
```
Imposto do Item = IPI + ST - Desconto
```

Onde:
- **IPI** = Imposto sobre Produtos Industrializados
- **ST** = Substituição Tributária
- **Desconto** = Desconto aplicado ao item

**Exemplo:**
- IPI: R$ 50,00
- ST: R$ 30,00
- Desconto: R$ 10,00
- **Imposto do Item = R$ 50,00 + R$ 30,00 - R$ 10,00 = R$ 70,00**

---

### 3. RATEIO DE VALORES (FRETE, SEGURO, DESPESAS)

Esta é uma das partes mais importantes! O sistema distribui valores que são da **nota inteira** entre os **itens individuais**.

#### **Valores que são Rateados:**

- **Frete** (custo de transporte)
- **Seguro** (seguro da mercadoria)
- **Despesas Acessórias** (outras despesas da nota)
- **Outros Valores** (do XML)
- **Desconto** (desconto total da nota - reduz o valor a ratear)

#### **Como Funciona o Rateio:**

O sistema divide esses valores **igualmente** entre todos os itens da nota.

**Fórmula Geral:**
```
Valor para Rateio = Frete + Seguro + Despesas Acessórias + Outros - Desconto
Valor Rateado por Item = Valor para Rateio ÷ Quantidade de Itens
```

**Exemplo Prático:**

Imagine uma nota fiscal com:
- **3 itens** (produtos diferentes)
- **Frete**: R$ 300,00
- **Seguro**: R$ 150,00
- **Despesas Acessórias**: R$ 50,00
- **Desconto**: R$ 100,00

**Cálculo:**
1. Valor para Rateio = R$ 300,00 + R$ 150,00 + R$ 50,00 - R$ 100,00 = **R$ 400,00**
2. Valor Rateado por Item = R$ 400,00 ÷ 3 = **R$ 133,33** (para os 2 primeiros itens)
3. Último item recebe o restante para evitar diferenças de arredondamento: **R$ 133,34**

**Distribuição:**
- Item 1: R$ 133,33
- Item 2: R$ 133,33
- Item 3: R$ 133,34
- **Total Rateado: R$ 400,00** ✓

---

### 4. CÁLCULO DO VALOR TOTAL DO PRODUTO

O valor total de cada produto é calculado somando:
- Valor do produto
- Valor rateado (frete, seguro, etc.)
- Impostos do item

#### **Para Arquivos SPED:**

**Fórmula:**
```
Valor Total = Valor do Produto + Valor Rateado + Impostos do Item
```

**Exemplo:**
- Valor do Produto: R$ 1.000,00
- Valor Rateado: R$ 133,33
- Impostos (IPI + ST - Desconto): R$ 70,00
- **Valor Total = R$ 1.000,00 + R$ 133,33 + R$ 70,00 = R$ 1.203,33**

#### **Para Arquivos XML:**

**Fórmula:**
```
Valor Total = Valor do Produto + Valor Rateado + (IPI + ST)
```

**Exemplo:**
- Valor do Produto: R$ 2.000,00
- Valor Rateado: R$ 200,00
- IPI: R$ 100,00
- ST: R$ 50,00
- **Valor Total = R$ 2.000,00 + R$ 200,00 + (R$ 100,00 + R$ 50,00) = R$ 2.350,00**

---

### 5. CÁLCULO DE IMPOSTOS NO XML

Quando processa XMLs, o sistema extrai os impostos diretamente do arquivo:

**Impostos Extraídos:**
- **ICMS**: Imposto sobre Circulação de Mercadorias e Serviços
- **IPI**: Imposto sobre Produtos Industrializados
- **ST**: Substituição Tributária
- **Base de Cálculo do ICMS**: Valor sobre o qual o ICMS é calculado
- **Alíquota do ICMS**: Percentual do ICMS

**Cálculo do ICMS (quando necessário):**
```
ICMS = Base de Cálculo × (Alíquota ÷ 100)
```

**Exemplo:**
- Base de Cálculo: R$ 1.000,00
- Alíquota: 18%
- **ICMS = R$ 1.000,00 × (18 ÷ 100) = R$ 180,00**

---

### 6. TRATAMENTO DE ARREDONDAMENTOS

O sistema usa uma técnica especial para evitar problemas de arredondamento:

1. Calcula o valor base para cada item (exceto o último)
2. Soma todos os valores rateados dos itens anteriores
3. O **último item** recebe a diferença para completar o total exato

**Por que isso é importante?**

Se dividirmos R$ 400,00 por 3:
- Divisão exata: R$ 133,333333...
- Arredondando: R$ 133,33 cada
- Total: R$ 133,33 × 3 = R$ 399,99 ❌ (falta 1 centavo!)

**Solução do Sistema:**
- Item 1: R$ 133,33
- Item 2: R$ 133,33
- Item 3: R$ 400,00 - (R$ 133,33 + R$ 133,33) = R$ 133,34 ✓
- **Total: R$ 400,00** ✓

---

### 7. CASOS ESPECIAIS

#### **Quando Não Há Valores para Ratear:**

Se a nota não tiver frete, seguro ou despesas:
```
Valor Total = Valor do Produto + Impostos
```

#### **Quando Há Apenas Um Item na Nota:**

O item recebe 100% dos valores a ratear:
```
Valor Rateado = Total de Valores da Nota
Valor Total = Valor do Produto + Valor Rateado + Impostos
```

---

## 📊 PROCESSAMENTO DE PLANILHAS DE CUSTO

Esta funcionalidade permite processar planilhas Excel com dados de custos para análise.

### Como Processar uma Planilha

1. Acesse **"Rateio"** → **"Menu"**
2. Selecione a **Empresa**
3. Informe a **Data de Referência**
4. Faça upload da planilha Excel (.xlsx)
5. Clique em **"Processar"**

### Estrutura da Planilha

A planilha deve ter as seguintes colunas (a partir da linha 2):

| Coluna | Campo | Exemplo |
|--------|-------|---------|
| B | Categoria | Serviço, Material, etc. |
| C | Centro de Custo | Administrativo, Produção |
| D | Descrição | Descrição do custo |
| E | Documento Fiscal | Número da nota |
| F | Fornecedor | Nome do fornecedor |
| G | Conta Contábil | Código da conta |
| H | Valor Total | 1000,00 |
| I | Percentual Aplicado | 50,00 |
| J | Valor Alocado | 500,00 |
| K | ICMS Passível de Crédito | 90,00 |

### Visualizar Análise

1. Acesse **"Rateio"** → **"Análise da Planilha"**
2. Você verá:
   - **Dados detalhados** de cada linha processada
   - **Totais agrupados** por descrição
   - **Totais gerais** por categoria

---

## 👁️ VISUALIZAÇÃO E EDIÇÃO DE DADOS

### Visualizar Movimentações

1. Acesse **"Validação"** → **"Movimentações"**
2. A tabela mostra:
   - Dados do participante (fornecedor/cliente)
   - Dados da nota fiscal
   - Dados do produto
   - Valores e impostos

### Filtros Disponíveis

Use os filtros para encontrar dados específicos:
- **Tipo de Nota** (Entrada/Saída)
- **CNPJ/CPF** do participante
- **Número da Nota**
- **Código do Produto**
- **Descrição do Produto**
- **NCM**
- **CFOP**
- **Valores** (quantidade, unitário, total)
- **Impostos** (ICMS, IPI, etc.)

### Editar Dados

1. Clique na célula que deseja editar
2. Digite o novo valor
3. Pressione **Enter** ou clique em outra célula
4. Clique no botão **"Salvar Alterações"** no topo da página
5. Os dados serão atualizados no banco de dados

**⚠️ Atenção:** As edições só são salvas quando você clica em "Salvar Alterações"!

### Paginação

- A tabela mostra **100 registros por página**
- Use as setas de navegação para ver mais registros
- Os **totais** são calculados apenas para a página atual

---

## 📥 EXPORTAÇÃO DE RELATÓRIOS

### Exportar para Excel

1. Acesse **"Validação"** → **"Movimentações"**
2. Aplique os filtros desejados (opcional)
3. Clique no botão **"Exportar Relatório"**
4. O sistema gerará um arquivo Excel (.xlsx)
5. O arquivo será baixado automaticamente

### O que é Exportado

O relatório inclui todas as colunas visíveis na tela:
- Tipo de Nota
- CNPJ/CPF
- Número da Nota
- Nome do Participante
- UF
- CFOP
- Código e Descrição do Produto
- NCM
- Quantidade
- Valores (unitário, total)
- Impostos (ICMS, IPI)
- CST e CEST

---

## ✅ VALIDAÇÃO E FINALIZAÇÃO

### Lista de Validações

1. Acesse **"Validação"** → **"Validação de Dados"**
2. Você verá uma lista de todas as movimentações processadas
3. Cada movimentação mostra:
   - **Empresa**
   - **Data do SPED**
   - **Status** (Em Andamento / Concluído)
   - **Progresso** (percentual)

### Finalizar Movimentação

Quando você terminar de validar os dados de uma data específica:

1. Na lista de validações, encontre a movimentação desejada
2. Clique no botão **"Finalizar"**
3. A movimentação será marcada como **"Concluída"**
4. Ela será movida para a seção de **"Movimentações Concluídas"**

**⚠️ Importante:** 
- Você pode finalizar movimentações por **data**
- Uma empresa pode ter várias movimentações (uma para cada data)
- Após finalizar, os dados ainda podem ser visualizados, mas ficam marcados como concluídos

### Limpar Dados Concluídos

Se necessário, você pode limpar todas as marcações de "concluído":
1. Na tela de validações, clique em **"Limpar Concluídos"**
2. Todas as movimentações voltarão para "Em Andamento"

---

## ❓ DÚVIDAS FREQUENTES

### 1. Por que alguns produtos aparecem como "S/N" (Sem Nota)?

**Resposta:** Isso significa que o produto está cadastrado no SPED (bloco 0200), mas não aparece em nenhuma nota fiscal. Pode ser um produto que estava no estoque mas não foi vendido/comprado no período.

### 2. Por que alguns produtos aparecem como "S/CADASTRO"?

**Resposta:** O produto aparece em uma nota fiscal, mas não está cadastrado no catálogo de produtos do SPED. Isso pode acontecer quando:
- O produto foi adicionado manualmente na nota
- Houve erro no cadastro do SPED
- O produto é novo e ainda não foi cadastrado

### 3. Como o sistema faz a correspondência entre SPED e XML?

**Resposta:** O sistema compara:
- **Número da Nota** (campo `nNF` no XML)
- **Número ID da Nota** (chave de acesso sem os 3 primeiros dígitos)
- **Empresa** (deve ser a mesma)

Quando encontra correspondência, atualiza os dados do SPED com as informações mais completas do XML.

### 4. Por que o valor total do produto é diferente do valor na nota?

**Resposta:** O sistema **soma** ao valor do produto:
- Valores rateados (frete, seguro, despesas)
- Impostos (IPI, ST)

Isso é feito para que cada item reflita seu **custo real**, incluindo todos os custos da nota.

### 5. Posso processar arquivos de empresas diferentes ao mesmo tempo?

**Resposta:** Não. O sistema processa **uma empresa por vez**. Selecione a empresa antes de fazer o upload dos arquivos.

### 6. Quantos arquivos posso enviar de uma vez?

**Resposta:**
- **SPED**: 1 arquivo por vez
- **XML**: Até 1000 arquivos por vez
- **Tamanho máximo**: 10MB por arquivo XML

### 7. O que acontece se eu enviar o mesmo arquivo duas vezes?

**Resposta:** 
- Se a nota já existe, o sistema **atualiza** os dados
- Se for um produto novo, o sistema **cria** um novo registro
- Pode haver duplicação se os dados não corresponderem exatamente

### 8. Como saber se o processamento foi bem-sucedido?

**Resposta:** Após o processamento, você verá:
- Mensagem de sucesso
- Quantidade de produtos processados
- Lista de erros (se houver)

### 9. Posso editar dados depois de finalizar uma movimentação?

**Resposta:** Sim, você pode editar os dados mesmo após finalizar. A finalização é apenas uma marcação de status, não bloqueia edições.

### 10. Os cálculos são automáticos?

**Resposta:** Sim! Todos os cálculos são feitos automaticamente durante o processamento. Você não precisa calcular nada manualmente.

---

## 🎯 DICAS IMPORTANTES

### ✅ Boas Práticas

1. **Sempre valide os dados** antes de finalizar uma movimentação
2. **Use os filtros** para encontrar informações específicas rapidamente
3. **Exporte relatórios** regularmente para backup
4. **Verifique os totais** na parte inferior da tabela
5. **Mantenha os arquivos originais** (SPED e XML) como backup

### ⚠️ Cuidados

1. **Não exclua empresas** que já têm movimentações processadas
2. **Verifique os valores rateados** para garantir que estão corretos
3. **Confirme a correspondência** entre SPED e XML antes de finalizar
4. **Revise os impostos** calculados pelo sistema
5. **Salve as edições** antes de sair da página

### 🔍 Verificações Recomendadas

Após processar arquivos, verifique:

1. ✅ Quantidade de produtos processados está correta?
2. ✅ Valores totais fazem sentido?
3. ✅ Impostos estão sendo calculados corretamente?
4. ✅ Rateios estão distribuídos igualmente?
5. ✅ Não há produtos duplicados?
6. ✅ Status dos produtos está correto (C/N, S/N, S/CADASTRO)?

---

## 📞 SUPORTE

Se você encontrar problemas ou tiver dúvidas:

1. Verifique se os arquivos estão no formato correto (.txt para SPED, .xml para XML)
2. Confirme que a empresa está cadastrada no sistema
3. Verifique o tamanho dos arquivos (máximo 10MB por XML)
4. Revise os logs de erro (se disponíveis)
5. Entre em contato com o suporte técnico

---

## 📝 RESUMO DOS CÁLCULOS

Para referência rápida, aqui está um resumo das fórmulas principais:

### Valor Unitário
```
Valor Unitário = Valor do Produto ÷ Quantidade
```

### Impostos do Item (SPED)
```
Impostos = IPI + ST - Desconto
```

### Valor para Rateio
```
Valor para Rateio = Frete + Seguro + Despesas + Outros - Desconto
```

### Valor Rateado por Item
```
Valor Rateado = Valor para Rateio ÷ Quantidade de Itens
```

### Valor Total do Produto
```
Valor Total = Valor do Produto + Valor Rateado + Impostos
```

### ICMS (quando calculado)
```
ICMS = Base de Cálculo × (Alíquota ÷ 100)
```

---

## 🎉 CONCLUSÃO

Agora você está pronto para usar o **SG-ECREDAC** com confiança! 

Lembre-se:
- O sistema faz os cálculos automaticamenteocê pode editar dados quando nec
- Vessário
- Sempre valide antes de finalizar
- Exporte relatórios regularmente

**Bom trabalho!** 🚀

---

**Versão do Manual:** 1.0  
**Data:** 2025  
**Sistema:** SG-ECREDAC

