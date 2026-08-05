# Refinamento — BL-0020 — Bloquear renomeação de item vinculado ao template

## Rastreabilidade

- Item de backlog: [BL-0020](../backlog/items/BL-0020-bloquear-renomeacao-item-vinculado.md)
- Branch: `feature/BL-0020-bloquear-renomeacao-item-vinculado`
- Responsável pelo refinamento: Engenharia Jaci
- Estado do refinamento: `em_validacao`
- Itens relacionados: `BL-0003`, `BL-0005` e `BL-0011`
- Decisões de produto: nome vinculado visível em modo somente leitura; troca de
  produto usa remoção e adição; divergências históricas são preservadas.
- Aprovação de implementação: emitida explicitamente em `2026-08-05`, depois
  do commit documental `0fd7aaa`.

## Objetivo e critérios de sucesso

### Objetivo

Preservar a identidade de itens originados de templates para que um produto
diferente não seja registrado sob o mesmo `template_item_id`, protegendo
análises de preço, frequência e quantidade sem reduzir a edição dos demais
atributos da execução.

### Critérios de sucesso

1. Item com `template_item_id` conserva exatamente o nome de seu snapshot em
   edições agendadas e em andamento, online e offline.
2. Quantidade planejada, categoria e observações continuam editáveis sem
   renomear o item nem alterar o template.
3. Item sem `template_item_id` continua renomeável pelos contratos atuais.
4. A interface exibe o nome vinculado como somente leitura e orienta remover e
   adicionar quando o produto desejado for outro.
5. POST adulterado falha com `422`, sem mutação, incremento de versão ou evento
   Socket.IO.
6. Operação offline antiga que tente renomear gera conflito `409` auditável,
   preserva a fila e expõe o estado remoto para resolução explícita.
7. Nenhum nome histórico é reescrito e nenhuma mudança de modelo ou migração é
   introduzida.

## Escopo

### Incluído

- Invariante de nome centralizada no serviço de edição de item de execução.
- Rejeição explícita de adulteração no adaptador HTML e na API offline.
- Estado remoto do conflito incluindo `template_item_id` e motivo estável
  `linked_template_item_name_immutable`.
- Nome somente leitura com ajuda contextual no modal server-rendered.
- Alternância segura entre somente leitura e editável no modal offline
  compartilhado, baseada em `data-template-item-id`.
- Compatibilidade de payload: atualizações válidas continuam enviando o nome
  atual para editar os demais campos.
- Atualização da versão do cache PWA e dos contratos de documentação/testes.
- Cenário Playwright futuro registrado para `BL-0011`, sem criar a
  infraestrutura nesta demanda.

### Excluído

- Impedir remoção ou adição de itens durante a execução.
- Propagar alterações entre template e execuções já criadas.
- Comparar o snapshot com o nome atual do item do template.
- Corrigir, migrar, excluir ou sinalizar automaticamente divergências
  históricas já persistidas.
- Alterar preço, quantidade comprada, recorrência, status ou cálculos
  financeiros.
- Criar triggers, constraints de banco, migrações ou infraestrutura Playwright.

## Riscos e regras preservadas

- Regras de negócio afetadas: quando `template_item_id IS NOT NULL`, o nome do
  snapshot torna-se imutável; itens avulsos permanecem editáveis. Se a FK ficar
  nula pelo comportamento `ON DELETE SET NULL`, o item passa a seguir a regra
  avulsa existente.
- Segurança e permissões: a regra reside no serviço e é aplicada depois do
  carregamento autorizado por execução; POST/API adulterados não contornam a
  interface.
- LGPD: nenhum dado novo é coletado. Auditoria offline conserva somente estados
  já usados pelo fluxo e permanece isolada por usuário/grupo.
- Isolamento por grupo: `get_execution_by_id` e a associação item/execução
  existentes permanecem obrigatórios; não haverá consulta nova sem filtro.
- Offline e sincronização: a UI nova não cria renomeações vinculadas. Operação
  antiga divergente vira conflito explícito, não repetição silenciosa nem perda
  da intenção local.
- Histórico financeiro: nenhuma linha passada é modificada. O bloqueio reduz
  contaminação futura de preço e quantidade associados ao item errado.
- Recorrência: `template_id`, datas, finalização e geração futura não mudam.
- Separação entre template e execução: o nome protegido é o snapshot atual da
  execução, não o nome vigente do template; edições continuam sem propagação.

## Plano de implementação

### Etapa 1 — Proteger a identidade do item online e offline

#### Ticket 1.1 — Aplicar a invariante em todos os adaptadores

##### Fatia 1.1.1 — Contratos TDD e implementação completa

- Ordem: `1`
- Objetivo da fatia: escrever os contratos executáveis de todo o escopo e
  entregar a regra de domínio, respostas explícitas, UX somente leitura,
  conflito offline e distribuição PWA em uma unidade coerente.
- Dependências: aprovação explícita deste refinamento versionado.
- Arquivos esperados:
  - `tests/test_business_rules.py`
  - `tests/test_template_execution_flow.py`
  - `tests/test_offline_cache.py`
  - `tests/test_pwa.py`
  - `app/services/execution_service.py`
  - `app/routers/executions.py`
  - `app/routers/offline.py`
  - `app/templates/pages/executions/_edit_modal.html`
  - `app/templates/pages/executions/_items_fragment.html`
  - `app/templates/base.html`
  - `app/static/js/offline-cache.js`
  - `app/static/js/service-worker.js`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_business_rules.py tests/test_template_execution_flow.py tests/test_offline_cache.py tests/test_pwa.py`
  - `node --check app/static/js/offline-cache.js`
  - `node --check app/static/js/service-worker.js`
  - `timeout 180 env PYTHONPATH=. venv/bin/pylint app/services/execution_service.py app/routers/executions.py app/routers/offline.py --errors-only`
  - validação manual online/offline em viewport móvel
- Documentação a atualizar:
  - `tests/README.md`
  - item e refinamento `BL-0020`

## Cenários TDD

Estes cenários devem ser escritos como testes antes da implementação, depois da
aprovação explícita deste refinamento.

1. Dado item com `template_item_id`, solicitar nome diferente no serviço falha
   sem modificar nome, demais campos ou versão.
2. Dado item vinculado e o mesmo nome exato, alterar quantidade planejada,
   categoria e observações funciona e incrementa a versão uma vez.
3. Dado item sem `template_item_id`, alterar o nome continua funcionando.
4. Dada execução finalizada ou cancelada, a imutabilidade geral continua tendo
   precedência e nenhuma edição é aceita.
5. Dado POST HTML adulterado para item vinculado, a rota responde `422`, não
   persiste parcialmente e não transmite `item_updated`.
6. Dado o modal online de item vinculado, o nome aparece como `readonly`, é
   enviado com o formulário e possui ajuda explicando remoção/adição; item
   avulso mantém o campo editável.
7. Dado o botão offline, `template_item_id` é exposto ao controlador; ao abrir
   itens vinculados e avulsos alternadamente, o modal ativa e remove
   `readonly` e a ajuda sem vazar estado entre aberturas.
8. Dada atualização offline válida de item vinculado com nome atual, os demais
   campos sincronizam normalmente.
9. Dada atualização offline divergente de item vinculado, a API retorna `409`
   com `reason=linked_template_item_name_immutable`, cria auditoria isolada,
   inclui `template_item_id` no estado remoto e não altera o item.
10. Dada uma operação divergente na fila, o cliente mantém a pendência e a
    apresenta para resolução explícita pelo fluxo de conflitos existente.
11. Dada a nova versão do shell PWA, clientes deixam de reutilizar o JavaScript
    antigo que permitia editar o nome vinculado.

### Contratos de etapas futuras

- Não haverá `xfail(strict=True)` no escopo executável da fatia única.
- A `BL-0011` deve cobrir futuramente em Playwright, com dados do grupo
  autenticado: abrir compra vinculada online e offline, confirmar nome somente
  leitura e ajuda visível, editar quantidade/observações, reconectar e validar
  persistência; abrir item avulso e confirmar que o nome permanece editável.

## Estratégia de validação

### Por fatia

- Escrever todos os contratos de serviço, rota, renderização, offline e PWA
  antes de alterar comportamento de produção.
- Implementar a invariante no serviço e manter rotas como adaptadores.
- Executar testes focados e verificações sintáticas dos dois arquivos
  JavaScript.
- Executar lint dos módulos Python tocados; registrar indisponibilidade do
  `pylint` como limitação ambiental, se ocorrer.
- Confirmar ausência de migração, reescrita histórica e arquivos `tests/ui`.
- Executar `venv/bin/graphify update .` após as mudanças de código.
- Atualizar item, índice, matriz de testes e progresso antes do commit técnico.

### Validação manual

1. Em viewport móvel, abrir uma execução agendada vinculada e confirmar nome
   visível somente para leitura, ajuda contextual e demais campos editáveis.
2. Repetir em execução em andamento, alterar quantidade e observações e
   confirmar que o nome e o template permanecem intactos.
3. Remover um item vinculado ainda pendente, adicionar outro produto e confirmar
   que o novo item avulso permite renomeação.
4. Desconectar a rede, editar os demais campos de item vinculado, confirmar
   estado local/fila e reconciliar após reconectar sem alteração de nome.
5. Abrir alternadamente itens vinculados e avulsos no modal offline e confirmar
   que `readonly` e a ajuda não vazam entre itens.
6. Simular payload online e offline com nome diferente e confirmar rejeição
   explícita sem mutação parcial nem broadcast.

### Regressão total

Como a fatia única fecha todo o ticket, executar ao concluí-la e sem
`xfail(strict=True)` deste escopo:

- `venv/bin/alembic upgrade head`
- `timeout 240 venv/bin/pytest`
- Playwright: infraestrutura ausente no Jaci; manter o cenário futuro na
  `BL-0011` e executar a validação manual definida acima.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 / Ticket 1.1 — Identidade online/offline | `1/1` | `0` | Concluído |

## Fechamento

- Commits/PRs: commit técnico será registrado após consolidar esta
  rastreabilidade.
- Resultado das validações focadas: ciclo TDD inicial com 10 falhas esperadas e
  79 aprovações; após a implementação, 89 testes aprovados. `node --check`
  aprovou `offline-cache.js` e `service-worker.js`; compilação Python aprovada.
  O `pylint` não está instalado no venv.
- Resultado da validação manual: pendente de aceite em navegador; renderização,
  adaptadores HTMX e contratos offline possuem cobertura automatizada. A
  infraestrutura Playwright permanece futura na `BL-0011`.
- Resultado da regressão total: migrações no head; 235 testes aprovados e 5
  `xfail` legados fora do escopo.
- `xfail(strict=True)` pendentes no escopo: nenhum.
- Documentação atualizada: item, índice, matriz de testes e este refinamento;
  grafo AST-only reconstruído.
