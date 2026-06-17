# Edição de execuções agendadas

BL-043, BL-044 e BL-045 permitem editar dados próprios de uma compra enquanto ela ainda está agendada.

## Campos editáveis

- Nome da execução
- Data agendada
- Orçamento da execução

## Regras

- Apenas execuções com status `scheduled` podem ser editadas.
- O nome editado fica salvo na execução e não altera o template associado.
- A data editada fica salva na execução e não altera a recorrência do template.
- O orçamento editado substitui apenas o orçamento da execução atual.
- Próximos ciclos continuam sendo gerados pelo servidor a partir do template e da data de finalização.

## Notificações e sincronização

- Ao salvar uma alteração, membros do grupo recebem notificação persistente `execution_updated`.
- Usuários conectados na tela da execução recebem evento WebSocket `execution_updated` e recarregam a visão.
- Usuários desconectados visualizam as alterações ao recarregar a página ou atualizar o snapshot offline.
