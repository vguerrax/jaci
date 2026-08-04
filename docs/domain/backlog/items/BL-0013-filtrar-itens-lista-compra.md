# BL-0013 — Buscar itens e padronizar categorias nas telas de Lista e Compra

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0013` |
| Título | Buscar itens e padronizar categorias nas telas de Lista e Compra |
| Tipo | `melhoria` |
| Estado | `em_implementacao` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-08-03` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` (`e07bcfe`) em `2026-08-03` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-03` |

### Comportamento observado

As telas de detalhe da Lista e da Compra exibem os itens agrupados por
categoria, mas não oferecem um campo para localizar um produto pelo nome. Em
listas extensas, o usuário precisa percorrer manualmente os grupos e itens. A
tela de compra finalizada também não oferece controles para expandir ou
recolher categorias, diferindo das compras agendada e em andamento.

### Comportamento esperado

As telas de Lista, Compra agendada, Compra em andamento e Compra finalizada
devem permitir filtrar localmente, pelo nome, os itens já carregados. A tela de
compra finalizada deve adotar os controles de collapse das demais telas de
execução. A busca não deve depender de catálogo externo nem de conexão ativa e
deve permitir restaurar a visualização completa ao ser limpa.

### Impacto e abrangência

- Impacto: reduz o tempo e o esforço para localizar produtos durante o
  planejamento e a execução da compra.
- Abrangência: itens existentes nas telas de detalhe de templates e de
  execuções agendadas, em andamento e finalizadas, inclusive em dispositivos
  móveis e offline.
- Frequência: sempre que o usuário precisar localizar um item em uma lista ou
  compra extensa.

### Passos de reprodução

1. Abrir uma Lista ou Compra que contenha vários itens e categorias.
2. Tentar localizar um produto específico pelo nome.
3. Observar que é necessário percorrer manualmente os grupos exibidos.
4. Abrir uma Compra finalizada e observar que suas categorias não podem ser
   expandidas ou recolhidas como nas compras mutáveis.

### Evidências sanitizadas

- [Tela de detalhe da Lista](../../../../app/templates/pages/templates/detail.html).
- [Telas de Compra mutável](../../../../app/templates/pages/executions/in_progress.html).
- [Tela de Compra finalizada](../../../../app/templates/pages/executions/completed.html).

### Workaround

Expandir as categorias e percorrer manualmente os itens até localizar o
produto desejado.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de experiência local e padronização visual, sem alteração de domínio ou persistência |
| Domínio afetado | Planejamento por templates e visualização de execuções |
| Regras de negócio afetadas | Nenhuma regra de persistência; preservar histórico, imutabilidade de execução finalizada e independência entre template e execução |
| Risco de segurança | Não — o filtro opera somente sobre HTML já autorizado e carregado |
| Risco de LGPD | Não — o termo não será enviado, registrado nem persistido |
| Risco de isolamento por grupo | Não — nenhuma consulta ou mutação nova; o conteúdo permanece limitado às rotas autorizadas existentes |
| Risco offline/sincronização | Baixo — a busca deve funcionar sem conexão e ser reaplicada após trocas de fragmento HTMX, WebSocket ou offline |
| Risco ao histórico financeiro | Baixo — resumos globais não podem ser recalculados pelo filtro e a execução finalizada permanece somente leitura |
| Risco à recorrência | Não — nenhuma alteração em datas, status ou geração de execuções |
| Risco à separação template/execução | Não — o filtro atua separadamente no DOM de cada tela e não copia alterações entre entidades |
| Dependências | Agrupamento Jinja2 existente, Bootstrap Collapse e atualização de `#items-container`; BL-0011 acompanha futura infraestrutura Playwright |
| Duplicidades | Nenhuma identificada no backlog ativo ou legado |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Executar as três fatias aprovadas, iniciando pelos contratos TDD do escopo completo |

## Acompanhamento até produção

- Documento refinado: [Refinamento BL-0013](../../tasks/BL-0013-filtrar-itens-lista-compra.md).
- Implementação (commits/PRs): fatia 1 `518cff5`; fatia 2 concluída e com hash
  a registrar após o commit técnico.
- Validações: fatia 1 com 8 testes aprovados; fatia 2 com verificações
  sintáticas JavaScript e 35 testes Pytest aprovados.
- Publicação: ainda não publicada.
- Itens relacionados: `BL-0011`, `BL-0014`, `BL-0015` e `BL-0016`; `BL-0011`
  acompanha a infraestrutura futura de testes em navegador e os demais itens
  cobrem melhorias correlatas da experiência de Lista e Compra.

### Impedimentos

- Nenhum impedimento registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 18:03 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
| `2026-08-03 21:09 -03` | Codex | `recebido` -> `em_triagem` | Diagnóstico das telas, atualização dinâmica e cobertura existente |
| `2026-08-03 21:09 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Escopo, prioridade, riscos e dependências definidos |
| `2026-08-03 21:09 -03` | Codex | `pronto_para_refinamento` -> `em_refinamento` | Documento técnico criado e ligado ao item |
| `2026-08-03 21:09 -03` | Codex | `em_refinamento` -> `pronto_para_implementacao` | Objetivo, três fatias, cenários TDD e validações refinados; aguarda aprovação explícita |
| `2026-08-03 21:18 -03` | Usuário/Codex | Refinamento aprovado; `pronto_para_implementacao` -> `em_implementacao` | Aprovação explícita emitida após o commit documental `2d703bf` |
| `2026-08-03 21:21 -03` | Codex | Fatia 1.1.1 concluída (`1/3`) | Contratos TDD, filtro compartilhado e detalhe da Lista validados com 8 testes aprovados |
| `2026-08-03 21:25 -03` | Codex | Fatia 1.1.2 concluída (`2/3`) | Compras mutáveis e atualizações dinâmicas validadas com 35 testes aprovados |
