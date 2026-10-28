# BL-0004 — Disponibilizar análise de gastos e dashboard financeiro

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0004` |
| Título | Disponibilizar análise de gastos e dashboard financeiro |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-07-24` |
| Origem | FL-08, item 7 do roadmap e contrato futuro de análise de gastos |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

### Comportamento observado

O Jaci calcula totais de execuções e mostra métricas operacionais recentes, mas
não consolida gastos por período em uma análise financeira. O contrato futuro
de FL-08 para resumo de gastos permanece em `xfail(strict=True)`.

### Comportamento esperado

O usuário deve analisar os gastos do grupo ativo por atalhos de período ou
intervalo personalizado. A primeira entrega deve apresentar total gasto,
quantidade de compras, média por compra e evolução mensal, considerando apenas
execuções finalizadas e preservando o histórico que originou os totais. A
primeira versão não detalha gastos por categoria, template, local ou orçamento.

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
- [Métrica mensal existente na Home](../../../../app/services/home_service.py).
- [Cálculo vigente dos totais da execução](../../../../app/services/execution_service.py).
- [Cobertura do dashboard operacional](../../../../tests/test_home_dashboard.py).

### Workaround

Somar manualmente os totais das execuções finalizadas ou exportá-los para uma
ferramenta externa.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de consulta financeira consolidada, somente leitura, baseada nos totais já preservados em execuções finalizadas |
| Domínio afetado | Histórico de compras, execuções finalizadas, análise financeira, filtros de período e isolamento por grupo |
| Regras de negócio afetadas | Usar `finished_at` para o período; considerar somente execuções finalizadas e itens comprados não excluídos; preservar os valores históricos e não alterar templates ou execuções |
| Risco de segurança | Sim — filtros e acesso à análise devem exigir autenticação, validar o grupo ativo no servidor e limitar entradas de período |
| Risco de LGPD | Sim — os indicadores revelam hábitos e valores de compra; respostas, logs e evidências não podem expor dados pessoais ou financeiros de outro usuário ou grupo |
| Risco de isolamento por grupo | Alto — agregações nunca podem combinar execuções de grupos distintos; o filtro pelo grupo autorizado é obrigatório em toda consulta |
| Risco offline/sincronização | Médio — dados disponíveis localmente podem gerar uma visão parcial, que deve ser identificada como tal e nunca bloquear o fluxo de compra |
| Risco ao histórico financeiro | Alto — os indicadores devem derivar dos valores persistidos, sem recalcular, reclassificar ou modificar execuções finalizadas retroativamente |
| Risco à recorrência | Baixo — `finished_at` serve apenas para classificar o gasto no período e não pode alterar o cálculo do próximo ciclo |
| Risco à separação template/execução | Baixo — a análise consulta execuções e não pode gravar valores, indicadores ou ajustes nos templates |
| Dependências | Nenhum bloqueio identificado; o refinamento deve reutilizar o cálculo vigente de totais, a autorização do grupo ativo e o histórico por `finished_at` |
| Duplicidades | Nenhuma identificada; a [BL-0003](BL-0003-historico-precos.md) trata preços por item e a [BL-0005](BL-0005-inteligencia-compras.md) trata recomendações, não o resumo financeiro por período |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Refinar atalhos e intervalo personalizado, agregações de total, quantidade, média e evolução mensal, apresentação mobile-first, estado offline parcial, navegação sem ampliar a função operacional da Home e cenários TDD |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem baseada no contrato futuro, no cálculo vigente dos totais
  e na métrica mensal da Home; validações de implementação ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0003](BL-0003-historico-precos.md) e
  [BL-0005](BL-0005-inteligencia-compras.md).

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração do roadmap, fluxo parcial e contrato futuro |
| `2026-08-05 17:06 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Resumo e tendência, seleção de período e prioridade definidos com o usuário |
| `2026-08-05 17:06 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Fontes atuais, riscos, dependências, duplicidades e próximo passo definidos |
