# Refinamento — BL-0001 — Rastreabilidade da operação offline

## Rastreabilidade

- Item: [BL-0001](../backlog/items/BL-0001-operacao-offline-cobertura-rastreabilidade.md).
- Versão-alvo: 1.4.0; responsável: Engenharia Jaci.
- Estado: pronto_para_implementacao; aprovação posterior ao versionamento pendente.
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
| 1 — Reconciliação | 0/2 | 2 | Aguarda aprovação |

## Fechamento

- Código/testes: não iniciados; três xfail legados preservados nesta etapa.
- Dependências: Node e implementação atual; BL-0011/BL-0026 são relacionadas, sem
  bloqueio obrigatório à conclusão desta demanda por Node/API.
- Validações nesta etapa: links, estados e diff documental; sem execução UI/Node/Python.
- Publicação e aceite: pendentes. Implementação exige aprovação deste documento versionado.
