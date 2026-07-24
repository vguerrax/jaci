# Backlog legado do Jaci

Este documento referencia entregas concluídas antes da adoção do processo
`BL-NNNN` em 24 de julho de 2026. Ele não recebe novos itens e não participa da
numeração do [backlog atual](../backlog/README.md).

Os identificadores legados usam larguras variadas, por exemplo `BL-004` e
`BL-029`. Eles permanecem inalterados para preservar branches, histórico Git e
documentos existentes. Um identificador atual como `BL-0004` é uma demanda
diferente de `BL-004`.

O termo "concluído legado" significa que a capacidade está documentada e possui
cobertura ou integração no histórico atual do repositório. Esses registros não
são convertidos em itens arquivados do processo novo porque não contêm toda a
rastreabilidade de triagem, refinamento, validação e publicação hoje exigida.

## PWA, operação offline e sincronização

| Identificador legado | Entrega referenciada | Evidência principal | Referência Git |
| --- | --- | --- | --- |
| `BL-001` | Fundação PWA instalável | [Testes PWA](../../../tests/test_pwa.py) | `foundation/bl-001-pwa` |
| `BL-004` | Estratégia de cache do service worker | [Fundação PWA — BL-004](../pwa-offline-foundation.md#bl-004--estratégia-de-cache) | `9a35d67` |
| `BL-005` a `BL-008` | Cache local de grupos, categorias, templates e execuções | [Fundação PWA — cache local](../pwa-offline-foundation.md#bl-005-a-bl-013--cache-local-e-operações-offline) | `d302163` |
| `BL-009` | Início de compra offline | [Testes de cache offline](../../../tests/test_offline_cache.py) | `971d343` |
| `BL-010` | Atualização de itens offline | [Testes de cache offline](../../../tests/test_offline_cache.py) | `6ea834a` |
| `BL-011` | Adição de itens offline | [Testes de cache offline](../../../tests/test_offline_cache.py) | `dc1602a` |
| `BL-012` | Remoção de itens offline | [Testes de cache offline](../../../tests/test_offline_cache.py) | `5f655b9` |
| `BL-013` | Finalização de compra offline | [Testes de cache offline](../../../tests/test_offline_cache.py) | `cd43c90` |
| `BL-014` | Fila local persistente | [Fundação PWA — BL-014](../pwa-offline-foundation.md#bl-014--fila-local-de-operações) | `e0c55fb` |
| `BL-015` | Sincronização automática | [Fundação PWA — BL-015](../pwa-offline-foundation.md#bl-015--sincronização-automática) | `726a89e` |
| `BL-016` | Status detalhado de sincronização | [Fundação PWA — BL-016](../pwa-offline-foundation.md#bl-016--status-detalhado-de-sincronização) | `774e33b` |
| `BL-017` | Retentativa automática | [Fundação PWA — BL-017](../pwa-offline-foundation.md#bl-017--retentativa-automática) | `3c4ab9c` |
| `BL-018` | Sincronização de alterações da execução agendada | [Edição de execuções agendadas](../scheduled-execution-editing.md#sincronização-offline) | `3bd0d81` |
| `BL-019` | Detecção e resolução explícita de conflitos | [Fundação PWA — BL-019](../pwa-offline-foundation.md#bl-019--resolução-de-conflitos) | `e265f3e` |
| `BL-020` | Central de sincronização | [Fundação PWA — BL-020](../pwa-offline-foundation.md#bl-020--central-de-sincronização) | `75d8bb2` |
| `BL-021` | Auditoria de conflitos | [Fundação PWA — BL-021](../pwa-offline-foundation.md#bl-021--auditoria-de-conflitos) | `3467931` |
| `BL-026` | Indicador global de sincronização | [Fundação PWA — BL-026](../pwa-offline-foundation.md#bl-026--indicador-de-sincronização) | `12a9983` |

A cobertura e a rastreabilidade ainda não consolidadas estão registradas no
[BL-0001 atual](../backlog/items/BL-0001-operacao-offline-cobertura-rastreabilidade.md).

## Aprendizado de templates

| Identificador legado | Entrega referenciada | Evidência principal | Referência Git |
| --- | --- | --- | --- |
| `BL-029` | Detecção de itens adicionados durante a execução | [Aprendizado — BL-029](../template-learning.md#bl-029--detecção-de-itens-adicionados-na-execução) | `5831ca1` |
| `BL-030` | Incorporação confirmada de novos itens | [Aprendizado — BL-030](../template-learning.md#bl-030--incorporação-de-itens) | `aed5d19` |
| `BL-031` e `BL-032` | Detecção e aplicação de quantidades recorrentes | [Aprendizado — quantidades](../template-learning.md#bl-031-e-bl-032--quantidades-recorrentes) | `aed5d19` |
| `BL-033` e `BL-034` | Detecção e aplicação de observações recorrentes | [Aprendizado — observações](../template-learning.md#bl-033-e-bl-034--observações-recorrentes) | `aed5d19` |
| `BL-075` e `BL-076` | Detecção e aplicação de orçamento recorrente | [Aprendizado — orçamentos](../template-learning.md#bl-075-e-bl-076--orçamentos-recorrentes) | `dd07e16` |

A cobertura TDD detalhada permanece em
[`tests/test_template_learning_tdd.py`](../../../tests/test_template_learning_tdd.py).

## Edição de execuções agendadas

| Identificador legado | Entrega referenciada | Evidência principal | Referência Git |
| --- | --- | --- | --- |
| `BL-043`, `BL-044` e `BL-045` | Edição segura de nome, data e orçamento de execução agendada | [Regras da edição agendada](../scheduled-execution-editing.md) | `77672bf` |

## Entregas concluídas sem identificador BL legado

| Entrega | Evidência principal | Referência Git |
| --- | --- | --- |
| Home operacional | [Regras da Home](../home-dashboard.md) e [testes](../../../tests/test_home_dashboard.py) | `feature/new-home` |
| Tratamento de datas e timezone | [Decisão 0001](../../decisions/0001-datas-e-timezone.md) | `c8844a8` |
| Backup automático local do PostgreSQL | [Decisão 0002](../../decisions/0002-backup-postgresql.md) | `4a02cba` |

As lacunas posteriores dessas entregas, quando explícitas, foram migradas para
itens ativos. A replicação externa do backup, por exemplo, está no
[BL-0007](../backlog/items/BL-0007-replicacao-externa-backups.md).

## Mapeamento das fontes abertas migradas

| Fonte anterior | Item atual |
| --- | --- |
| Limitações e contratos futuros de operação offline | [BL-0001](../backlog/items/BL-0001-operacao-offline-cobertura-rastreabilidade.md) |
| Unidades de medida | [BL-0002](../backlog/items/BL-0002-unidades-medida.md) |
| Histórico de preços | [BL-0003](../backlog/items/BL-0003-historico-precos.md) |
| Análise de gastos e dashboards financeiros | [BL-0004](../backlog/items/BL-0004-analise-gastos-dashboard-financeiro.md) |
| Inteligência de compras | [BL-0005](../backlog/items/BL-0005-inteligencia-compras.md) |
| Integrações externas | [BL-0006](../backlog/items/BL-0006-integracoes-externas.md) |
| Replicação externa dos backups | [BL-0007](../backlog/items/BL-0007-replicacao-externa-backups.md) |
| Autoexclusão e anonimização de conta | [BL-0008](../backlog/items/BL-0008-autoexclusao-anonimizacao-conta.md) |
| Criptografia em repouso | [BL-0009](../backlog/items/BL-0009-criptografia-repouso.md) |
