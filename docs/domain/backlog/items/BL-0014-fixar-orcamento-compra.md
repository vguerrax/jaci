# BL-0014 — Fixar resumo de orçamento durante a compra

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0014` |
| Título | Fixar resumo de orçamento durante a compra |
| Tipo | `melhoria` |
| Estado | `em_validacao` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-08-03` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` (`e07bcfe`) em `2026-08-03` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-04` |

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
| Próximo passo | Validar o comportamento em navegador móvel/desktop e registrar a publicação |

## Acompanhamento até produção

- Documento refinado: [Refinamento BL-0014](../../tasks/BL-0014-fixar-orcamento-compra.md).
- Implementação (commits/PRs): `6c6bd17`, correção `440a68d` e compatibilidade
  pós-merge `76c55fb`.
- Validações: 44 testes focados pós-merge e regressão com 186 testes aprovados e
  5 `xfail` legados fora do escopo; `item-filter.js`, `execution-budget.js` e
  `offline-cache.js` aprovados por `node --check`; migrações no head; grafo
  AST-only reconstruído e consultável; validação manual em navegador pendente.
- Publicação: ainda não publicada.
- Itens relacionados: `BL-0013`, `BL-0015` e `BL-0016`, registrados como
  melhorias correlatas da experiência de Lista e Compra.

### Impedimentos

- Nenhum.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 18:03 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
| `2026-08-03 23:27 -03` | Codex | `recebido` -> `em_triagem` | Tela, fragmentos HTMX, WebSocket, estado offline e cobertura existente diagnosticados |
| `2026-08-03 23:27 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Impacto, prioridade, riscos, dependências e limites definidos |
| `2026-08-03 23:27 -03` | Codex | `pronto_para_refinamento` -> `em_refinamento` | Refinamento técnico criado e ligado ao item |
| `2026-08-03 23:27 -03` | Codex | `em_refinamento` -> `pronto_para_implementacao` | Escopo, fatia, cenários TDD e validações completos; aguarda aprovação explícita |
| `2026-08-03 23:30 -03` | Usuário/Codex | Refinamento aprovado; `pronto_para_implementacao` -> `em_implementacao` | Aprovação explícita recebida após o commit documental `b472c20` |
| `2026-08-03 23:37 -03` | Codex | Fatia 1.1.1 concluída (`1/1`) | Resumo fixo, toasts e atualização offline implementados; 54 testes focados aprovados |
| `2026-08-03 23:37 -03` | Codex | `em_implementacao` -> `em_validacao` | Migrações no head e regressão com 178 testes aprovados e 5 `xfail` legados |
| `2026-08-03 23:37 -03` | Codex | Commit técnico registrado | Implementação e evidências consolidadas em `6c6bd17` |
| `2026-08-03 23:48 -03` | Usuário | Toast duplicado reportado durante validação | Duas mensagens simultâneas observadas ao disparar alerta de orçamento |
| `2026-08-03 23:48 -03` | Codex | Deduplicação de toast corrigida | Contrato reproduziu duas instâncias concorrentes; chave global no DOM e cache PWA `v25` validados com 55 testes focados e regressão 179/5 |
| `2026-08-03 23:48 -03` | Codex | Commit corretivo registrado | Correção e evidências consolidadas em `440a68d` |
| `2026-08-04 12:16 -03` | Codex | Compatibilidade pós-merge corrigida | Expectativa do campo de busca alinhada ao commit `f306bc4`; atributos DOM da BL-0013 restaurados no fragmento combinado com a BL-0014; 44 testes focados e regressão 186/5 aprovados |
| `2026-08-04 12:16 -03` | Codex | Commit técnico registrado | Correção dos dois testes e reconstrução do grafo consolidadas em `76c55fb` |
