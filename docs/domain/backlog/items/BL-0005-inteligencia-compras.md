# BL-0005 — Evoluir inteligência de compras

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0005` |
| Título | Evoluir inteligência de compras |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | Item 6 da ordem de prioridade do roadmap em `AGENTS.md` |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

### Comportamento observado

O Jaci aprende ajustes recorrentes de itens, observações, quantidades e
orçamento com confirmação do usuário. O roadmap prevê uma etapa posterior de
inteligência de compras, mas não há demanda ativa que centralize esse trabalho.

### Comportamento esperado

Evoluções de inteligência devem usar o histórico para reduzir esforço e
retrabalho sem alterar templates automaticamente, sem perder explicabilidade e
sem aumentar a complexidade durante a compra.

### Impacto e abrangência

- Impacto: oportunidades de planejamento e decisão baseadas no histórico não
  possuem rastreabilidade operacional.
- Abrangência: templates, execuções, histórico e sugestões ao usuário.
- Frequência: desconhecida até a triagem definir os casos de uso.

### Passos de reprodução

Não se aplica como falha pontual. A demanda formaliza uma frente futura do
roadmap ainda sem escopo técnico.

### Evidências sanitizadas

- [Roadmap do Jaci](../../../../AGENTS.md#ordem-de-prioridade-do-roadmap).
- [Aprendizado contínuo dos templates](../../template-learning.md).

### Workaround

Usar as sugestões de aprendizado já disponíveis e analisar manualmente o
histórico.

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
| Próximo passo | Realizar triagem dos problemas de usuário e resultados esperados |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: aprendizado de templates no
  [backlog legado](../../decisions/backlog.md#aprendizado-de-templates).

### Impedimentos

- Nenhum registrado; casos de uso permanecem a definir na triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração do item aberto no roadmap legado |
