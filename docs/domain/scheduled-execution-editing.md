# Edição de execuções agendadas

BL-043, BL-044 e BL-045 permitem editar dados próprios de uma compra enquanto ela ainda está agendada.

## Campos editáveis

- Nome da execução, somente quando a compra não possui template
- Data agendada, em qualquer execução agendada
- Orçamento da execução, em qualquer execução agendada

## Regras

- Apenas execuções com status `scheduled` podem ser editadas.
- Somente execução sem template (`template_id IS NULL`) pode ter o nome
  alterado. O nome é próprio da execução e não cria ou modifica template.
- Execuções vinculadas, inclusive compras extras com `is_standalone=true`, não
  podem ser renomeadas; data e orçamento continuam editáveis.
- Nomes históricos já divergentes em execuções vinculadas são preservados, mas
  ficam bloqueados para novas alterações.
- A data editada fica salva na execução e não altera a recorrência do template.
- O orçamento editado substitui apenas o orçamento da execução atual.
- Próximos ciclos continuam sendo gerados pelo servidor a partir do template e da data de finalização.

## Notificações e sincronização

- Ao salvar uma alteração, membros do grupo recebem notificação persistente `execution_updated`.
- Usuários conectados na tela da execução recebem evento WebSocket `execution_updated` e recarregam a visão.
- Usuários desconectados visualizam as alterações ao recarregar a página ou atualizar o snapshot offline.

## Sincronização offline

- Edições feitas sem conexão entram na fila local como `UPDATE_EXECUTION`.
- A operação usa `entidade: execution` e é consolidada por execução, mantendo apenas a alteração mais recente daquela compra.
- Para uma compra sem template, o cache local é atualizado imediatamente com
  nome, data agendada e orçamento.
- Para uma compra vinculada, o formulário envia o nome corrente como campo
  oculto, permitindo atualizar localmente data e orçamento sem oferecer
  renomeação.
- A sincronização automática envia a operação para `/api/offline/operations/update-execution`.
- Se a execução não estiver mais `scheduled` no servidor, a sincronização registra conflito e preserva o estado local para resolução manual.
- Se uma operação adulterada tentar renomear execução vinculada, o servidor
  responde `422` e não salva parcialmente data ou orçamento.
