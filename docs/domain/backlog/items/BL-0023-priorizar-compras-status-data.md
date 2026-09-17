# BL-0023 — Priorizar compras abertas por status e data

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0023` |
| Título | Priorizar compras abertas por status e data |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-09-17` |
| Origem | Solicitação do usuário para destacar compras abertas e atrasadas |
| Ambiente/versão | Estado de `develop` (`29e00ed`) em `2026-09-17` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-09-17` |

### Comportamento observado

A listagem de compras ordena execuções somente por `scheduled_date` decrescente.
Isso mistura estados e pode posicionar uma compra aberta e atrasada depois de
compras futuras, concluídas ou canceladas.

A Home prioriza uma compra em andamento, mas, na ausência dela, posiciona uma
agendada de hoje ou futura antes das agendadas atrasadas. Assim, a compra que há
mais tempo exige ação pode não ser o destaque principal.

### Comportamento esperado

A listagem deve aplicar uma ordem operacional estável:

1. compras em andamento, da data agendada mais antiga para a mais recente;
2. compras agendadas atrasadas, da mais antiga para a mais recente;
3. compras agendadas para hoje ou para o futuro, da mais próxima para a mais
   distante;
4. compras concluídas, da finalização mais recente para a mais antiga;
5. compras canceladas, da data agendada mais recente para a mais antiga.

A Home deve continuar destacando primeiro uma compra em andamento. Quando não
houver nenhuma, deve exibir a compra agendada atrasada mais antiga; sem atrasos,
deve exibir a próxima compra agendada de hoje ou do futuro.

Datas civis e a definição de “hoje” devem seguir `America/Sao_Paulo`. Filtros de
status continuam disponíveis e preservam a ordenação relevante dentro do
resultado filtrado.

### Impacto e abrangência

- Impacto: reduz o risco de ignorar compras vencidas e coloca a próxima ação
  operacional no início da lista e no destaque principal.
- Abrangência: listagem de execuções, filtros por status, compra principal da
  Home e documentação da prioridade operacional.
- Frequência: em toda abertura da lista de compras ou da Home de um grupo com
  execuções em estados e datas diferentes.

### Passos de reprodução

1. Criar compras agendadas para ontem, hoje e amanhã.
2. Manter ou criar compras concluídas e canceladas em datas variadas.
3. Abrir a listagem e observar que a data decrescente mistura a prioridade
   operacional esperada.
4. Sem compra em andamento, abrir a Home e observar que uma compra futura é
   exibida antes da compra atrasada.

### Evidências sanitizadas

- [`get_executions_for_group`](../../../../app/services/execution_service.py)
  usa somente `scheduled_date.desc()` na ordenação atual.
- [`get_priority_execution`](../../../../app/services/home_service.py) mantém
  compra em andamento primeiro, mas atribui prioridade às datas de hoje/futuras
  antes das atrasadas.
- [Documentação da Home](../../home-dashboard.md) e RN15 descrevem a compra
  principal, mas ainda não estabelecem a precedência das atrasadas.
- [ADR de datas](../../../decisions/0001-datas-e-timezone.md) define o cálculo
  de dias civis no fuso local.

### Workaround

Usar filtros de status, consultar a agenda e comparar manualmente as datas para
localizar compras atrasadas antes de iniciar a próxima.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` por inspeção das consultas da listagem e da Home |
| Classificação | Melhoria de priorização operacional compartilhada entre lista de compras e Home |
| Domínio afetado | Execuções, estados, agenda, listagem, Home e datas civis |
| Regras de negócio afetadas | Estender RN15: em andamento permanece primeiro; depois, atraso mais antigo e próxima agendada; preservar estados, imutabilidade e ADR 0001 |
| Risco de segurança | Baixo — somente a ordenação de dados já autorizados muda; filtros e consultas continuam exigindo grupo ativo |
| Risco de LGPD | Baixo — nenhuma informação nova é coletada ou exposta; a consulta permanece limitada ao grupo autorizado |
| Risco de isolamento por grupo | Alto — todas as parcelas da ordenação e a seleção da Home devem filtrar `group_id` antes de ordenar ou limitar resultados |
| Risco offline/sincronização | Médio — snapshots ou páginas em cache podem exibir ordem antiga; a ordenação local, se existir, deve reproduzir a regra do servidor e reconciliar após sincronização |
| Risco ao histórico financeiro | Baixo — concluídas mudam apenas de posição visual, ordenadas por `finished_at`; totais e registros históricos não são recalculados |
| Risco à recorrência | Baixo — datas e status são somente consultados; nenhuma execução é reagendada e nenhum ciclo é recalculado |
| Risco à separação template/execução | Não — a regra opera apenas sobre execuções e não consulta nem altera templates |
| Dependências | `ExecutionStatus`, ADR 0001, consultas de execução e Home, filtros atuais, cache/PWA e futura cobertura UI da BL-0011 |
| Duplicidades | Nenhuma; a Home existente implementa uma prioridade parcial, mas não cobre atrasadas antes das próximas compras |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Refinar chave de ordenação comum, limites de dia local, empates por ID, paridade dos filtros e cache offline, atualização de RN15 e cenários TDD |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem por inspeção das consultas, template e documentação da
  Home; validações executáveis ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md)
  e [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md).

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-09-17 16:37 -03` | Codex | Item criado em `recebido` | Solicitação de ordenação por status/data e prioridade de atrasadas na Home |
| `2026-09-17 16:37 -03` | Codex | `recebido` → `em_triagem` | Ordenações atuais da listagem e da Home confirmadas por inspeção |
| `2026-09-17 16:37 -03` | Usuário/Codex | `em_triagem` → `pronto_para_refinamento` | Precedência de andamento, atrasadas e futuras, prioridade P1 e riscos definidos |
