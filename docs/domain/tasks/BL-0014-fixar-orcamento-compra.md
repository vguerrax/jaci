# Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra

## Rastreabilidade

- Item de backlog: [BL-0014](../backlog/items/BL-0014-fixar-orcamento-compra.md)
- Branch: `feature/BL-0014-fixar-orcamento-compra`
- Responsável pelo refinamento: Engenharia Jaci
- Estado do refinamento: `concluido`
- Itens relacionados: `BL-0011`, `BL-0013`, `BL-0015` e `BL-0016`

## Objetivo e critérios de sucesso

### Objetivo

Manter o acompanhamento do gasto disponível durante a rolagem de uma compra em
andamento, com feedback consistente em operações online, colaborativas e
offline, sem reduzir excessivamente a área útil da tela móvel.

### Critérios de sucesso

1. Uma compra `em_andamento` com orçamento positivo mantém total realizado,
   orçamento, percentual e barra visual fixos abaixo da navbar durante a
   rolagem em viewport móvel e desktop.
2. O resumo não encobre navbar, itens ou ações e acompanha alterações na altura
   da navegação e no viewport.
3. Compras agendadas e execuções sem orçamento preservam o comportamento atual
   e não recebem resumo fixo.
4. HTMX, Socket.IO e sincronização atualizam o mesmo resumo sem duplicar estado
   ou depender do WebSocket para persistência.
5. Operações offline de comprar, desmarcar e remover item recalculam o total a
   partir do snapshot local e atualizam imediatamente percentual e faixa.
6. Subidas para 80%, 95% e 100% exibem um toast além do banner existente; cada
   faixa alerta uma vez até o total cair abaixo dela.
7. Nenhuma API, migração, dado financeiro ou relação entre template e execução
   é alterada.

## Escopo

### Incluído

- Transformar o cartão financeiro existente em resumo fixo somente para
  execuções em andamento com orçamento positivo.
- Contrato DOM por atributos `data-*` para total, limite, percentual, barra,
  faixa e mensagem de alerta.
- Controlador JavaScript Vanilla para posição sob a navbar, atualização visual,
  transições de faixa e Bootstrap Toast.
- Integração do controlador com trocas do fragmento HTMX, eventos Socket.IO e
  o snapshot/fila de operações offline.
- Atualização do shell PWA e da versão de cache para distribuir os ativos.
- Contratos Pytest, validação sintática JavaScript e cenários manuais
  responsivos.

### Excluído

- Alterar o cálculo financeiro autoritativo do servidor ou os limiares atuais
  de 80%, 95% e 100%.
- Criar notificações persistentes, endpoints, tabelas ou migrações.
- Fixar os banners detalhados; eles continuam no fluxo normal para não ocupar
  excessivamente a tela móvel.
- Alterar a tela de compra finalizada, cancelada ou os resumos de índices.
- Criar a infraestrutura Playwright, acompanhada pela BL-0011.
- Integrar ou remover branches de outras demandas correlatas.

## Riscos e regras preservadas

- Regras de negócio afetadas: somente apresentação; `get_execution_totals` e
  `check_budget_alerts` permanecem as fontes autoritativas no servidor.
- Segurança e permissões: operar apenas sobre o DOM e snapshot da execução já
  autorizada; não introduzir IDs ou consultas vindos do cliente.
- LGPD: não registrar nem transmitir dados adicionais; toasts são efêmeros.
- Isolamento por grupo: preservar rotas e consultas existentes; o cálculo local
  filtra pelo ID da execução exibida.
- Offline e sincronização: estado local é a fonte visual durante a desconexão;
  o servidor reassume após sincronização, sem depender do Socket.IO.
- Histórico financeiro: nenhuma atualização local substitui a persistência ou
  altera execuções finalizadas.
- Recorrência: `N/A` — nenhuma alteração em datas, status ou geração futura.
- Separação entre template e execução: usar exclusivamente orçamento e itens da
  execução atual, sem propagar valores ao template.

## Plano de implementação

### Etapa 1 — Acompanhamento contínuo do orçamento

#### Ticket 1.1 — Entregar resumo fixo, alertas e atualização resiliente

##### Fatia 1.1.1 — Implementar o contrato completo da BL-0014

- Ordem: `1`
- Objetivo da fatia: escrever os contratos TDD do escopo e entregar o resumo
  fixo com atualização online, colaborativa e offline em uma mudança coesa.
- Dependências: aprovação explícita deste refinamento; compatibilizar os
  atributos do fragmento caso a BL-0013 seja integrada antes da implementação.
- Arquivos esperados:
  - `app/templates/pages/executions/_items_fragment.html`
  - `app/static/css/jaci-theme.css`
  - `app/static/js/execution-budget.js`
  - `app/static/js/execution-sync.js`
  - `app/static/js/offline-cache.js`
  - `app/static/js/service-worker.js`
  - `tests/test_sticky_budget.py`
  - `tests/test_offline_cache.py`
  - `tests/test_pwa.py`
- Validações focadas:
  - `node --check app/static/js/execution-budget.js`
  - `node --check app/static/js/execution-sync.js`
  - `node --check app/static/js/offline-cache.js`
  - `timeout 180 venv/bin/pytest tests/test_sticky_budget.py tests/test_agenda_and_budget_flow.py tests/test_execution_totals_regression.py tests/test_offline_cache.py tests/test_pwa.py --no-cov`
- Documentação a atualizar:
  - item e refinamento `BL-0014`
  - `tests/README.md`, se o contrato ganhar entrada na matriz vigente

## Cenários TDD

Estes cenários devem ser escritos como testes antes da implementação, depois da
aprovação explícita deste refinamento.

1. Dada uma execução em andamento com orçamento positivo, o fragmento expõe o
   resumo fixo e os dados necessários para total, orçamento, percentual, faixa
   e mensagem; uma compra agendada usa o cartão normal e uma compra sem
   orçamento não o renderiza.
2. Dado um resumo fixo, a posição acompanha a altura real da navbar, mantém
   `z-index` inferior ao menu e não cobre o primeiro grupo durante a rolagem em
   viewport móvel ou desktop.
3. Dada uma resposta HTMX ou atualização Socket.IO, o resumo substituído exibe
   os novos valores e preserva um único controlador e um único toast.
4. Dado um total que sobe de abaixo de 80% para as faixas de 80%, 95% ou 100%,
   o controlador atualiza barra/cor e exibe a mensagem retornada pela regra de
   orçamento no toast.
5. Dada uma atualização dentro da mesma faixa ou a repetição do mesmo evento
   por fragmento e WebSocket, nenhum toast duplicado é exibido.
6. Dado um total que cai para uma faixa inferior, nenhum toast é exibido e a
   faixa superior fica rearmada para uma subida futura.
7. Dada a abertura de uma página já em faixa de alerta, o resumo e o banner são
   renderizados, mas a carga inicial não gera toast retrospectivo.
8. Dada uma compra offline, comprar, desmarcar ou remover um item atualiza o
   snapshot local e recalcula imediatamente total, percentual, barra e toast;
   a sincronização posterior converge para o fragmento do servidor sem alerta
   duplicado.
9. Dada uma execução ou item de outro grupo, nenhuma nova interface permite
   acessá-lo e as validações de autorização existentes permanecem inalteradas.
10. Dado o cache PWA anterior, a nova versão remove os caches antigos e inclui
    o controlador de orçamento no shell disponível offline.

### Contratos de etapas futuras

- A cobertura Playwright real permanece futura e rastreada pela BL-0011. Não há
  `xfail(strict=True)` planejado no escopo executável desta demanda.

## Estratégia de validação

### Por fatia

- Criar os contratos TDD completos antes de alterar o comportamento de
  produção.
- Executar os testes focados e as verificações sintáticas JavaScript.
- Validar Jinja2 por renderização das variantes em andamento, agendada, sem
  orçamento e nas três faixas de alerta.
- Atualizar a versão do cache PWA e confirmar o inventário do shell.
- Executar `venv/bin/graphify update .` após as mudanças de código.
- Atualizar item, refinamento e contagem de progresso antes do commit.

### Validação manual

1. Em viewport móvel e desktop, abrir compra longa com orçamento, rolar e
   confirmar que o resumo permanece sob a navbar sem encobrir itens ou ações.
2. Abrir e fechar o menu móvel, redimensionar a janela e confirmar o ajuste do
   deslocamento e da área útil.
3. Comprar e desmarcar itens online atravessando 80%, 95% e 100%, confirmando
   valores, cores, banner e um toast por subida de faixa.
4. Repetir alterações por outro cliente conectado e confirmar atualização
   visual sem toast duplicado.
5. Repetir comprar, desmarcar e remover offline, recarregar a página cacheada e
   sincronizar, confirmando o total local e a convergência posterior.
6. Abrir compra agendada, compra sem orçamento e compra finalizada para
   confirmar ausência de comportamento fixo indevido.

### Regressão total

Executar quando a fatia estiver concluída e não houver contratos pendentes:

- `venv/bin/alembic upgrade head`
- `timeout 240 venv/bin/pytest`
- UI Playwright: infraestrutura ausente no Jaci; cenários registrados acima e
  validação manual obrigatória até a BL-0011 disponibilizá-la.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 / Ticket 1.1 — Resumo fixo e resiliente | `1/1` | `0` | Concluído |

## Fechamento

- Commits/PRs: `6c6bd17`, correção `440a68d` e compatibilidade pós-merge
  `76c55fb`
- Resultado das validações focadas: 55 testes aprovados na entrega original,
  incluindo duas instâncias concorrentes do controlador com apenas um toast;
  após o merge com `develop`, 44 testes de filtro, orçamento fixo e offline
  aprovados; `node --check` aprovado para `item-filter.js`,
  `execution-budget.js` e `offline-cache.js`; migrações no head
- Resultado da validação manual: o aceite da versão `1.2.0` em produção foi
  informado pelo usuário; a infraestrutura Playwright futura permanece
  acompanhada pela BL-0011
- Resultado da regressão total: após o merge com `develop`, 186 testes
  aprovados e 5 `xfail` legados fora do escopo
- `xfail(strict=True)` pendentes no escopo: nenhum
- Documentação atualizada: item, índice, este refinamento, matriz de testes e
  grafo do projeto; o grafo malformado pelo merge foi reconstruído em modo
  AST-only e voltou a aceitar consultas
- Observação de lint: `venv/bin/pylint` não está instalado; nenhum arquivo
  Python de produção foi alterado
- Publicação: produção, versão `1.2.0`, tag `v1.2.0` no commit `7364294`,
  publicada em `2026-08-05`
