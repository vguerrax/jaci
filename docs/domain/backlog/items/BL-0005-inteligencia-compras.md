# BL-0005 — Evoluir inteligência de compras

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0005` |
| Título | Evoluir inteligência de compras |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-07-24` |
| Origem | Item 6 da ordem de prioridade do roadmap em `AGENTS.md` |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

### Comportamento observado

O Jaci aprende ajustes recorrentes de itens, observações, quantidades e
orçamento com confirmação do usuário. O roadmap prevê uma etapa posterior de
inteligência de compras, mas não há demanda ativa que centralize esse trabalho.

### Comportamento esperado

Antes de iniciar uma execução futura vinculada a template, o usuário deve poder
revisar recomendações opcionais e explicáveis de itens provavelmente necessários
e respectivas quantidades, derivadas do histórico finalizado do mesmo template.
Cada recomendação aceita deve alterar somente a execução agendada; o template e
as execuções históricas permanecem intactos.

A primeira entrega não contempla execuções avulsas, preços, locais, orçamento ou
análises posteriores à compra.

### Impacto e abrangência

- Impacto: o usuário precisa recordar e ajustar manualmente itens e quantidades
  da próxima compra mesmo quando o histórico do template contém padrões úteis.
- Abrangência: planejamento de execuções futuras vinculadas a template,
  histórico finalizado do template e isolamento por grupo.
- Frequência: sempre que o usuário prepara uma nova execução vinculada a um
  template com histórico suficiente para recomendações.

### Passos de reprodução

1. Finalizar execuções recorrentes do mesmo template com padrões de itens ou
   quantidades.
2. Gerar ou abrir a próxima execução vinculada ao template antes de iniciá-la.
3. Observar que o Jaci não antecipa itens prováveis nem ajustes de quantidade
   com base nesse histórico.

### Evidências sanitizadas

- [Roadmap do Jaci](../../../../AGENTS.md#ordem-de-prioridade-do-roadmap).
- [Aprendizado contínuo dos templates](../../template-learning.md).
- [Serviço de aprendizado existente](../../../../app/services/template_learning_service.py).
- [Cobertura do aprendizado de templates](../../../../tests/test_template_learning_tdd.py).

### Workaround

Usar as sugestões reativas de aprendizado já disponíveis e revisar manualmente
o histórico do template antes de iniciar a próxima compra.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de planejamento preditivo e explicável, anterior ao início da compra, baseada em padrões de itens e quantidades do mesmo template |
| Domínio afetado | Templates, execuções agendadas, itens executados, histórico finalizado, aprendizado e isolamento por grupo |
| Regras de negócio afetadas | Usar somente execuções finalizadas e vinculadas ao mesmo template; exigir aceitação individual; alterar apenas o snapshot futuro e preservar template, histórico, recorrência e execuções avulsas |
| Risco de segurança | Sim — a consulta e a aplicação das recomendações devem exigir autenticação, autorização no grupo ativo e validação no servidor dos IDs recebidos |
| Risco de LGPD | Sim — padrões de itens e quantidades revelam hábitos de consumo; respostas, logs e evidências não podem expor dados de outro usuário ou grupo |
| Risco de isolamento por grupo | Alto — histórico, sugestões e execução de destino devem pertencer ao mesmo grupo autorizado, sem combinar padrões entre grupos |
| Risco offline/sincronização | Médio — recomendações podem refletir somente o histórico local disponível, devem indicar parcialidade e nunca bloquear o início ou a edição offline da compra |
| Risco ao histórico financeiro | Baixo — a primeira entrega não estima preços ou orçamento e deve consultar execuções finalizadas sem recalcular ou modificar seus registros |
| Risco à recorrência | Baixo — recomendações não podem alterar datas, frequência nem a geração do próximo ciclo, somente itens e quantidades da execução agendada |
| Risco à separação template/execução | Alto — a aceitação deve alterar somente a execução futura; qualquer aprendizado posterior do template continua no fluxo explícito já existente |
| Dependências | [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md) para experiência offline, [BL-0002](BL-0002-unidades-medida.md) para comparar quantidades compatíveis e o aprendizado de templates existente como base histórica e de confirmação |
| Duplicidades | Nenhuma identificada; a [BL-0003](BL-0003-historico-precos.md) consulta preços, a [BL-0004](BL-0004-analise-gastos-dashboard-financeiro.md) consolida gastos e o aprendizado legado atualiza templates após a compra |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Refinar elegibilidade e limiar histórico, explicações, revisão mobile-first antes do início, aplicação individual na execução, estado offline parcial e cenários TDD |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem baseada no aprendizado existente, nos contratos de domínio
  e nas decisões de primeira entrega; validações de implementação ainda não
  iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md),
  [BL-0002](BL-0002-unidades-medida.md),
  [BL-0003](BL-0003-historico-precos.md),
  [BL-0004](BL-0004-analise-gastos-dashboard-financeiro.md) e aprendizado de
  templates no [backlog legado](../../decisions/backlog.md#aprendizado-de-templates).

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração do item aberto no roadmap legado |
| `2026-08-05 19:59 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Planejamento preditivo anterior à compra, escopo de itens e quantidades, aplicação somente na execução e prioridade definidos com o usuário |
| `2026-08-05 19:59 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Fontes atuais, riscos, dependências, duplicidades e próximo passo definidos |
