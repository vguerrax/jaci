# BL-0018 — Corrigir backdrop sobre o modal de completar item

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0018` |
| Título | Corrigir backdrop sobre o modal de completar item |
| Tipo | `bug` |
| Estado | `concluido` |
| Severidade | `S1` |
| Prioridade | `P0` |
| Data de entrada | `2026-08-05` |
| Origem | Hotfix reportado pelo usuário |
| Ambiente/versão | Produção, versão `1.2.0`; código da `main` em `5c7c869` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

### Comportamento observado

Ao abrir o modal de comprar/completar um item durante a execução, o backdrop
fica acima do conteúdo do modal. A interface aparece encoberta e não permite
interagir normalmente com os campos e ações.

### Comportamento esperado

O modal de completar item deve permanecer acima do backdrop, visível e
interativo, tanto no caminho online carregado por HTMX quanto no fallback
offline, preservando o bloqueio visual e de interação do restante da página.

### Impacto e abrangência

- Impacto: bloqueia o registro de quantidade e valor de um item planejado no
  fluxo crítico da compra.
- Abrangência: execuções em andamento que abrem modais controlados por
  `JaciModal`, com impacto confirmado no modal de completar item.
- Frequência: sempre que o modal afetado é aberto com o contrato atual de
  camadas.

### Passos de reprodução

1. Abrir uma execução de compra em andamento com item pendente.
2. Acionar a compra do item para abrir o formulário de conclusão.
3. Observar que o backdrop está em `z-index: 1060`, acima do modal Bootstrap no
   nível `1055`, encobrindo seu conteúdo.

### Evidências sanitizadas

- Relato do usuário em `2026-08-05`.
- [`jaci-theme.css`](../../../../app/static/css/jaci-theme.css) eleva o backdrop
  manual a `1060`, mas eleva somente `.item-add-modal` a `1070`.
- [`_complete_modal.html`](../../../../app/templates/pages/executions/_complete_modal.html)
  abre um modal Bootstrap padrão pelo controlador `JaciModal`.

### Workaround

Não há alternativa operacional aceitável no mesmo fluxo para registrar os
dados financeiros do item planejado.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` por relato e inspeção estática do contrato de camadas |
| Classificação | Regressão visual de empilhamento introduzida pelo backdrop manual compartilhado |
| Domínio afetado | Execução da compra, conclusão e edição de itens, experiência online/offline |
| Regras de negócio afetadas | Nenhuma regra de persistência deve mudar; preservar quantidade, valor, versão otimista e fluxo de conclusão existentes |
| Risco de segurança | Baixo — correção restrita à apresentação, sem alterar autenticação, autorização ou entrada de dados |
| Risco de LGPD | Não — nenhum dado novo é coletado, transmitido ou registrado |
| Risco de isolamento por grupo | Não — rotas e consultas autorizadas permanecem inalteradas |
| Risco offline/sincronização | Médio — o mesmo controlador abre o fallback offline e o CSS corrigido precisa ser distribuído pelo cache PWA |
| Risco ao histórico financeiro | Baixo — a correção apenas devolve acesso ao formulário; persistência e histórico não mudam |
| Risco à recorrência | Não — nenhuma data, finalização ou geração futura é alterada |
| Risco à separação template/execução | Não — nenhuma propagação entre template e execução é introduzida |
| Dependências | `JaciModal`, Bootstrap modal, CSS do tema, shell/cache PWA e cobertura futura da `BL-0011` |
| Duplicidades | Nenhuma identificada; `BL-0014`, `BL-0015` e `BL-0016` são entregas relacionadas, mas não cobrem a regressão |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Nenhum — demanda concluída na versão `1.2.1` |

## Acompanhamento até produção

- Documento refinado: [Refinamento BL-0018](../../tasks/BL-0018-corrigir-backdrop-modal-completar-item.md).
- Implementação (commits/PRs): camada global dos modais elevada acima do
  backdrop manual, cache PWA atualizado para `v30` e contratos de regressão
  adicionados no commit `a079492`.
- Validações: 61 testes focados aprovados; sintaxe do service worker aprovada;
  migrações no head; regressão com 226 testes aprovados e 5 `xfail` legados
  fora do escopo; grafo AST-only atualizado; aceite da versão `1.2.1` em
  produção informado pelo usuário.
- Publicação: produção, versão `1.2.1`, tag `v1.2.1` no commit `f9cb4dd`,
  publicada em `2026-08-05`.
- Itens relacionados: `BL-0011`, `BL-0014`, `BL-0015` e `BL-0016`.

### Impedimentos

- Nenhum.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-05 11:59 -03` | Usuário/Codex | Item criado em `recebido` | Hotfix reportado pelo usuário |
| `2026-08-05 11:59 -03` | Codex | `recebido` -> `em_triagem` | Relato, modal, controlador manual, CSS e cache PWA inspecionados |
| `2026-08-05 11:59 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Impacto bloqueante, causa aparente, riscos, prioridade e ausência de duplicidade definidos |
| `2026-08-05 11:59 -03` | Codex | `pronto_para_refinamento` -> `em_refinamento` | Refinamento técnico criado e ligado ao item |
| `2026-08-05 11:59 -03` | Codex | `em_refinamento` -> `pronto_para_implementacao` | Escopo, fatia, cenários TDD e validações completos; aguarda aprovação explícita |
| `2026-08-05 12:02 -03` | Usuário/Codex | Refinamento aprovado; `pronto_para_implementacao` -> `em_implementacao` | Aprovação explícita recebida após o commit documental `8d666a2` |
| `2026-08-05 12:06 -03` | Codex | Fatia 1.1.1 concluída (`1/1`) | Contratos TDD reproduziram camada e cache antigos; modal elevado e shell PWA `v30` validados |
| `2026-08-05 12:06 -03` | Codex | `em_implementacao` -> `em_validacao` | 61 testes focados e regressão 226/5 aprovados; migrações no head e validação manual pendente |
| `2026-08-05 12:08 -03` | Codex | Commit técnico registrado | Implementação, contratos, evidências e grafo consolidados em `a079492` |
| `2026-08-05 14:15 -03` | Usuário/Codex | `em_validacao` -> `concluido` | Publicação em produção da versão `1.2.1`, tag `v1.2.1` no commit `f9cb4dd`, informada pelo usuário |
