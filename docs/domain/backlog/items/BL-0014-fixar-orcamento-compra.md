# BL-0014 — Fixar resumo de orçamento durante a compra

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0014` |
| Título | Fixar resumo de orçamento durante a compra |
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
| Dependências | Atualização dos totais e composição responsiva da tela; detalhamento `a_triar` |
| Duplicidades | Nenhuma identificada no diagnóstico inicial; confirmar na triagem |
| Responsável pela próxima etapa | `a_definir` |
| Próximo passo | Triar comportamento responsivo, atualização dos valores e interação com cabeçalhos fixos |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: somente diagnóstico documental; nenhuma validação executável
  iniciada.
- Publicação: ainda não publicada.
- Itens relacionados: `BL-0013`, `BL-0015` e `BL-0016`, registrados como
  melhorias correlatas da experiência de Lista e Compra.

### Impedimentos

- Nenhum registrado; critérios detalhados dependem da triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 18:03 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
