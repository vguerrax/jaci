# BL-0006 — Exportar compras para calendário e compartilhar listas, compras e convites

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0006` |
| Título | Exportar compras para calendário e compartilhar listas, compras e convites |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P3` |
| Data de entrada | `2026-07-24` |
| Origem | Item 8 da ordem de prioridade do roadmap em `AGENTS.md` |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

### Comportamento observado

O Jaci mantém agenda, listas recorrentes e compras dentro da aplicação. Não há
como adicionar uma compra agendada a um calendário externo nem compartilhar,
por uma ação explícita do aparelho, o resumo de uma lista, compra ou convite de
grupo. O convite atual é entregue somente por e-mail.

### Comportamento esperado

O usuário deve poder:

- exportar manualmente uma compra agendada em arquivo ICS compatível com
  calendários externos, contendo somente nome, data e link protegido para o
  Jaci, sem sincronização automática;
- compartilhar pelo recurso do aparelho, com destino compatível com WhatsApp,
  um resumo sem valores de uma lista ou compra e o respectivo link protegido;
- como proprietário do grupo, informar o e-mail do destinatário e compartilhar
  pelo WhatsApp um convite de curta duração vinculado a esse e-mail.

Todas as ações são iniciadas e confirmadas pelo usuário. A primeira entrega não
usa WhatsApp Business API, não envia mensagens automaticamente e não inclui
orçamento, preços, valores pagos ou membros. Catálogos, comprovantes e outras
integrações externas devem receber demandas próprias.

### Impacto e abrangência

- Impacto: o usuário precisa recriar compromissos no calendário e copiar
  manualmente informações e links para coordenar compras fora do Jaci.
- Abrangência: agenda de compras, templates usados como listas, execuções e
  convites de grupos autorizados.
- Frequência: sempre que um usuário desejar levar uma compra ao calendário ou
  compartilhar uma lista, compra ou convite fora do Jaci.

### Passos de reprodução

1. Abrir uma compra agendada, lista, compra ou tela de convite de grupo.
2. Procurar uma ação para exportar ao calendário ou compartilhar pelo
   WhatsApp.
3. Observar que a ação não está disponível e que o convite só pode ser enviado
   pelo fluxo de e-mail atual.

### Evidências sanitizadas

- [Roadmap do Jaci](../../../../AGENTS.md#ordem-de-prioridade-do-roadmap).
- [README do projeto](../../../../README.md).
- [Fluxo de gestão de grupos](../../user-flows.md#fl-07--gestão-de-grupos).
- [Decisão de datas e timezone](../../../decisions/0001-datas-e-timezone.md).

### Workaround

Copiar manualmente os dados para o calendário ou para uma conversa e continuar
enviando convites por e-mail.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de interoperabilidade de saída, sob ação explícita do usuário, por arquivo ICS e compartilhamento nativo compatível com WhatsApp |
| Domínio afetado | Agenda, templates/listas, execuções/compras, grupos, convites, autenticação e autorização |
| Regras de negócio afetadas | Exportar apenas snapshots autorizados; não alterar template, execução, recorrência ou histórico; exigir proprietário para convidar e vincular o convite ao e-mail informado; validar no servidor o acesso a todo link compartilhado |
| Risco de segurança | Alto — links e convites podem ser encaminhados; convites devem preservar prazo curto, destinatário vinculado e autorização do proprietário, e links de listas e compras não podem conceder acesso por si sós |
| Risco de LGPD | Alto — nomes de compras e itens revelam hábitos de consumo e passam a um aplicativo externo; o compartilhamento deve ser explícito, minimizar dados e excluir valores, membros e evidências sensíveis |
| Risco de isolamento por grupo | Alto — a geração do resumo, ICS, link ou convite deve validar usuário, grupo e recurso no servidor; abrir o link deve repetir a autorização e nunca expor dados entre grupos |
| Risco offline/sincronização | Médio — o compartilhamento é complementar e não pode bloquear os fluxos locais; indisponibilidade do aplicativo externo ou da conexão deve falhar de forma clara, sem criar operação pendente nem depender de WebSocket |
| Risco ao histórico financeiro | Baixo — valores, orçamento e registros pagos ficam fora do conteúdo exportado, e a integração não modifica execuções finalizadas |
| Risco à recorrência | Baixo — o ICS representa a data atual da execução como snapshot e não cria, recalcula nem sincroniza ciclos recorrentes |
| Risco à separação template/execução | Baixo — listas e compras possuem resumos e links próprios, sem propagação de alterações entre template e execução |
| Dependências | [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md), agenda e regra de timezone, detalhes autorizados de templates e execuções, fluxo atual de convite por magic link e autenticação no Tupã, Web Share API com fallback compatível com WhatsApp e clientes externos de calendário |
| Duplicidades | Nenhuma identificada; o FL-07 e o convite por e-mail atual são bases relacionadas, mas não oferecem exportação de calendário ou compartilhamento pelo aparelho |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Refinar pontos de entrada mobile-first, contrato ICS e timezone, conteúdo e sanitização dos resumos, fallback do compartilhamento, convite por canal alternativo, autorização, falhas offline e cenários TDD |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem baseada nos fluxos atuais de agenda, templates,
  execuções, grupos, convites, autenticação e operação offline; validações de
  implementação ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md),
  [FL-07 — Gestão de Grupos](../../user-flows.md#fl-07--gestão-de-grupos) e
  [Decisão 0001 — Tratamento de datas e timezone](../../../decisions/0001-datas-e-timezone.md).

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração do item aberto no roadmap legado |
| `2026-08-05 22:07 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Casos de uso de calendário e WhatsApp, mecanismos sem APIs proprietárias, conteúdo mínimo e prioridade definidos com o usuário |
| `2026-08-05 22:07 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Escopo limitado, riscos, dependências, duplicidades, responsável e próximo passo definidos |
