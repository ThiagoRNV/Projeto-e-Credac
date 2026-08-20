from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import os

respostas = {
    # === CADASTRO ===
    'pergunta1': '''Ótima pergunta! Para cadastrar um novo produto manualmente, siga estes passos:

1. Acesse o menu "Cadastro" → "Produtos" → "Cadastro Manual"
2. Preencha os campos obrigatórios:
   - Empresa (selecione da lista)
   - Código do Produto
   - Descrição do Produto
   - Unidade de Medida
   - Tipo de Produto
   - Gênero
   - NCM (Nomenclatura Comum do Mercosul)
   - Saldo Inicial (opcional)
   - Saldo Inicial ICMS (opcional)

3. Clique em "Salvar" para finalizar o cadastro.

💡 **Dica**: Você também pode importar produtos através de arquivos SPED, que serão processados automaticamente pelo sistema.''',
    
    'pergunta2': '''Para cadastrar uma nova empresa no sistema, você tem duas opções:

**Opção 1 - Cadastro Manual:**
1. Acesse "Cadastro" → "Empresas" → "Nova Empresa"
2. Preencha os dados da empresa:
   - Razão Social
   - CNPJ
   - Inscrição Estadual
   - UF
   - Endereço completo
   - Telefone
   - Método de Rateio (Direto/Indireto)
3. Clique em "Salvar"

**Opção 2 - Importar via SPED:**
1. Acesse "Cadastro" → "Empresas" → "Cadastrar via SPED"
2. Selecione o arquivo .txt do SPED
3. O sistema extrairá automaticamente os dados da empresa

💡 **Importante**: O CNPJ é único e serve como identificador principal.''',
    
    'pergunta3': '''Para visualizar o histórico de processamentos, siga estes passos:

1. Acesse o menu "Histórico" no sistema
2. Você verá uma lista de todos os arquivos processados
3. As informações incluem:
   - Data do processamento
   - Nome do arquivo
   - Status (Sucesso/Erro)
   - Empresa relacionada

💡 **Dica**: O histórico ajuda a rastrear todas as operações realizadas no sistema, facilitando a auditoria e controle.''',
    
    # === VALIDAÇÃO ===
    'pergunta4': '''A validação de dados é uma funcionalidade essencial do sistema! Aqui está como funciona:

**O que é validado:**
- Produtos cadastrados vs produtos no SPED
- Notas fiscais e seus itens
- Participantes (clientes/fornecedores)
- Consistência dos dados fiscais

**Como usar:**
1. Primeiro, faça o upload dos arquivos XML ou SPED na seção "Validação" → "Upload de Movimentações"
2. Selecione a empresa e a data de referência
3. O sistema processará e validará automaticamente
4. Acesse "Validação" → "Dados Validados" para ver os resultados

**Status possíveis:**
- ✅ Pendente: Aguardando processamento
- 🔄 Em andamento: Sendo processado
- ✅ Concluído: Validação finalizada

💡 **Importante**: A validação garante a integridade dos dados antes da geração do arquivo e-CredAc.''',
    
    'pergunta5': '''Para fazer upload de arquivos XML ou SPED, siga estas instruções:

**Upload de XML:**
1. Acesse "Validação" → "Upload de Movimentações"
2. Selecione a empresa
3. Escolha a data de referência
4. Clique em "📁 Arquivos Individuais" ou "📂 Pasta Completa"
5. Selecione os arquivos XML (ou arraste e solte)
6. Aguarde o processamento

**Upload de SPED:**
1. Acesse "Cadastro" → "Empresas" → "Cadastrar via SPED"
2. Selecione o arquivo .txt do SPED
3. O sistema processará automaticamente

**Limites:**
- Máximo de 1000 arquivos por upload
- Tamanho máximo: 10MB por arquivo
- Tamanho total: até 50MB

💡 **Dica**: Você pode fazer upload de uma pasta inteira com múltiplos arquivos XML de uma vez!''',
    
    # === RATEIO ===
    'pergunta6': '''O método de rateio é usado para distribuir custos (frete, seguro, descontos) entre os itens de uma nota fiscal. Veja como funciona:

**Tipos de Rateio:**
- **Direto**: Rateio proporcional ao valor de cada item
- **Indireto**: Rateio igualitário entre todos os itens

**Como processar:**
1. Acesse "Rateio" → "Menu"
2. Selecione a empresa
3. Informe a data de referência
4. Faça upload da planilha de custo (formato Excel)
5. O sistema processará e aplicará o rateio automaticamente

**O que é rateado:**
- Valor do frete
- Valor do seguro
- Outros custos
- Descontos

💡 **Importante**: O rateio é calculado automaticamente durante o processamento dos XMLs, garantindo a distribuição correta dos custos.''',
    
    # === CONVERSÃO ===
    'pergunta7': '''Para gerar o arquivo e-CredAc, siga estes passos:

1. Acesse "Gerar Arquivo" → "e-CredAc"
2. Selecione a empresa
3. Escolha o mês de referência
4. (Opcional) Importe arquivos XML ou SPED adicionais
5. Selecione o método de rateio (se aplicável)
6. Clique em "Gerar Arquivo"

**O que o sistema faz:**
- Consolida todos os dados validados
- Aplica os métodos de rateio configurados
- Gera o arquivo no formato e-CredAc
- Disponibiliza para download

**Pré-requisitos:**
- Empresa cadastrada
- Dados validados
- Produtos cadastrados

💡 **Dica**: Certifique-se de que todas as validações foram concluídas antes de gerar o arquivo final.''',
    
    # === PRODUTOS SPED ===
    'pergunta8': '''Os produtos do SPED são importados automaticamente quando você faz upload de arquivos SPED. Veja como funciona:

**Importação Automática:**
1. Ao fazer upload de um arquivo SPED, o sistema extrai automaticamente:
   - Código do produto
   - Descrição
   - NCM, CFOP, CST
   - Valores e quantidades
   - Informações de ICMS, IPI, PIS

**Visualização:**
- Acesse "Cadastro" → "Produtos" → "Lista SPED"
- Você verá todos os produtos importados
- Pode editar ou excluir produtos individualmente

**Diferença entre Manual e SPED:**
- **Manual**: Produtos cadastrados manualmente pelo usuário
- **SPED**: Produtos extraídos automaticamente dos arquivos SPED

💡 **Importante**: Produtos do SPED são vinculados à empresa e data específicas do arquivo processado.''',
    
    # === PROBLEMAS COMUNS ===
    'pergunta9': '''Se você está tendo problemas com upload de arquivos, verifique:

**Problemas comuns e soluções:**

1. **Erro "Arquivo muito grande"**
   - Limite: 10MB por arquivo
   - Solução: Divida arquivos grandes ou use compressão

2. **Erro "Formato inválido"**
   - XML deve ser válido e no formato NFe
   - SPED deve ser arquivo .txt
   - Verifique se o arquivo não está corrompido

3. **Erro "Número de arquivos excedido"**
   - Limite: 1000 arquivos por upload
   - Solução: Faça uploads em lotes menores

4. **Arquivo não processa**
   - Verifique se a empresa está cadastrada
   - Confirme se o arquivo não está duplicado
   - Verifique os logs de erro no sistema

💡 **Dica**: Sempre verifique se os arquivos estão no formato correto antes do upload.''',
    
    'pergunta10': '''Para editar um produto cadastrado, siga estas instruções:

**Produtos Manuais:**
1. Acesse "Cadastro" → "Produtos" → "Lista Manual"
2. Localize o produto na lista
3. Clique no botão "Editar"
4. Modifique os campos desejados
5. Clique em "Salvar"

**Produtos SPED:**
1. Acesse "Cadastro" → "Produtos" → "Lista SPED"
2. Localize o produto
3. Clique em "Editar"
4. Modifique os campos (cuidado com dados fiscais)
5. Salve as alterações

**Importante:**
- Alterações em produtos SPED podem afetar validações
- Sempre verifique a consistência após edições
- Produtos vinculados a validações concluídas podem ter restrições

💡 **Dica**: Use os filtros de busca para localizar produtos rapidamente.''',
    
    'pergunta11': '''Para excluir uma empresa, você precisa ter cuidado, pois isso pode afetar dados relacionados:

**Como excluir:**
1. Acesse "Cadastro" → "Empresas" → "Lista de Empresas"
2. Localize a empresa desejada
3. Clique no botão "Excluir"
4. Confirme a exclusão

**⚠️ Atenção:**
- A exclusão de uma empresa também remove:
  - Todos os produtos vinculados
  - Validações relacionadas
  - Histórico de processamentos
  - Dados de rateio

**Recomendações:**
- Faça backup antes de excluir
- Verifique se não há validações em andamento
- Confirme que realmente deseja excluir todos os dados relacionados

💡 **Dica**: Considere desativar a empresa ao invés de excluir, se possível.''',
    
    'pergunta12': '''O sistema oferece várias formas de filtrar e buscar informações:

**Filtros disponíveis:**
- Por empresa
- Por data de referência
- Por tipo de nota
- Por código de produto
- Por NCM, CFOP, CST
- Por CNPJ/CPF
- Por número da nota

**Como usar:**
1. Acesse a página desejada (Produtos, Validação, etc.)
2. Use os campos de filtro no topo da página
3. Digite os critérios de busca
4. Os resultados serão filtrados automaticamente

**Busca avançada:**
- Combine múltiplos filtros
- Use paginação para navegar em grandes listas
- Exporte resultados quando necessário

💡 **Dica**: Os filtros são salvos durante a sessão, facilitando consultas repetidas.''',
}   


@csrf_exempt
def help(request):
    if request.method == 'POST':
       data = json.loads(request.body)
       pergunta = data.get('pergunta')

       resposta = respostas.get(pergunta, 'Desculpe, não encontrei uma resposta para essa pergunta.')
       return JsonResponse({'resposta': resposta})
    return render(request, 'help.html', {'respostas': respostas})
