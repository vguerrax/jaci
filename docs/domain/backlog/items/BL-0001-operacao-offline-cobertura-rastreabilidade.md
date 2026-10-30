# BL-0001 — Completar cobertura e rastreabilidade da operação offline

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0001` |
| Título | Completar cobertura e rastreabilidade da operação offline |
| Versão-alvo | `1.4.0` |
| Tipo | `melhoria` |
| Estado | `em_validacao` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-07-24` |
| Origem | Limitações e contratos futuros registrados no README, na documentação PWA e nos testes de fluxos futuros |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-10-29` |

### Comportamento observado

A operação offline de execuções já possui cache local, fila IndexedDB,
sincronização, retentativa, resolução explícita e auditoria de conflitos.
Entretanto, documentos de visão geral ainda descrevem essa capacidade como
planejada ou somente leitura, três contratos `xfail(strict=True)` representam
uma arquitetura Python anterior à implementação no navegador e a documentação
PWA informa que escritas fora da fila atual continuam dependendo da API.

### Comportamento esperado

A rastreabilidade deve refletir a arquitetura offline efetivamente adotada, e
os três contratos Python legados de FL-09 devem ser reconciliados com a fila em
JavaScript e IndexedDB. Mutações de grupos, categorias, templates ou outros
fluxos ainda dependentes da API ficam fora deste item e devem receber demandas
independentes antes de qualquer ampliação da fila.

### Impacto e abrangência

- Impacto: documentação e contratos divergentes dificultam reconhecer o que já
  funciona offline e quais operações ainda precisam evoluir.
- Abrangência: PWA, fila local, sincronização, documentação e contratos de
  FL-09.
- Frequência: sempre que o estado da operação offline ou sua cobertura
  automatizada é consultado.

### Passos de reprodução

1. Comparar a seção PWA do README com `docs/domain/pwa-offline-foundation.md`.
2. Comparar os contratos futuros de FL-09 com `app/static/js/offline-cache.js`.
3. Observar descrições diferentes para a mesma capacidade offline.

### Evidências sanitizadas

- [Fundação PWA e Offline](../../pwa-offline-foundation.md).
- [Rastreabilidade dos fluxos](../../../../tests/README.md).
- [Contratos futuros](../../../../tests/test_future_user_flows.py).
- [Implementação da fila IndexedDB](../../../../app/static/js/offline-cache.js).
- [Cobertura da operação offline](../../../../tests/test_offline_cache.py).
- [Cobertura da central de sincronização](../../../../tests/test_sync_center.py).

### Workaround

Usar a documentação PWA e os testes específicos de cache offline como
referência técnica, verificando cada operação antes de assumir suporte offline.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de rastreabilidade documental e contratual; a implementação crítica já existe no navegador, enquanto três contratos Python de FL-09 representam uma arquitetura anterior |
| Domínio afetado | PWA, operação offline de execuções, fila IndexedDB, sincronização e rastreabilidade de testes |
| Regras de negócio afetadas | Preservar fonte de verdade local, ordem da fila, bloqueio otimista, resolução explícita de conflitos, isolamento por grupo, histórico, recorrência calculada após sincronização e independência entre template e execução |
| Risco de segurança | Sim — snapshots, operações e IDs originados no cliente devem continuar autenticados e autorizados no servidor |
| Risco de LGPD | Sim — IndexedDB e payloads pendentes armazenam dados de compras; a documentação e os contratos não devem expor dados pessoais ou financeiros identificáveis |
| Risco de isolamento por grupo | Sim — snapshot, sincronização e auditoria devem permanecer limitados aos grupos autorizados do usuário |
| Risco offline/sincronização | Sim — é o núcleo da demanda; a reconciliação não pode enfraquecer persistência local, ordem, retentativa ou resolução explícita |
| Risco ao histórico financeiro | Sim — alterações offline incluem quantidades, preços e finalização; os contratos devem preservar valores e impedir perda ou sobrescrita silenciosa |
| Risco à recorrência | Sim — a finalização local deve continuar delegando ao servidor a geração do próximo ciclo após a sincronização |
| Risco à separação template/execução | Sim — o escopo permanece nas execuções e não autoriza propagação automática para templates |
| Dependências | Implementação e cobertura atuais em `offline-cache.js`, `offline.py`, `test_offline_cache.py` e `test_sync_center.py`; BL-0011 acompanha futura cobertura ampla em navegador real sem bloquear este item |
| Duplicidades | Nenhuma identificada; há sobreposição parcial com a [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md), restrita à infraestrutura futura de testes de UI |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Registrar publicação e aceite da 1.4.0; integração autorizada e realizada na develop |

## Acompanhamento até produção

- Documento refinado: [BL-0001](../../tasks/BL-0001-operacao-offline-cobertura-rastreabilidade.md).
- Implementação: 2/2 fatias na feature/BL-0001-refinamento-1-4-0; c7cb3ed entrega os sete cenários Node, wrapper Pytest, lockfile e instalação CI. Documentação reconciliada em 990ac0f; PR de revisão https://github.com/vguerrax/jaci/pull/44.
- Validações: 289 passes/2 xfail FL-08, cobertura 56,18%, sete cenários Node e nove Chromium aprovados; actionlint, migrações no SQLite sintético e links locais aprovados. CI 40816112651 aprovado nos jobs Python/Chromium em 35129bf. Resultados e limitação do sandbox no refinamento.
- Publicação: ainda não publicada no processo atual.
- Itens relacionados: [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md) e
  entregas offline do
  [backlog legado](../../decisions/backlog.md#pwa-operação-offline-e-sincronização).

### Impedimentos

- Publicação e aceite da 1.4.0 pendentes; integração na develop realizada em f5ac74f.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração das limitações e contratos futuros espalhados pela documentação |
| `2026-08-05 14:54 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Escopo da triagem aprovado e evidências da arquitetura offline atual confrontadas |
| `2026-08-05 14:54 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Confirmação, prioridade, recorte, riscos, dependências, duplicidades e próximo passo definidos |
| `2026-10-28 20:40 -03` | Codex | Versão-alvo 1.4.0 associada | Roadmap aprovado para formalização; estado e prioridade preservados, sem autorizar implementação |
| `2026-10-28 20:40 -03` | Codex | pronto_para_refinamento → em_refinamento → pronto_para_implementacao | Reconciliação FL-09, contratos Node e documentação refinados para 1.4.0; aprovação pendente |
| `2026-10-29` | Usuário/Codex | pronto_para_implementacao → em_implementacao | Refinamento aprovado; branch atualizada com dependências integradas; início dos contratos Node da fila efetiva |
| `2026-10-29` | Codex | em_implementacao → em_validacao; 2/2 fatias | Sete Node, 289 passes/2 xfail FL-08, cobertura 56,18% e nove Chromium; sem alterações de produção ou publicação |
| `2026-10-29` | Codex | Validação remota aprovada | PR 44; candidato 35129bf e run 40816112651 com ambos os jobs success; integração final aguarda autorização |
| `2026-10-29` | Usuário/Codex | Integração autorizada e realizada na develop | Merge f5ac74f da feature/BL-0001-refinamento-1-4-0, contendo o candidato validado e seu acompanhamento documental; 2/2 fatias, sem deploy |
