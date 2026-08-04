# BL-0015 — Adicionar item como comprado durante execução

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0015` |
| Título | Adicionar item como comprado durante execução |
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

Ao adicionar um item a uma compra em andamento, o fluxo atual solicita nome,
quantidade planejada, categoria e observações. O item é criado como pendente,
sem quantidade comprada nem valor unitário, e exige uma segunda ação para ser
marcado como comprado.

### Comportamento esperado

Ao incluir um item em uma compra `em_andamento`, o fluxo deve exigir o valor
unitário e persistir o novo item imediatamente como comprado. A inclusão em
compras apenas agendadas deve continuar sem registrar dados financeiros antes
da execução, e o novo item não deve alterar o template automaticamente.

### Impacto e abrangência

- Impacto: elimina uma etapa frequente ao registrar produtos encontrados e
  comprados durante a execução.
- Abrangência: inclusão online e offline de itens em compras em andamento,
  totais financeiros, alertas de orçamento, sincronização e histórico.
- Frequência: sempre que um produto não planejado for adicionado durante uma
  compra em andamento.

### Passos de reprodução

1. Abrir uma compra em andamento.
2. Usar o formulário de adição para incluir um produto novo.
3. Observar que não é solicitado valor e que o item permanece pendente até uma
   segunda ação de compra.

### Evidências sanitizadas

- [Formulário de adição na Compra](../../../../app/templates/pages/executions/in_progress.html).
- [Serviço de itens da execução](../../../../app/services/execution_service.py).
- [Fila offline de itens da execução](../../../../app/static/js/offline-cache.js).

### Workaround

Adicionar o item como pendente e, em seguida, acionar **Comprar** para informar
quantidade e valor unitário.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de experiência e persistência para eliminar a segunda ação de compra ao incluir item não planejado |
| Domínio afetado | Execuções, itens executados, totais financeiros e sincronização offline |
| Regras de negócio afetadas | Item incluído em execução não altera template; dados financeiros pertencem somente à execução; persistência precede atualização visual |
| Risco de segurança | Baixo — preservar autenticação e autorização da execução antes de aceitar a mutação |
| Risco de LGPD | Baixo — não introduz novo dado pessoal; textos e valores continuam no grupo autorizado |
| Risco de isolamento por grupo | Médio — execução e categoria recebidas do cliente devem continuar validadas contra o grupo do usuário |
| Risco offline/sincronização | Alto — o item comprado deve existir localmente, atualizar a interface e reconciliar o ID temporário sem duplicação |
| Risco ao histórico financeiro | Médio — quantidade e valor passam a compor total e alertas no mesmo ato da inclusão e não podem ser perdidos na sincronização |
| Risco à recorrência | Baixo — a inclusão não altera cálculo de recorrência nem gera execução automaticamente |
| Risco à separação template/execução | Médio — o item permanece sem `template_item_id` e qualquer incorporação ao template continua manual |
| Dependências | Serviço e rota de itens, fragmentos HTMX, totais e alertas, IndexedDB/fila offline, reconciliação e cache PWA |
| Duplicidades | Nenhuma identificada; BL-0013, BL-0014 e BL-0016 são melhorias correlatas de interface, não substitutas |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Validar manualmente os fluxos mobile online/offline e registrar a publicação |

## Acompanhamento até produção

- Documento refinado: [Refinamento BL-0015](../../tasks/BL-0015-adicionar-item-comprado.md).
- Implementação (commits/PRs): fatia 1.1.1 `69cfd64`; fatia 1.1.2 `ae32ca5`.
- Validações: 83 testes focados aprovados; sintaxe dos dois JavaScript
  aprovada; migrações no head; regressão com 181 testes aprovados e 5 `xfail`
  legados fora do escopo; `pylint` indisponível no ambiente virtual.
- Publicação: ainda não publicada.
- Itens relacionados: `BL-0013`, `BL-0014` e `BL-0016`, registrados como
  melhorias correlatas da experiência de Lista e Compra.

### Impedimentos

- Nenhum.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 18:03 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
| `2026-08-04 00:22 -03` | Codex | `recebido` -> `em_triagem` | Fluxos online/offline, totais, autorização e regras críticas diagnosticados |
| `2026-08-04 00:22 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Quantidade compartilhada, valor maior que zero e atualização offline imediata definidos com o usuário |
| `2026-08-04 00:22 -03` | Codex | `pronto_para_refinamento` -> `em_refinamento` | Documento técnico criado e ligado ao item |
| `2026-08-04 00:22 -03` | Codex | `em_refinamento` -> `pronto_para_implementacao` | Objetivo, duas fatias, contratos TDD e validações refinados; aguarda nova aprovação explícita |
| `2026-08-04 00:30 -03` | Usuário/Codex | Refinamento aprovado; `pronto_para_implementacao` -> `em_implementacao` | Aprovação explícita emitida após o commit documental `4e5aa92` |
| `2026-08-04 00:36 -03` | Codex | Fatia 1.1.1 concluída (`1/2`) | Contratos completos escritos; fluxo online validado com 54 testes aprovados e 3 `xfail(strict=True)` da fatia offline |
| `2026-08-04 00:42 -03` | Codex | Fatia 1.1.2 concluída (`2/2`) | Estado local, totais, alertas, sincronização, reconciliação e cache PWA validados com 50 testes aprovados |
| `2026-08-04 00:42 -03` | Codex | `em_implementacao` -> `em_validacao` | Migrações no head; regressão com 181 testes aprovados e 5 `xfail` legados fora do escopo; aguarda validação manual e publicação |
