# Refinamento — BL-0013 — Busca e padronização das telas de itens

## Rastreabilidade

- Item de backlog: [BL-0013](../backlog/items/BL-0013-filtrar-itens-lista-compra.md)
- Branch: `feature/BL-0013-filtrar-itens-lista-compra`
- Responsável pelo refinamento: Engenharia Jaci
- Estado do refinamento: `pronto_para_implementacao`
- Item relacionado: [BL-0011](../backlog/items/BL-0011-ampliar-cobertura-testes-ui.md), responsável pela futura infraestrutura Playwright

## Objetivo e critérios de sucesso

### Objetivo

Reduzir o esforço para localizar produtos em listas extensas e padronizar a
navegação por categorias das compras agendada, em andamento e finalizada, com
um filtro local, acessível, mobile-first e resiliente a atualizações dinâmicas.

### Critérios de sucesso

1. Lista, Compra agendada, Compra em andamento e Compra finalizada permitem
   buscar itens por trecho do nome, ignorando caixa, acentos e espaços nas
   extremidades.
2. Categorias sem correspondência são ocultadas, contadores refletem os itens
   visíveis e uma mensagem acessível informa quando não há resultados.
3. A busca expande categorias correspondentes e, ao ser limpa, restaura a
   visualização e o estado de collapse anterior.
4. Compras agendada, em andamento e finalizada oferecem collapse individual e
   um controle global de expandir ou recolher categorias.
5. A Compra em andamento preserva o termo após atualizações HTMX, WebSocket e
   offline, sem depender de conexão contínua.
6. A Compra finalizada permanece somente leitura, e seus resumos financeiro e
   geral continuam representando toda a execução, independentemente do filtro.

## Escopo

### Incluído

- Componente JavaScript Vanilla compartilhado para normalização, filtragem,
  contadores, estado vazio e controle de collapse.
- Campo `search`, botão de limpeza e contrato DOM acessível baseado em
  atributos `data-*` nas quatro telas em escopo.
- Busca por nome nos itens planejados, comprados e não comprados.
- Collapse individual e global nas três telas de execução.
- Reaplicação automática da busca depois da substituição ou mutação do
  fragmento de itens da Compra em andamento.
- Padronização dos cards da Compra finalizada, incluindo o grupo especial
  "Não comprados" como conteúdo colapsável e pesquisável.
- Contratos Pytest compatíveis com a estratégia atual do repositório e
  rastreabilidade em `tests/README.md`.

### Excluído

- Busca por categoria, observações, local, quantidade ou valores financeiros.
- Consulta ao servidor, catálogo externo, paginação ou novo endpoint.
- Persistência do termo em sessão, banco, IndexedDB ou `localStorage`.
- Alteração de templates de compra, execuções existentes ou dados financeiros.
- Compras canceladas, telas de índice e demais telas fora dos detalhes citados.
- Criação de infraestrutura Playwright, acompanhada separadamente pela
  BL-0011.

## Riscos e regras preservadas

- Regras de negócio afetadas: somente apresentação; preservar imutabilidade de
  execuções finalizadas, histórico e independência entre template e execução.
- Segurança e permissões: operar exclusivamente sobre o DOM já retornado pelas
  rotas autorizadas; não criar consultas nem aceitar IDs novos do cliente.
- LGPD: normalizar o termo somente em memória e não registrar, transmitir ou
  persistir o texto pesquisado.
- Isolamento por grupo: preservar as rotas e consultas existentes; o filtro
  não pode introduzir acesso a itens não renderizados para o grupo ativo.
- Offline e sincronização: funcionar sem rede e reaplicar o termo após HTMX,
  WebSocket ou mutações offline; WebSocket continua apenas visual.
- Histórico financeiro: manter orçamento, total gasto e resumo lateral com os
  totais completos; somente indicadores internos de grupos refletem o filtro.
- Recorrência: `N/A` — nenhuma mudança em datas, status ou geração futura.
- Separação entre template e execução: manter instâncias independentes; a
  filtragem não modifica nem propaga itens.

## Plano de implementação

### Etapa 1 — Busca local e navegação padronizada

#### Ticket 1.1 — Entregar o filtro compartilhado nas telas de itens

##### Fatia 1.1.1 — Criar contratos TDD e integrar a Lista

- Ordem: `1`
- Objetivo da fatia: escrever os contratos executáveis do escopo completo,
  criar o componente compartilhado e ativar a busca no detalhe da Lista.
- Dependências: aprovação explícita deste refinamento.
- Arquivos esperados:
  - `tests/test_item_filter.py`
  - `app/static/js/item-filter.js`
  - `app/templates/pages/templates/detail.html`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_item_filter.py --no-cov`
  - validação manual da Lista em viewport móvel e desktop
- Documentação a atualizar:
  - este refinamento e o item `BL-0013`

##### Fatia 1.1.2 — Integrar Compras agendada e em andamento

- Ordem: `2`
- Objetivo da fatia: aplicar busca e collapse compartilhados ao fragmento de
  itens, preservando o termo e o estado do usuário durante atualizações
  dinâmicas.
- Dependências: fatia 1.1.1.
- Arquivos esperados:
  - `app/templates/pages/executions/in_progress.html`
  - `app/templates/pages/executions/_items_fragment.html`
  - `app/static/js/item-filter.js`
  - `tests/test_item_filter.py`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_item_filter.py tests/test_offline_cache.py --no-cov`
  - validação manual online e offline das compras agendada e em andamento
- Documentação a atualizar:
  - este refinamento e o item `BL-0013`

##### Fatia 1.1.3 — Padronizar a Compra finalizada

- Ordem: `3`
- Objetivo da fatia: adicionar busca, collapse individual/global e grupo
  colapsável de itens não comprados, preservando os totais históricos globais.
- Dependências: fatias 1.1.1 e 1.1.2.
- Arquivos esperados:
  - `app/templates/pages/executions/completed.html`
  - `app/static/js/item-filter.js`
  - `tests/test_item_filter.py`
  - `tests/README.md`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_item_filter.py --no-cov`
  - validação manual da Compra finalizada em viewport móvel e desktop
- Documentação a atualizar:
  - `tests/README.md`, este refinamento e o item `BL-0013`

## Cenários TDD

Estes cenários devem ser escritos como testes antes da implementação, depois
da aprovação do refinamento.

1. Dado um nome com caixa, acentos ou espaços diferentes, a busca encontra o
   item por qualquer trecho normalizado do nome.
2. Dado um termo ativo, linhas sem correspondência e categorias vazias ficam
   ocultas, e os contadores representam somente os itens visíveis.
3. Dado um termo sem correspondência, a tela mostra uma mensagem acessível e
   preserva resumos globais de quantidade e valores.
4. Dado um filtro limpo, todas as linhas e categorias reaparecem, os textos dos
   contadores originais retornam e o estado de collapse anterior é restaurado.
5. Dada uma categoria recolhida com item correspondente, a busca a expande sem
   persistir essa expansão forçada em `X-Collapse-State`.
6. Dado o controle global de collapse em qualquer tela de execução, ele expande
   ou recolhe somente os grupos de itens daquela tela.
7. Dada uma Compra agendada ou em andamento filtrada, uma substituição HTMX,
   atualização WebSocket ou mutação offline mantém o termo e reaplica o filtro
   aos itens atualizados.
8. Dada uma Compra em andamento filtrada, o cabeçalho da categoria recalcula
   comprados, itens visíveis e subtotal visível, enquanto orçamento e progresso
   globais permanecem inalterados.
9. Dada uma Compra finalizada, itens comprados e não comprados participam da
   busca; "Não comprados" funciona como grupo colapsável independente.
10. Dada uma Compra finalizada filtrada, o resumo lateral, o orçamento e o
    total gasto continuam representando toda a execução e nenhuma ação de
    mutação é introduzida.

### Contratos de etapas futuras

- Não há `xfail(strict=True)` planejado neste escopo. A cobertura em navegador
  real permanece futura e rastreada pela BL-0011; os contratos da BL-0013 usam
  a infraestrutura Pytest atualmente disponível.

## Estratégia de validação

### Por fatia

- Executar os contratos Pytest diretamente relacionados antes e depois de cada
  implementação.
- Executar `pylint --errors-only` caso algum arquivo Python existente seja
  alterado além dos contratos.
- Validar manualmente em viewport móvel e desktop os controles acessíveis,
  contadores, estado vazio e comportamento do Bootstrap Collapse.
- Na fatia dinâmica, validar conexão normal, ausência de conexão e substituição
  do fragmento sem perda do filtro.
- Atualizar item, refinamento e rastreabilidade ao concluir cada fatia.
- Não há migração de banco ou mudança de backend prevista.

### Validação manual

1. Abrir uma Lista com nomes acentuados em categorias distintas, buscar por
   trecho sem acento e confirmar grupos, contadores, limpeza e foco móvel.
2. Em Compra agendada e em andamento, alternar collapse individual/global,
   aplicar a busca e adicionar, editar, comprar ou remover um item, confirmando
   que o termo continua aplicado ao fragmento atualizado.
3. Repetir a operação da Compra em andamento sem conexão e confirmar que a
   busca continua local sobre o estado visual disponível.
4. Abrir uma Compra finalizada com itens comprados e não comprados, validar os
   dois grupos, collapse e busca, confirmando que resumo, orçamento e total
   gasto não mudam.
5. Limpar a busca em todas as telas e confirmar a restauração integral dos
   itens, grupos, contadores e estados anteriores.

### Regressão total

Executar quando as três fatias estiverem concluídas e não houver contratos
pendentes:

- `timeout 240 venv/bin/pytest`
- UI Playwright: não disponível no estado atual do Jaci; acompanhamento pela
  BL-0011 e validação manual obrigatória nesta demanda.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 / Ticket 1.1 — Busca e padronização | `0/3` | `3` | Pendente de aprovação |

## Fechamento

- Commits/PRs: ainda não iniciados
- Resultado das validações focadas: ainda não iniciadas
- Resultado da validação manual: ainda não iniciada
- Resultado da regressão total: ainda não iniciada
- `xfail(strict=True)` pendentes no escopo: nenhum planejado
- Documentação atualizada: item, índice e este refinamento
- Publicação: ainda não publicada
