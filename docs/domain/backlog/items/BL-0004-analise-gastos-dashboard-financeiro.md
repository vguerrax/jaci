# BL-0004 — Disponibilizar análise de gastos e dashboard financeiro

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0004` |
| Título | Disponibilizar análise de gastos e dashboard financeiro |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | FL-08, item 7 do roadmap e contrato futuro de análise de gastos |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

### Comportamento observado

O Jaci calcula totais de execuções e mostra métricas operacionais recentes, mas
não consolida gastos por período em uma análise financeira. O contrato futuro
de FL-08 para resumo de gastos permanece em `xfail(strict=True)`.

### Comportamento esperado

O usuário deve analisar gastos do grupo ativo em períodos definidos,
considerando apenas execuções finalizadas e preservando o histórico que originou
os totais.

### Impacto e abrangência

- Impacto: o acompanhamento financeiro depende da abertura manual de compras ou
  de ferramentas externas.
- Abrangência: execuções finalizadas, filtros de período, Home, agenda e futuras
  visualizações financeiras.
- Frequência: sempre que o usuário deseja acompanhar gastos acumulados ou
  tendências.

### Passos de reprodução

1. Finalizar compras em um mesmo período.
2. Acessar Home e agenda.
3. Observar que não há resumo financeiro consolidado do período.

### Evidências sanitizadas

- [FL-08 — Consulta da Agenda e Histórico](../../user-flows.md#fl-08--consulta-da-agenda-e-histórico).
- [Contrato futuro de análise de gastos](../../../../tests/test_future_user_flows.py).
- [Roadmap do Jaci](../../../../AGENTS.md#ordem-de-prioridade-do-roadmap).

### Workaround

Somar manualmente os totais das execuções finalizadas ou exportá-los para uma
ferramenta externa.

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
| Próximo passo | Realizar triagem das métricas, períodos e visualizações esperadas |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: contrato futuro existente, ainda em `xfail(strict=True)`.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0003](BL-0003-historico-precos.md).

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração do roadmap, fluxo parcial e contrato futuro |
