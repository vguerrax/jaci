# BL-0014 — Fixar resumo de orçamento durante a compra

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0014` |
| Título | Fixar resumo de orçamento durante a compra |
| Tipo | `melhoria` |
| Estado | `pronto_para_implementacao` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-08-03` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` (`e07bcfe`) em `2026-08-03` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-03` |

### Comportamento observado

Durante uma compra em andamento, o resumo mostra o total realizado, o
orçamento previsto e o percentual utilizado antes da lista de itens. Ao rolar
uma compra extensa, essas informações deixam de ficar visíveis.

### Comportamento esperado

Enquanto a compra estiver em andamento, o resumo de orçamento realizado e
previsto deve permanecer visível no topo da tela durante a rolagem, atualizar-se
com as alterações dos itens e não encobrir conteúdo ou ações, especialmente em
dispositivos móveis.

### Impacto e abrangência

- Impacto: permite acompanhar continuamente o limite da compra sem interromper
  a execução para retornar ao topo.
- Abrangência: compras em andamento com orçamento definido, seus totais e
  alertas visuais nos layouts móvel e desktop.
- Frequência: durante toda compra em andamento na qual o usuário percorra a
  lista de itens.

### Passos de reprodução

1. Abrir uma compra em andamento com orçamento e vários itens.
2. Rolar a tela para consultar ou comprar itens distantes do início.
3. Observar que o resumo de orçamento sai da área visível.

### Evidências sanitizadas

- [Resumo de orçamento da Compra](../../../../app/templates/pages/executions/_items_fragment.html).
- [Tela da Compra](../../../../app/templates/pages/executions/in_progress.html).

### Workaround

Rolar manualmente até o início da lista sempre que for necessário conferir o
total realizado e o orçamento previsto.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de apresentação e feedback local, sem mudança de domínio ou persistência remota |
| Domínio afetado | Execução de compras, resumo financeiro e experiência offline |
| Regras de negócio afetadas | Preservar o orçamento da execução, os totais persistidos e a independência entre template e execução |
| Risco de segurança | Não — reutiliza somente dados já autorizados e renderizados na execução |
| Risco de LGPD | Não — não cria coleta, transmissão ou persistência de dados pessoais |
| Risco de isolamento por grupo | Baixo — nenhum endpoint ou consulta nova; manter as rotas autorizadas existentes |
| Risco offline/sincronização | Médio — o resumo deve refletir o estado local e deduplicar alertas após sincronização e WebSocket |
| Risco ao histórico financeiro | Baixo — apresentação local não pode modificar valores persistidos nem substituir o cálculo do servidor |
| Risco à recorrência | Não — não altera status, datas ou geração de execuções futuras |
| Risco à separação template/execução | Não — o resumo usa exclusivamente orçamento e itens da execução atual |
| Dependências | Fragmento de itens, IndexedDB/fila offline, Socket.IO, Bootstrap Toast, navbar fixa e cache PWA |
| Duplicidades | Nenhuma identificada nos backlogs ativo e legado |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Obter aprovação explícita do refinamento versionado antes de criar testes ou código |

## Acompanhamento até produção

- Documento refinado: [Refinamento BL-0014](../../tasks/BL-0014-fixar-orcamento-compra.md).
- Implementação (commits/PRs): ainda não iniciada.
- Validações: somente diagnóstico documental; nenhuma validação executável
  iniciada.
- Publicação: ainda não publicada.
- Itens relacionados: `BL-0013`, `BL-0015` e `BL-0016`, registrados como
  melhorias correlatas da experiência de Lista e Compra.

### Impedimentos

- Implementação bloqueada pelo gate documental até aprovação explícita deste
  refinamento versionado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 18:03 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
| `2026-08-03 23:27 -03` | Codex | `recebido` -> `em_triagem` | Tela, fragmentos HTMX, WebSocket, estado offline e cobertura existente diagnosticados |
| `2026-08-03 23:27 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Impacto, prioridade, riscos, dependências e limites definidos |
| `2026-08-03 23:27 -03` | Codex | `pronto_para_refinamento` -> `em_refinamento` | Refinamento técnico criado e ligado ao item |
| `2026-08-03 23:27 -03` | Codex | `em_refinamento` -> `pronto_para_implementacao` | Escopo, fatia, cenários TDD e validações completos; aguarda aprovação explícita |
