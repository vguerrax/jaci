# BL-0015 — Adicionar item como comprado durante execução

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0015` |
| Título | Adicionar item como comprado durante execução |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-08-03` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` (`e07bcfe`) em `2026-08-03` |
| Responsável | `a_definir` |
| Atualizado em | `2026-08-03` |

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
| Dependências | Contrato de adição online/offline, totais e alertas de orçamento; detalhamento `a_triar` |
| Duplicidades | Nenhuma identificada no diagnóstico inicial; confirmar na triagem |
| Responsável pela próxima etapa | `a_definir` |
| Próximo passo | Triar quantidade comprada, validação do valor, sincronização, conflitos e atualização dos totais |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: somente diagnóstico documental; nenhuma validação executável
  iniciada.
- Publicação: ainda não publicada.
- Itens relacionados: `BL-0013`, `BL-0014` e `BL-0016`, registrados como
  melhorias correlatas da experiência de Lista e Compra.

### Impedimentos

- Nenhum registrado; critérios detalhados dependem da triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 18:03 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
