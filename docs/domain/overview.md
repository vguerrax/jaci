## Jaci

**Jaci** é uma aplicação web para planejamento e execução colaborativa de compras periódicas.

Na essência, ele resolve um problema comum em famílias e grupos: organizar compras recorrentes (a compra do mês, a feira da semana, o abastecimento da despensa) substituindo listas de papel, mensagens de WhatsApp ou planilhas soltas.

## Qual problema o produto resolve?

O Jaci resolve o problema de planejar e executar compras periódicas de forma colaborativa e organizada.

Antes do Jaci, uma família ou grupo que faz compras recorrentes (compra do mês, feira da semana, abastecimento) geralmente usa lista de papel, bloco de notas ou WhatsApp — ferramentas que não separam o planejamento (o que pretendo comprar) da execução (o que realmente comprei e quanto paguei). Isso gera dores como:

- **Falta de histórico:** não saber quanto gastou na compra passada ou se o preço subiu

- **Desorganização na execução:** várias pessoas comprando ao mesmo tempo sem saber quem já pegou o quê

- **Retrabalho:** recriar a mesma lista todo mês/semana do zero

- **Perda de itens não encontrados:** esquecer o que ficou pendente da compra anterior

- **Sem noção de gasto em tempo real:** chegar no caixa e descobrir que estourou o orçamento

O Jaci ataca essas dores com templates recorrentes, execução em tempo real multiusuário, registro financeiro por item, e agenda inteligente.


## Operação com conexão instável

A execução de compras já utiliza IndexedDB e uma fila persistente: ações
suportadas são registradas no dispositivo antes do envio à API. O estado local
pendente não confirma persistência remota. Ao reconectar, a aplicação sincroniza
as operações; divergências de versão exigem decisão explícita, preservando os
dados local e remoto para resolução. Socket.IO complementa a atualização visual.

É necessário ter aberto as páginas e armazenado os dados anteriormente. Criar ou
administrar grupos, categorias e templates, autenticar e criar execuções exige
API. Finalizar localmente não gera o próximo ciclo recorrente: isso acontece no
servidor durante a sincronização. A [matriz de operações e recuperação](pwa-offline-foundation.md#matriz-atual-de-operações)
detalha o alcance e os limites; os testes estão rastreados na
[BL-0001](backlog/items/BL-0001-operacao-offline-cobertura-rastreabilidade.md).
