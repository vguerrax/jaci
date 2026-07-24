# BL-0003 — Disponibilizar histórico de preços por grupo e item

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0003` |
| Título | Disponibilizar histórico de preços por grupo e item |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | FL-08, item 4 do roadmap e contrato futuro de histórico de preços |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

### Comportamento observado

Execuções finalizadas preservam quantidade e valor unitário, mas o Jaci não
oferece uma consulta consolidada da evolução de preços de um item. O contrato
futuro de FL-08 permanece em `xfail(strict=True)`.

### Comportamento esperado

O usuário deve consultar o histórico de preços de um item usando somente
execuções finalizadas autorizadas para o grupo ativo, sem alterar dados
históricos.

### Impacto e abrangência

- Impacto: usuários não conseguem comparar preços anteriores ou identificar
  variações diretamente no produto.
- Abrangência: execuções finalizadas, itens comprados, agenda/histórico e
  isolamento por grupo.
- Frequência: sempre que o usuário deseja comparar um preço atual com compras
  anteriores.

### Passos de reprodução

1. Finalizar mais de uma execução contendo o mesmo item com preços diferentes.
2. Acessar agenda ou detalhes das compras.
3. Observar que não há visão consolidada da evolução dos preços.

### Evidências sanitizadas

- [FL-08 — Consulta da Agenda e Histórico](../../user-flows.md#fl-08--consulta-da-agenda-e-histórico).
- [Contrato futuro de histórico](../../../../tests/test_future_user_flows.py).
- [Roadmap do Jaci](../../../../AGENTS.md#ordem-de-prioridade-do-roadmap).

### Workaround

Abrir manualmente cada execução finalizada e comparar os valores.

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
| Próximo passo | Realizar triagem do fluxo, identidade do item e fontes históricas |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: contrato futuro existente, ainda em `xfail(strict=True)`.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0004](BL-0004-analise-gastos-dashboard-financeiro.md).

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração do roadmap, fluxo parcial e contrato futuro |
