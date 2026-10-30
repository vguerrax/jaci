# BL-0024 — Autocompletar nomes de itens pelo histórico do grupo

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0024` |
| Título | Autocompletar nomes de itens pelo histórico do grupo |
| Versão-alvo | `1.8.0` |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-09-17` |
| Origem | Solicitação do usuário para reutilizar nomes já conhecidos pelo grupo |
| Ambiente/versão | Estado de `develop` (`67059b3`) em `2026-09-17` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-10-28` |

### Comportamento observado

Os formulários de adição de item em templates e execuções usam campos de texto
livre para o nome. Mesmo quando o grupo já cadastrou ou comprou o mesmo produto,
a pessoa precisa digitar o nome completo novamente e pode criar variações de
capitalização, acentuação ou grafia.

O Jaci mantém nomes em `TemplateItem` e `ExecutionItem`, mas não oferece uma
consulta ou cache de sugestões para esses formulários.

### Comportamento esperado

Ao adicionar um item a um template ou a uma execução, o campo de nome deve
sugerir nomes únicos já presentes em itens de templates ou de execuções do mesmo
grupo. Itens de execução apagados logicamente não devem alimentar as sugestões.

O usuário continua livre para informar um nome novo. Selecionar uma sugestão
preenche somente o nome: categoria, quantidade e observações não são alteradas
automaticamente. A primeira entrega não adiciona autocomplete aos formulários
de edição e não interfere em nomes bloqueados por vínculo histórico.

A experiência deve ser mobile-first, acessível e resiliente a conexão instável,
sem misturar nomes entre grupos ou tornar o cadastro dependente da obtenção das
sugestões.

### Impacto e abrangência

- Impacto: reduz digitação repetitiva e variações de nome, melhorando a
  consistência necessária ao histórico e às futuras análises do grupo.
- Abrangência: adição de itens em templates e execuções, histórico de nomes do
  grupo, atualização dinâmica de fragmentos e funcionamento offline.
- Frequência: em toda inclusão de item cujo nome já tenha sido usado pelo grupo.

### Passos de reprodução

1. Cadastrar ou comprar um item chamado “Arroz” em um grupo.
2. Abrir o formulário para adicionar item em outro template ou execução do
   mesmo grupo.
3. Digitar as primeiras letras do nome.
4. Observar que o sistema não apresenta “Arroz” como sugestão.

### Evidências sanitizadas

- [Formulário de adição em template](../../../../app/templates/pages/templates/detail.html)
  possui campo de nome sem fonte de sugestões.
- [Formulário de adição em execução](../../../../app/templates/pages/executions/in_progress.html)
  possui o mesmo comportamento e integra a fila offline.
- [`TemplateItem`](../../../../app/models/template.py) e
  [`ExecutionItem`](../../../../app/models/execution.py) já armazenam nomes e
  vínculos suficientes para limitar a consulta ao grupo.
- [JavaScript do modal de adição](../../../../app/static/js/item-add-modal.js)
  valida o nome, mas não carrega nem apresenta histórico.

### Workaround

Consultar visualmente itens existentes e digitar o nome completo, tentando
reproduzir manualmente a grafia anterior.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` por inspeção dos formulários, modelos e JavaScript atuais |
| Classificação | Melhoria de produtividade e consistência nominal baseada no histórico isolado do grupo |
| Domínio afetado | Templates, execuções, itens, histórico nominal, interface mobile e cache offline |
| Regras de negócio afetadas | Sugestão é opcional e preenche somente nome; não altera template automaticamente, não modifica itens históricos e respeita imutabilidade de nomes vinculados |
| Risco de segurança | Médio — a fonte de sugestões deve ficar autorizada no servidor e não aceitar `group_id` arbitrário nem expor nomes por endpoints públicos sem sessão |
| Risco de LGPD | Médio — nomes de produtos revelam hábitos de consumo; respostas, cache, logs e métricas devem minimizar dados e permanecer no dispositivo/grupo autorizado |
| Risco de isolamento por grupo | Alto — nomes devem ser coletados exclusivamente de templates e execuções do grupo ativo, sem deduplicação ou cache compartilhado entre grupos |
| Risco offline/sincronização | Alto — sugestões em cache podem estar incompletas ou defasadas, mas o formulário deve continuar aceitando texto novo e reconciliar o histórico sem bloquear a inclusão |
| Risco ao histórico financeiro | Baixo — apenas nomes são consultados; valores, quantidades compradas e totais não entram nas sugestões nem são recalculados |
| Risco à recorrência | Não — a seleção de nome não altera frequência, datas ou geração de execuções |
| Risco à separação template/execução | Médio — a fonte pode reunir nomes dos dois domínios, mas a escolha cria somente o item solicitado e nunca propaga alterações entre eles |
| Dependências | Modelos e serviços de template/execução, formulários de adição, fragmentos HTMX, fila/cache PWA, BL-0001 e futura cobertura UI da BL-0011 |
| Duplicidades | Nenhuma; a [BL-0005](BL-0005-inteligencia-compras.md) recomenda itens e quantidades para uma execução futura, enquanto esta demanda apenas completa o texto digitado; a [BL-0020](BL-0020-bloquear-renomeacao-item-vinculado.md) protege nomes históricos existentes |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Refinar normalização e deduplicação, ranking por prefixo/frequência/recência, limite e contrato da consulta, cache por grupo, acessibilidade e cenários TDD online/offline |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem por inspeção dos modelos, formulários e fluxo offline;
  validações executáveis ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md),
  [BL-0005](BL-0005-inteligencia-compras.md),
  [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md) e
  [BL-0020](BL-0020-bloquear-renomeacao-item-vinculado.md).

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-09-17 16:38 -03` | Codex | Item criado em `recebido` | Solicitação de autocomplete no nome de novos itens |
| `2026-09-17 16:38 -03` | Codex | `recebido` → `em_triagem` | Ausência de sugestões e fontes históricas confirmadas nos modelos e formulários |
| `2026-09-17 16:38 -03` | Usuário/Codex | `em_triagem` → `pronto_para_refinamento` | Fonte templates+execuções, escopo apenas de adição, prioridade P2 e riscos definidos |
| `2026-10-28 20:40 -03` | Codex | Versão-alvo 1.8.0 associada | Roadmap aprovado para formalização; estado e prioridade preservados, sem autorizar implementação |
