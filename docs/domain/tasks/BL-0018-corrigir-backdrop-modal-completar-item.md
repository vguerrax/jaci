# Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item

## Rastreabilidade

- Item de backlog: [BL-0018](../backlog/items/BL-0018-corrigir-backdrop-modal-completar-item.md)
- Branch: `feature/BL-0018-corrigir-backdrop-modal-completar-item`, criada a
  partir da `main` por solicitação explícita do usuário para este hotfix
- Responsável pelo refinamento: Engenharia Jaci
- Estado do refinamento: `pronto_para_implementacao`
- Itens relacionados: `BL-0011`, `BL-0014`, `BL-0015` e `BL-0016`

## Objetivo e critérios de sucesso

### Objetivo

Restabelecer a interação com o modal de completar item, garantindo uma ordem de
camadas consistente para todos os modais abertos pelo controlador manual sem
reduzir a proteção visual do backdrop nem comprometer o fluxo offline.

### Critérios de sucesso

1. O modal de completar item fica acima do backdrop e permite interação com
   campos, cancelamento e confirmação em viewport móvel e desktop.
2. O caminho online carregado por HTMX e o modal offline persistente usam a
   mesma ordem de camadas e não criam backdrops duplicados.
3. O modal de editar item e o modal de adicionar item preservam o empilhamento
   correto, sem colocar FAB, navbar ou conteúdo da página acima do backdrop.
4. Fechar por botão ou `Escape` remove o backdrop e restaura o estado de rolagem
   já controlado por `JaciModal`.
5. Nenhuma rota, regra de negócio, persistência, autorização ou contrato de
   sincronização é alterado.
6. O CSS corrigido é distribuído pelo shell PWA sem permanecer preso ao cache
   da versão `1.2.0`.

## Escopo

### Incluído

- Contrato TDD que explicita a ordem de camadas entre modais gerenciados,
  backdrop, FAB e conteúdo da página.
- Ajuste mínimo no CSS compartilhado dos modais para manter seu plano acima do
  backdrop manual.
- Regressão estática para os modais de completar, editar e adicionar item.
- Incremento da versão do cache PWA e atualização do contrato correspondente.
- Validação manual online e offline em viewport móvel e desktop.
- Cenário Playwright futuro associado à `BL-0011`, sem criar infraestrutura de
  UI nesta demanda.

### Excluído

- Alterar HTML, campos, submissão HTMX ou persistência da conclusão do item,
  salvo se um teste demonstrar necessidade estrita para o empilhamento.
- Trocar Bootstrap, reescrever `JaciModal` ou introduzir framework frontend.
- Alterar quantidade, preço, concorrência otimista ou sincronização offline.
- Criar a infraestrutura Playwright ainda acompanhada pela `BL-0011`.
- Corrigir modais não relacionados que não compartilhem o contrato afetado.

## Riscos e regras preservadas

- Regras de negócio afetadas: nenhuma; o hotfix atua somente na camada visual
  e preserva a conclusão e edição existentes.
- Segurança e permissões: rotas e consultas autorizadas permanecem intactas;
  IDs do cliente não ganham qualquer papel novo.
- LGPD: `N/A` — nenhum dado pessoal novo ou telemetria é introduzido.
- Isolamento por grupo: `N/A` para o CSS; as validações atuais das rotas não
  serão alteradas.
- Offline e sincronização: o modal offline deve funcionar com o CSS cacheado
  localmente; a versão do shell deve ser elevada para distribuir a correção.
- Histórico financeiro: nenhum cálculo ou registro é modificado.
- Recorrência: `N/A` — nenhuma mudança de status ou data da execução.
- Separação entre template e execução: `N/A` — nenhuma propagação de dados.

## Plano de implementação

### Etapa 1 — Restaurar o empilhamento dos modais de item

#### Ticket 1.1 — Corrigir e distribuir o contrato visual compartilhado

##### Fatia 1.1.1 — Proteger a ordem de camadas e o cache PWA

- Ordem: `1`
- Objetivo da fatia: escrever os contratos de regressão, aplicar o menor ajuste
  CSS capaz de manter os modais gerenciados acima do backdrop e distribuir o
  ativo corrigido pelo cache PWA.
- Dependências: aprovação explícita deste refinamento.
- Arquivos esperados:
  - `tests/test_offline_cache.py`
  - `tests/test_item_add_fab.py`
  - `tests/test_pwa.py`
  - `app/static/css/jaci-theme.css`
  - `app/static/js/service-worker.js`
- Validações focadas:
  - `node --check app/static/js/service-worker.js`
  - `timeout 180 venv/bin/pytest tests/test_offline_cache.py tests/test_item_add_fab.py tests/test_pwa.py --no-cov`
  - inspeção manual online/offline em viewport móvel e desktop
- Documentação a atualizar:
  - item e refinamento `BL-0018`
  - `tests/README.md`, se a matriz registrar a cobertura do hotfix

## Cenários TDD

Estes cenários devem ser escritos como testes antes da implementação, depois da
aprovação explícita deste refinamento.

1. Dado um modal padrão aberto por `JaciModal`, seu plano de empilhamento é
   superior ao backdrop manual, que continua acima do conteúdo, navbar e FAB.
2. Dado o modal online de completar item carregado por HTMX, o usuário consegue
   visualizar e interagir com quantidade, valor, local, observações, cancelar e
   confirmar sem o backdrop interceptar as ações.
3. Dado o fallback offline de completar item, o mesmo contrato visual é usado e
   o formulário continua operável sem conexão.
4. Dados os modais de editar e adicionar item, ambos permanecem acima do mesmo
   backdrop e não sofrem regressão de empilhamento.
5. Dado o fechamento pelo botão ou por `Escape`, o modal e o backdrop deixam de
   interceptar interação e a rolagem da página é restaurada.
6. Dada uma abertura repetida ou a troca entre modais, existe no máximo um
   backdrop manual ativo.
7. Dado um cliente com o shell PWA anterior, a nova versão do service worker
   invalida o cache antigo e disponibiliza o CSS corrigido.

### Contratos de etapas futuras

- Quando a `BL-0011` entregar a infraestrutura Playwright, cobrir o fluxo real:
  entrar em uma compra, abrir “Comprar” em viewport móvel, confirmar que o
  modal recebe eventos de ponteiro acima do backdrop, preencher os campos e
  fechar por cancelamento e confirmação.
- Não haverá `xfail(strict=True)` no escopo executável deste hotfix.

## Estratégia de validação

### Por fatia

- Escrever primeiro os contratos estáticos de ordem das camadas e cache.
- Aplicar o ajuste CSS mínimo e elevar a versão do shell PWA.
- Executar os testes focados e a verificação sintática do service worker.
- Confirmar que nenhum arquivo de backend, modelo ou migração foi alterado.
- Executar `venv/bin/graphify update .` após a mudança de código.
- Atualizar item, refinamento, progresso e evidências antes do commit técnico.

### Validação manual

1. Online e em viewport móvel, abrir uma compra com item pendente, acionar
   “Comprar” e confirmar que o modal está visível e recebe toque em todos os
   campos e botões.
2. Repetir em viewport desktop e confirmar que navbar, FAB e página permanecem
   atrás do backdrop enquanto o modal fica acima dele.
3. Fechar por “Cancelar” e por `Escape`, verificando remoção do backdrop e
   restauração da rolagem.
4. Desconectar a rede, abrir o modal offline de completar item e confirmar o
   mesmo empilhamento e interação.
5. Abrir os modais de editar e adicionar item para confirmar ausência de
   regressão e inexistência de backdrops duplicados.

### Regressão total

Executar quando a fatia estiver concluída e não houver contrato pendente:

- `venv/bin/alembic upgrade head`
- `timeout 240 venv/bin/pytest`
- Playwright: infraestrutura ausente; cenário futuro registrado na `BL-0011` e
  validação manual obrigatória neste hotfix.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 / Ticket 1.1 — Empilhamento e cache | `0/1` | `1` | Pendente |

## Fechamento

- Commits/PRs: ainda não iniciados.
- Resultado das validações focadas: ainda não executadas.
- Resultado da validação manual: ainda não executada.
- Resultado da regressão total: ainda não executada.
- `xfail(strict=True)` pendentes no escopo: nenhum planejado.
- Documentação atualizada: item, índice e este refinamento.
