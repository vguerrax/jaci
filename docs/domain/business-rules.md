## Regras de negócio críticas

### RN01

Template é independente da execução - alterações só afetam execuções futura. Garante que compras em andamento não sejam corrompidas.

### RN02

Execuções são imutáveis após finalização.

### RN03

Recorrência gera próximo ciclo com base na data de finalização da execução atual. Automatiza o agendamento e mantém a periodicidade.

### RN04

Adiantar/adiar NÃO altera o ciclo do template. Flexibilidade na execução sem bagunçar o planejamento.

### RN05

Execução em andamento não pode ser adiada/adiantada. Evita inconsistência com itens já comprados.

### RN06

Ao finalizar, itens não comprados são removidos e podem gerar execução avulsa de pendentes. Fecha o ciclo sem perder o que ficou faltando.

### RN07

Execuções avulsas não geram próximo ciclo. Evita geração indevida de recorrência para compras pontuais.

### RN08

Execuções não modificam templates automaticamente. Toda sugestão de aleração exige confirmação do usuário.

### RN09

Isolamento total por grupo. Todo recurso pertence a um único grupo.

### RN10

Bloqueio otimista por item — conflito detectado por comparação de versão. Essencial para multiusuário simultâneo sem duplicar compras.

### RN11

Orçamento da execução herda do template, mas pode ser sobrescrito. Planejamento padrão com ajuste por ocasião.

### RN12

WebSocket não é fonte de verdade. Atualizações em tempo real servem apenas para sincronização visual. A persistência sempre ocorre por meio da API e do banco de dados.

### RN13

O sistema deve funcionar sem conexão contínua. Toda operação offline deve ser armazenada localmente até ser sincronizada.

### RN14

Conflitos de sincronização não podem causar perda silenciosa de dados.
Quando houver conflito entre dados locais e remotos:

* O sistema deve detectar o conflito.
* O sistema deve informar o usuário.
* O sistema deve permitir resolução explícita.

### RN15

A Home sempre prioriza uma execução em andamento. Na ausência dela, exibe a
próxima execução agendada.

### RN16

Indicadores, alertas e histórico da Home devem ser calculados exclusivamente para
o grupo ativo.

### RN17

A Home exibe no máximo três alertas simultâneos, ordenados por criticidade:
orçamento ultrapassado, compra em andamento e compra nas próximas 24 horas.

### RN18

O histórico recente da Home exibe no máximo as três execuções finalizadas mais
recentes do grupo ativo.
