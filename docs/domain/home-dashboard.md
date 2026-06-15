# Tela Inicial Operacional

## Objetivo

A Home do Jaci é um painel operacional, não uma página institucional. Ela deve
responder rapidamente:

* O que preciso comprar agora?
* Quanto estou gastando?
* O que exige minha atenção?

## Prioridade da Compra Principal

O card principal respeita a seguinte ordem:

1. Execução em andamento mais antiga.
2. Próxima execução agendada.
3. Estado vazio com ação para criar uma compra ou lista.

A compra em andamento deve ser acessível em um único toque.

## Indicadores

Os indicadores são calculados exclusivamente para o grupo ativo:

* quantidade de compras agendadas;
* quantidade de compras em andamento;
* gasto acumulado em compras finalizadas no mês;
* quantidade de itens pendentes em compras agendadas ou em andamento.

## Alertas

A Home exibe no máximo três alertas, ordenados por criticidade:

1. orçamento ultrapassado;
2. compra em andamento;
3. compra agendada para as próximas 24 horas.

Alertas de sincronização e modo offline são apresentados pelo indicador global de
sincronização.

## Histórico Recente

O histórico recente contém as três execuções finalizadas mais recentes do grupo
ativo, com nome, data e total gasto.

## Offline e Sincronização

O indicador de sincronização permanece visível em todas as telas e informa:

* sincronizado;
* modo offline;
* quantidade de alterações pendentes, quando disponível localmente.

O service worker usa estratégia network-first para páginas visitadas e assets
essenciais. Quando a rede falha, a última versão armazenada pode ser exibida.

A fila persistente de mutações e a resolução de conflitos continuam sendo
evoluções separadas do módulo offline-first.
