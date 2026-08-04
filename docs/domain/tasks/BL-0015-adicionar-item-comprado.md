# Refinamento — BL-0015 — Adicionar item como comprado durante execução

## Rastreabilidade

- Item de backlog: [BL-0015](../backlog/items/BL-0015-adicionar-item-comprado.md)
- Branch: `feature/BL-0015-adicionar-item-comprado`
- Responsável pelo refinamento: Engenharia Jaci
- Estado do refinamento: `em_implementacao`
- Itens relacionados: `BL-0011`, `BL-0013`, `BL-0014` e `BL-0016`

## Objetivo e critérios de sucesso

### Objetivo

Eliminar a segunda ação necessária para registrar um produto encontrado durante
uma compra em andamento, persistindo-o de uma só vez como comprado e mantendo
paridade confiável entre o fluxo online e o estado local offline.

### Critérios de sucesso

1. Em uma execução `em_andamento`, o formulário exige valor unitário maior que
   zero e usa a quantidade informada como planejada e comprada.
2. O item é persistido atomicamente como concluído, com versão inicial `1`, e
   passa a compor progresso, total gasto e alertas de orçamento imediatamente.
3. Em uma execução `agendada`, a inclusão continua criando item pendente sem
   quantidade comprada ou valor unitário.
4. Sem conexão, o item temporário aparece como comprado, atualiza progresso,
   total e alerta provisórios e permanece na fila até a API remota confirmar a
   operação.
5. A sincronização substitui o ID temporário pelo ID remoto sem duplicar o item
   e trata explicitamente a execução que tenha sido finalizada ou cancelada.
6. A categoria e a execução continuam limitadas ao grupo autorizado, e o item
   adicionado nunca altera o template automaticamente.
7. WebSocket continua apenas visual: falha no broadcast não desfaz nem impede a
   persistência online ou a reconciliação offline.

## Escopo

### Incluído

- Campo de valor unitário, obrigatório somente ao adicionar item em compra
  `em_andamento`, com mínimo de `0,01`.
- Uso da quantidade já existente como `planned_quantity` e
  `purchased_quantity` para o novo item comprado, sem criar outra etapa ou
  outro campo de quantidade.
- Persistência atômica do item, dados financeiros, estado concluído e versão.
- Validação do estado da execução no serviço, na rota HTML e na API de
  sincronização, sem confiar em estado informado pelo cliente.
- Atualização online do fragmento, resumo financeiro, progresso, alerta de
  orçamento e evento visual após a persistência.
- Extensão do payload offline de adição com `unit_price` e da resposta com
  `is_completed`, `purchased_quantity`, `unit_price` e dados suficientes para
  reconciliar o item temporário.
- Persistência IndexedDB, renderização local do item comprado, totais e alerta
  provisórios, fila, retentativa e reconciliação sem duplicação.
- Atualização da versão do cache do service worker para distribuir o novo
  contrato JavaScript.

### Excluído

- Migração ou novo campo no banco de dados.
- Campo novo de local de compra no formulário de adição; o item nasce com
  `location` nulo e pode ser editado pelo fluxo existente.
- Valor unitário igual a zero ou negativo.
- Alteração automática do template, de recorrência ou de execuções existentes.
- Catálogo de produtos, leitura de código de barras ou sugestões de preço.
- Criação de infraestrutura Playwright; a BL-0011 continua responsável por
  essa capacidade e esta demanda exige validação manual em navegador.

## Riscos e regras preservadas

- Regras de negócio afetadas: o item incluído durante `em_andamento` passa a
  nascer comprado; em `agendada`, permanece planejado. Execuções finalizadas e
  canceladas não aceitam inclusão.
- Segurança e permissões: manter autenticação e autorização da execução antes
  da mutação; IDs e estado enviados pelo cliente não são fonte de autorização.
- LGPD: não introduzir dados pessoais nem registrar payloads financeiros ou
  textos de usuário em logs além dos padrões sanitizados existentes.
- Isolamento por grupo: validar a execução pelo usuário autenticado e conferir
  que `category_id` pertence ao mesmo grupo em todos os caminhos.
- Offline e sincronização: IndexedDB é a primeira fonte de verdade durante a
  desconexão; a fila preserva quantidade e valor, e a API remota confirma ou
  retorna conflito sem sobrescrita silenciosa.
- Histórico financeiro: quantidade comprada e valor unitário entram juntos no
  item e no total. O total local é provisório até ser substituído pelo estado
  canônico após a sincronização.
- Recorrência: `N/A` — nenhuma mudança em finalização, data-base ou criação do
  próximo ciclo.
- Separação entre template e execução: o novo item mantém
  `template_item_id = null`; sugestões ao finalizar continuam manuais.

## Plano de implementação

### Etapa 1 — Inclusão de item comprado com paridade online e offline

#### Ticket 1.1 — Persistir e sincronizar o item em uma única ação

##### Fatia 1.1.1 — Contratos TDD e fluxo online atômico

- Ordem: `1`
- Objetivo da fatia: escrever os contratos executáveis do escopo completo e
  implementar a regra de estado, o formulário e a persistência online do item
  comprado, com total, orçamento e broadcast posteriores ao commit.
- Dependências: aprovação explícita deste refinamento.
- Arquivos esperados:
  - `tests/test_business_rules.py`
  - `tests/test_template_execution_flow.py`
  - `tests/test_user_flows.py`
  - `tests/test_execution_totals_regression.py`
  - `tests/test_offline_cache.py`
  - `app/services/execution_service.py`
  - `app/routers/executions.py`
  - `app/templates/pages/executions/in_progress.html`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_business_rules.py tests/test_template_execution_flow.py tests/test_execution_totals_regression.py tests/test_offline_cache.py`
  - `timeout 180 env PYTHONPATH=. venv/bin/pylint app/services/execution_service.py app/routers/executions.py --errors-only`
  - validação manual online em viewport móvel e desktop
- Documentação a atualizar:
  - este refinamento e o item `BL-0015`

##### Fatia 1.1.2 — Estado local, sincronização e reconciliação offline

- Ordem: `2`
- Objetivo da fatia: retirar os contratos offline de `xfail(strict=True)`,
  persistir e renderizar o item comprado localmente, atualizar resumo e alerta
  provisórios, sincronizar o payload e reconciliar o ID temporário.
- Dependências: fatia 1.1.1.
- Arquivos esperados:
  - `app/routers/offline.py`
  - `app/static/js/offline-cache.js`
  - `app/static/js/service-worker.js`
  - `tests/test_offline_cache.py`
  - `tests/test_sync_center.py`
  - `tests/test_sync_status.py`
  - `tests/test_pwa.py`
- Validações focadas:
  - `node --check app/static/js/offline-cache.js`
  - `node --check app/static/js/service-worker.js`
  - `timeout 180 venv/bin/pytest tests/test_offline_cache.py tests/test_sync_center.py tests/test_sync_status.py tests/test_pwa.py`
  - `timeout 180 env PYTHONPATH=. venv/bin/pylint app/routers/offline.py --errors-only`
  - validação manual offline, reconexão e reconciliação em viewport móvel
- Documentação a atualizar:
  - este refinamento e o item `BL-0015`

## Cenários TDD

Estes cenários devem ser escritos como testes antes da implementação, depois da
aprovação explícita deste refinamento.

1. Dada uma execução agendada, adicionar um item mantém
   `is_completed = false`, `purchased_quantity = null` e `unit_price = null`.
2. Dada uma execução em andamento, adicionar nome, quantidade e valor maior que
   zero cria atomicamente o item concluído, usa a mesma quantidade como
   planejada e comprada e inicia a versão em `1`.
3. Dada uma execução em andamento sem valor, com valor zero ou negativo, o
   serviço, a rota HTML e a API offline rejeitam a inclusão sem persistência
   parcial.
4. Dada uma execução finalizada ou cancelada, qualquer caminho de inclusão
   falha explicitamente e não altera o histórico.
5. Dada uma categoria de outro grupo, a inclusão online e offline é rejeitada;
   usuário sem vínculo com o grupo não acessa a execução.
6. Dado um item incluído em execução ligada a template, ele permanece sem
   `template_item_id` e o template não é alterado.
7. Dado o novo item comprado online, seu total entra no total gasto e no
   progresso, o alerta de orçamento é recalculado e o broadcast ocorre somente
   depois da persistência.
8. Dada uma execução agendada, o formulário não exige nem envia valor; dada uma
   execução em andamento, exibe valor unitário obrigatório com mínimo `0,01`.
9. Dada uma inclusão sem conexão, a operação guarda quantidade e valor na fila,
   o registro temporário nasce concluído e a lista o mostra como comprado.
10. Dado o item comprado offline, progresso, total gasto e alerta de orçamento
    provisórios são atualizados sem depender de WebSocket ou API disponível.
11. Dada a sincronização bem-sucedida, o retorno remoto contém os campos
    financeiros e substitui o ID temporário sem deixar item duplicado.
12. Dada uma execução finalizada ou cancelada antes da sincronização, a API
    registra conflito, mantém a operação local rastreável e não sobrescreve o
    estado remoto.
13. Dada uma falha transitória de rede ou broadcast, a operação permanece na
    fila/servidor conforme sua fonte de verdade e é reconciliada na retentativa.
14. Dada a publicação do JavaScript atualizado, a nova versão do cache PWA
    invalida o shell anterior e entrega o contrato offline vigente.

### Contratos de etapas futuras

- Os cenários 9 a 14 permanecem com `xfail(strict=True)` durante a fatia 1.1.1
  e devem ser ativados na fatia 1.1.2.
- Não há outro `xfail(strict=True)` planejado no escopo ao fechar o ticket.
- A cobertura Playwright permanece futura na BL-0011; esta demanda não cria
  arquivos em `tests/ui`.

## Estratégia de validação

### Por fatia

- Executar primeiro os contratos diretamente relacionados e repetir após a
  implementação mínima da fatia.
- Executar lint dos arquivos Python alterados e verificação sintática dos
  arquivos JavaScript.
- Confirmar que não foi criada migração e executar o banco de testes no head.
- Validar manualmente o formulário mobile-first, a atualização HTMX e os
  estados local, enfileirado, sincronizado e em conflito.
- Atualizar item, refinamento, commits, resultados e progresso ao concluir cada
  fatia.

### Validação manual

1. Em compra agendada, adicionar item e confirmar que permanece pendente e sem
   valor financeiro.
2. Em compra em andamento online, adicionar item com quantidade e valor e
   confirmar em uma ação o estado comprado, subtotal, progresso, total e alerta.
3. Repetir sem conexão e confirmar item temporário visível, badge de pendência,
   totais e alerta provisórios.
4. Restabelecer a conexão e confirmar reconciliação sem duplicação e substituição
   pelos totais canônicos do servidor.
5. Simular finalização por outro membro antes da sincronização e confirmar
   conflito explícito sem perda da operação local.
6. Confirmar em viewport móvel que apenas o valor unitário foi acrescentado ao
   fluxo e que não há segunda etapa obrigatória.

### Regressão total

Executar quando as duas fatias estiverem concluídas e nenhum contrato deste
ticket permanecer em `xfail(strict=True)`:

- `venv/bin/alembic upgrade head`
- `timeout 240 venv/bin/pytest`
- UI Playwright: infraestrutura ainda não disponível no Jaci; registrar a
  validação manual e manter a cobertura futura na BL-0011.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 / Ticket 1.1 — Inclusão comprada online/offline | `1/2` | `1` | Em andamento |

## Fechamento

- Commits/PRs: fatia 1.1.1 implementada; commit a registrar.
- Resultado das validações focadas: fatia 1.1.1 com 54 testes aprovados e 3
  contratos offline em `xfail(strict=True)`; `git diff --check` aprovado;
  `pylint` não está instalado no ambiente virtual.
- Resultado da validação manual: ainda não executada.
- Resultado da regressão total: ainda não executada.
- `xfail(strict=True)` pendentes no escopo: 3 contratos da fatia 1.1.2 em
  `tests/test_offline_cache.py` e 1 contrato de cache PWA em
  `tests/test_pwa.py`.
- Documentação atualizada: item, índice e este refinamento.
