# BL-0003 — Disponibilizar histórico de preços por grupo e item

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0003` |
| Título | Disponibilizar histórico de preços por grupo e item |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-07-24` |
| Origem | FL-08, item 4 do roadmap e contrato futuro de histórico de preços |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

### Comportamento observado

Execuções finalizadas preservam quantidade e valor unitário, mas o Jaci não
oferece uma consulta consolidada da evolução de preços de um item. O contrato
futuro de FL-08 permanece em `xfail(strict=True)`.

### Comportamento esperado

O usuário deve consultar durante a compra o histórico de preços de itens com o
mesmo nome normalizado no grupo ativo. A consulta deve considerar somente itens
comprados em execuções finalizadas autorizadas, preservar os dados históricos e
não comparar preços registrados em unidades diferentes.

### Impacto e abrangência

- Impacto: usuários não conseguem comparar preços anteriores ou identificar
  variações diretamente no produto.
- Abrangência: execução da compra, execuções finalizadas, itens comprados,
  histórico financeiro, unidades de medida e isolamento por grupo.
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
- [Modelo de itens executados](../../../../app/models/execution.py).
- [Análise histórica existente](../../../../app/services/template_learning_service.py).
- [Histórico recente por grupo](../../../../app/services/home_service.py).

### Workaround

Abrir manualmente cada execução finalizada e comparar os valores.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de consulta financeira contextual, somente leitura, baseada nos valores já preservados em itens de execuções finalizadas |
| Domínio afetado | Execução da compra, agenda/histórico, itens executados, preços e isolamento por grupo |
| Regras de negócio afetadas | Considerar somente itens comprados e não excluídos de execuções finalizadas, ordenar pela data de finalização, preservar imutabilidade histórica e não alterar templates |
| Risco de segurança | Sim — o nome consultado vem do cliente e toda busca deve validar autenticação, grupo ativo e limites de entrada no servidor |
| Risco de LGPD | Sim — a consulta consolida hábitos e valores de compra; respostas, logs e evidências não podem expor dados de outro usuário ou grupo |
| Risco de isolamento por grupo | Alto — nomes iguais em grupos diferentes nunca podem compartilhar resultados; o filtro pelo grupo autorizado é obrigatório |
| Risco offline/sincronização | Médio — a consulta contextual deve usar apenas dados locais disponíveis quando offline, indicar resultado parcial e nunca bloquear o registro da compra |
| Risco ao histórico financeiro | Alto — somente valores persistidos podem ser exibidos; não recalcular, converter, reclassificar ou modificar registros finalizados |
| Risco à recorrência | Baixo — a consulta usa `finished_at` apenas como data histórica e não altera o cálculo ou a geração do próximo ciclo |
| Risco à separação template/execução | Baixo — a identidade por nome atravessa templates somente para leitura e não pode propagar valores ou alterações a templates ou execuções |
| Dependências | BL-0002 define unidades comparáveis antes da implementação; normalização de nomes, modelo `ExecutionItem`, histórico por `finished_at` e snapshot offline existente devem ser considerados no refinamento |
| Duplicidades | Nenhuma identificada; a [BL-0004](BL-0004-analise-gastos-dashboard-financeiro.md) consolida gastos por período, não preços por item |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Elaborar o refinamento da normalização por nome no grupo, consulta somente de compras finalizadas, apresentação contextual, compatibilidade com unidades e leitura offline parcial |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem baseada no contrato futuro, modelos e consultas históricas
  existentes; validações de implementação ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md),
  [BL-0002](BL-0002-unidades-medida.md) e
  [BL-0004](BL-0004-analise-gastos-dashboard-financeiro.md).

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração do roadmap, fluxo parcial e contrato futuro |
| `2026-08-05 15:16 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Identidade por nome normalizado, acesso contextual e prioridade definidos com o usuário |
| `2026-08-05 15:16 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Fontes históricas, riscos, dependências, duplicidades e próximo passo definidos |
