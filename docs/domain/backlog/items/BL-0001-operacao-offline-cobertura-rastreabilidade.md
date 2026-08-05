# BL-0001 — Completar cobertura e rastreabilidade da operação offline

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0001` |
| Título | Completar cobertura e rastreabilidade da operação offline |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | Limitações e contratos futuros registrados no README, na documentação PWA e nos testes de fluxos futuros |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

### Comportamento observado

A operação offline de execuções já possui cache local, fila IndexedDB,
sincronização, retentativa, resolução explícita e auditoria de conflitos.
Entretanto, documentos de visão geral ainda descrevem essa capacidade como
planejada ou somente leitura, três contratos `xfail(strict=True)` representam
uma arquitetura Python anterior à implementação no navegador e a documentação
PWA informa que escritas fora da fila atual continuam dependendo da API.

### Comportamento esperado

A rastreabilidade deve refletir a arquitetura offline efetivamente adotada e
deixar explícitas as mutações que ainda dependem da API. A eventual ampliação da
fila deve preservar estado local, sincronização assíncrona, bloqueio otimista,
isolamento por grupo e resolução explícita de conflitos.

### Impacto e abrangência

- Impacto: documentação e contratos divergentes dificultam reconhecer o que já
  funciona offline e quais operações ainda precisam evoluir.
- Abrangência: PWA, fila local, sincronização, contratos de FL-09 e operações de
  escrita da aplicação.
- Frequência: sempre que o estado da operação offline é consultado ou uma
  mutação fora da fila é tentada sem conexão.

### Passos de reprodução

1. Comparar a seção PWA do README com `docs/domain/pwa-offline-foundation.md`.
2. Comparar os contratos futuros de FL-09 com `app/static/js/offline-cache.js`.
3. Observar descrições diferentes para a mesma capacidade offline.

### Evidências sanitizadas

- [Fundação PWA e Offline](../../pwa-offline-foundation.md).
- [Rastreabilidade dos fluxos](../../../../tests/README.md).
- [Contratos futuros](../../../../tests/test_future_user_flows.py).

### Workaround

Usar a documentação PWA e os testes específicos de cache offline como
referência técnica, verificando cada operação antes de assumir suporte offline.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `a_triar` |
| Classificação | `a_triar` |
| Domínio afetado | `a_triar` |
| Regras de negócio afetadas | `a_triar` |
| Risco de segurança | `a_avaliar` |
| Risco de LGPD | `a_avaliar` |
| Risco de isolamento por grupo | `a_avaliar` |
| Risco offline/sincronização | `a_avaliar` |
| Risco ao histórico financeiro | `a_avaliar` |
| Risco à recorrência | `a_avaliar` |
| Risco à separação template/execução | `a_avaliar` |
| Dependências | `a_triar` |
| Duplicidades | `a_triar` |
| Responsável pela próxima etapa | `a_definir` |
| Próximo passo | Realizar triagem para separar correções de rastreabilidade das mutações offline ainda ausentes |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada no processo atual.
- Validações: somente inventário documental; validações de implementação ainda
  não iniciadas.
- Publicação: ainda não publicada no processo atual.
- Itens relacionados: entregas offline do
  [backlog legado](../../decisions/backlog.md#pwa-operação-offline-e-sincronização).

### Impedimentos

- Nenhum registrado; o escopo exato depende da triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração das limitações e contratos futuros espalhados pela documentação |
