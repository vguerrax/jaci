# Refinamento — BL-0001 — Rastreabilidade da operação offline

## Rastreabilidade

- Item: [BL-0001](../backlog/items/BL-0001-operacao-offline-cobertura-rastreabilidade.md).
- Versão-alvo: 1.4.0; responsável: Engenharia Jaci.
- Estado: em_validacao; refinamento versionado aprovado explicitamente pelo usuário.
- Branch documental: feature/BL-0001-refinamento-1-4-0, criada da develop.
  Preservar a branch anterior feature/BL-0001-operacao-offline-cobertura-rastreabilidade.
- Depois do merge documental, atualizar esta branch e usá-la para este item isolado.
  Não agregar demandas BL-0011/BL-0026; integração executável na develop só autorizada
  explicitamente. O item possui um ticket com duas fatias sequenciais nessa branch.

## Objetivo e critérios de sucesso

1. Documentar quais operações de execução funcionam offline e quais ainda exigem API.
2. Substituir os três contratos que importam app.services.sync_service inexistente,
   com evidência comportamental sobre a fila IndexedDB realmente implementada.
3. Preservar retenção local, ordem, reconexão, conflito explícito e isolamento.
4. Retirar apenas os três xfail legados FL-09 depois de seus substitutos passarem;
   manter os dois contratos FL-08 pendentes de BL-0003 e BL-0004.
5. Não ampliar a fila para templates, categorias, grupos ou novas operações.

## Escopo

Inclui reconciliação de contratos, rastreabilidade de regras/fluxos e documentação
PWA. Não recriar fila em Python, migrar arquitetura, alterar comportamento de
sincronização ou criar infraestrutura Playwright (BL-0011).

## Riscos e regras preservadas

- Segurança: autorização continua no servidor, inclusive para payload de cliente adulterado.
- LGPD: exemplos sintéticos; sem snapshots reais nem cookies em evidências.
- Grupo: fila/snapshot/auditoria não devem aceitar dados de grupo não autorizado.
- Offline: gravar localmente antes de enviar, manter ordem/retenção em falhas e conflito.
- Histórico: preservação de quantidade/preço/local/versão, sem sobrescrita silenciosa.
- Recorrência: finalização sincronizada gera ciclo a partir da conclusão, sem duplicação.
- Template/execução: sem propagação automática para planejamento.

## Plano de implementação

### Etapa 1 / Ticket 1 — Reconciliação completa

#### Fatia 1.1 — Contratos da implementação efetiva

- Arquivos esperados: tests/test_future_user_flows.py, tests/test_offline_cache.py,
  tests/js/offline_queue.test.cjs, package.json e package-lock.json de dependências
  estritamente de desenvolvimento, sem framework ou dependência frontend em produção.
- Usar Node test runner, VM e fake-indexeddb como dependência dev fixada por lockfile.
  Executar o JavaScript real offline-cache.js, acessando window.JaciOfflineCache;
  simular somente ambiente DOM/rede e inspecionar registros do IndexedDB de teste.
  Não criar funções de negócio exclusivas para satisfazer contratos legados.
- Wrapper Pytest chama Node e propaga erro/saída sanitizada; ausência de Node ou da
  dependência é falha com instrução de instalação, não skip que simula aprovação.
  Documentar npm ci para dev/CI; atualizar instalação no workflow da BL-0011 quando
  esta entrega for integrada depois dela, sem redefinir os jobs.
- Mapear test_fl09_offline_operation_is_queued_before_remote_sync: promessa de enqueue
  só resolve após persistir e sem envio com navigator offline; recarga do VM lê fila.
- Mapear test_fl09_reconnection_synchronizes_queued_operations_without_data_loss:
  reconectar e invocar syncPending, verificar payload/versão e remover apenas operação
  confirmada; em erro de rede reter item e ordem; não duplicar envio concorrente.
- Mapear test_fl09_sync_conflict_requires_explicit_resolution_and_preserves_both_versions:
  resposta 409 mantém payload local e estado remoto, não aplica overwrite nem descarta
  operação; correlacionar com testes existentes de auditoria/resolução de API.
- Escrever substitutos antes de remover contratos antigos. Depois que passarem,
  remover somente os três testes Python obsoletos e seus marcadores; manter histórico
  e links de substituição na matriz, sem alegar que a funcionalidade foi criada agora.
- Reutilizar os testes atuais de serviços de sincronização/autorização; não substituir
  asserts comportamentais por busca de strings ou testes que apenas importam módulos.
- Se os contratos revelarem defeito funcional real, registrar evidência e refinar a
  correção antes do código; não expandir silenciosamente esta demanda documental.

#### Fatia 1.2 — Documentação coerente e evidências

- Arquivos esperados: README.md, docs/domain/overview.md, user-flows.md,
  pwa-offline-foundation.md e tests/README.md; item/refinamento e índice.
- Matriz de operações: leitura do snapshot; iniciar/editar execução agendada;
  adicionar/editar/remover/concluir itens; finalizar; sincronização/conflitos/auditoria.
- Diferenciar ação local pendente de persistência remota; explicar estados de fila,
  falha de rede, conflito de versão e recuperação sem apagar IndexedDB.
- Declarar limites de grupos/categorias/templates e leitura offline parcial onde aplicável.
- Ligar cada contrato legado ao substituto Node/API e ao cenário UI BL-0011.
  Se UI não implementada/aprovada, marcar como cobertura futura, sem bloquear a
  comprovação Node/API desta demanda. Não apresentar mock IndexedDB como browser real.
- Registrar resultados novos, comando/commit/data/ambiente; não reutilizar a contagem
  histórica 262/5 como evidência da futura alteração.

## Cenários TDD e contratos futuros

Após aprovação, testar persistência antes de rede, recarga local, envio ordenado,
reconexão, falha sem perda, 409 sem overwrite e resolução auditada autorizada.
Adicionar testes somente após aprovação; xfail(strict=True) apenas em contrato da
fatia futura deste item. Os dois FL-08 continuam rastreados nas respectivas demandas.

## Estratégia de validação

- Focal: node --test tests/js/offline_queue.test.cjs; testes Python de offline,
  sync_center e future_user_flows; evitar rede externa ou banco real.
- Final do ticket: scripts/run_tests.sh se BL-0026 já entregue; senão
  timeout 240 venv/bin/pytest. Node/npm instalados explicitamente, dependências dev.
- UI: cenários mobile de fila, recarga, reconexão e conflito pertencem à BL-0011;
  quando disponíveis e explicitamente solicitados, usar
  ENV_FILE=.env.test bash scripts/run_ui_tests.sh.
- Manual: revisar matriz contra os handlers efetivos e distinguir online de offline;
  conferir que nenhum texto sugere uso de WebSocket como persistência.
- Atualizar grafo após código; publicação exige validação e registro da versão 1.4.0.

## Progresso

| Etapa/ticket | Fatias concluídas | Restantes | Estado |
| --- | --- | --- | --- |
| 1 — Reconciliação | 2/2 | 0 | Implementado e validado; publicação pendente |

## Registro do fechamento documental anterior à aprovação

- Código/testes: não iniciados; três xfail legados preservados nesta etapa.
- Dependências: Node e implementação atual; BL-0011/BL-0026 são relacionadas, sem
  bloqueio obrigatório à conclusão desta demanda por Node/API.
- Validações nesta etapa: links, estados e diff documental; sem execução UI/Node/Python.
- Publicação e aceite: pendentes. Implementação exige aprovação deste documento versionado.

## Início aprovado — 2026-10-29

Aprovação explícita do refinamento c2f9ebb, no conjunto da 1.4.0, registrada antes
dos testes. Branch atualizada até develop 9bda43a, incluindo BL-0026, BL-0011 e
BL-0027 já integradas. Contratos Node usam a fila existente; nenhum comportamento
de produção será alterado nesta demanda. Integração final depende de autorização.

## Fatia 1.1 — Contratos efetivos

Sete cenários Node executam o IIFE real, com fake-indexeddb 6.2.6 fixado por
lockfile. Wrapper Pytest falhou com instrução de npm ci quando a dependência
estava ausente e passou após instalação explícita. Não foi necessário alterar
produção: persistência/recarga, coalescência com versão base, envio por criação e
confirmação, retenção/ordem em falha de rede, sessão expirada, syncNow simultâneo
no mesmo contexto e 409 com versões local/remota foram comprovados.

Removidos somente os três contratos Python que importavam sync_service inexistente;
os dois FL-08 permanecem xfail(strict=True). Focal Python: 47 passes/2 xfail.
Comandos: node tests/js/offline_queue.test.cjs (sete cenários), node --test
tests/js/offline_queue.test.cjs e scripts/run_tests.sh com os quatro módulos
offline_queue_node/offline_cache/sync_center/future_user_flows. Node 26.3.1 local;
CI fixa Node 24 com Action oficial por SHA e npm ci --ignore-scripts no job Python.
Dependência exclusivamente de desenvolvimento, sem bundle ou runtime de produção.

Validação focal UI autorizada: dois cenários Chromium de fila/recarga/reconexão
e conflito/resolução passaram em 10,49s, run 92bb38833bb14123990e62ce6b462406.
Setup aplicou as cinco migrações no SQLite sintético. Actionlint aprovou o workflow
atualizado; compileall e diff --check sem erros. Grafo atualizado com AST.

## Fatia 1.2 e validação final — 2026-10-29

README, overview, FL-09, documento PWA e matriz de testes reconciliados com os
handlers existentes. A matriz distingue leitura parcial, operações locais de
execução, confirmação remota, estados da fila e recuperação. Administração de
grupos/categorias/templates, criação de execuções e aprendizado continuam na API.
Isolamento/autorização, preservação financeira, recorrência no servidor e
separação template/execução não foram alterados. Nenhuma mudança de produção.

- Fatia 1.1: c7cb3ed. Ticket único: 2/2 fatias concluídas, zero pendências próprias.
- Regressão: `bash scripts/run_tests.sh --coverage -q`, Python 3.12.3,
  **289 passes/2 xfail FL-08 em 64,42s**, cobertura **56,18%**, piso preservado.
  Relatórios XML/JSON/HTML em reports/coverage. Node 26.3.1 executou sete cenários.
- UI previamente autorizada: `ENV_FILE=.env.test bash scripts/run_ui_tests.sh -q`,
  Chromium com dados/banco/servidor isolados: **9 passes em 24,99s**, run
  376c6cff2cca442aa7a8e977d0fd700d. Nenhum cenário ignorado na suíte de navegador.
- Uma rodada no sandbox atingiu timeout de 30s no contrato existente de mock HTTP.
  Sem mudar código/timeout, o contrato isolado passou em 4,35s e a regressão final
  fora das restrições de rede local passou integralmente. O erro inicial não foi
  contado como aprovação.
- Setup aplicou as cinco migrações no SQLite marcado de teste. Actionlint,
  compileall, pip check, links locais e diff --check aprovados; grafo AST atualizado.
- CI instala Node 24 e npm ci --ignore-scripts antes da suíte Python. Validação
  remota aprovada conforme registro abaixo. Integração final na develop exige autorização
  explícita; estado em_validacao até publicação e aceite da 1.4.0.

## CI remoto e entrega para integração

- PR de revisão em rascunho: https://github.com/vguerrax/jaci/pull/44.
- Candidato 35129bf78754a61b93e0890953be70e23536fae9 aprovado no
  [run 40816112651](https://github.com/vguerrax/jaci/actions/runs/40816112651):
  Python coverage e Chromium mobile and desktop com success, incluindo instalação
  Node/npm, suíte Python, preparação sintética, nove UI e artifacts previstos.
- Commits das fatias: c7cb3ed (contratos/CI) e 990ac0f (documentação/evidências).
  Registro posterior ao CI altera somente documentação de acompanhamento.
- Branch feature/BL-0001-refinamento-1-4-0 preservada, 2/2 fatias concluídas e zero
  contratos próprios pendentes. develop contém as BL-0026, BL-0027 e BL-0011;
  integração desta BL-0001 ainda aguarda autorização explícita. Sem deploy.
- Publicação e aceite da versão 1.4.0 pendentes; manter em_validacao.

## Integração aprovada — 2026-10-29

O usuário autorizou explicitamente a integração depois da apresentação do PR 44,
das 2/2 fatias e das evidências locais/remotas. Merge na develop: **f5ac74f**,
da feature/BL-0001-refinamento-1-4-0 (head 0d0c575). A árvore do merge é idêntica
à branch aprovada; o registro posterior ao candidato 35129bf altera somente os
dois documentos de acompanhamento. Branch de implementação preservada.

A develop passa a conter as quatro entregas da 1.4.0: BL-0026, BL-0011, BL-0001 e
a correção BL-0027 descoberta no aceite UI. Implementação da BL-0001: 2/2 fatias,
zero pendências próprias. Estado permanece em_validacao até publicação e aceite
da 1.4.0. Nenhum deploy ou alteração de ambiente de produção nesta integração.
