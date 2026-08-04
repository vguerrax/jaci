# Refinamento — BL-0016 — Botão flutuante para adicionar itens

## Rastreabilidade

- Item de backlog: [BL-0016](../backlog/items/BL-0016-botao-flutuante-adicionar-itens.md)
- Branch: `feature/BL-0016-botao-flutuante-adicionar-itens`
- Responsável pelo refinamento: Engenharia Jaci
- Estado do refinamento: `pronto_para_implementacao`
- Itens relacionados: `BL-0011`, `BL-0013`, `BL-0014` e `BL-0015`

## Objetivo e critérios de sucesso

### Objetivo

Manter a adição de itens acessível durante toda a rolagem das telas de
detalhe de Lista e Compra por meio de um botão flutuante mobile-first que leva
ao formulário existente, sem duplicar campos, regras, estado ou persistência.

### Critérios de sucesso

1. A Lista e as Compras `scheduled` e `in_progress` exibem um único botão
   flutuante de adição enquanto o formulário correspondente estiver disponível.
2. Ao ativar o botão por toque, clique ou teclado, o navegador leva ao primeiro
   campo do formulário existente e permite digitar o nome sem procurar
   manualmente a área de adição.
3. O atalho é um link de fragmento nativo e continua funcional sem JavaScript;
   nenhuma cópia do formulário, modal ou novo endpoint é criado.
4. O controle tem nome acessível, foco visível e alvo com margem de rolagem
   compatível com a navegação fixa.
5. O botão respeita `safe-area-inset`, permanece acima do indicador global de
   sincronização e não encobre o fim da lista nem ações importantes em
   viewports móveis ou desktop.
6. A Compra continua submetendo exatamente o formulário
   `data-offline-add-item`: agendada cria item pendente, em andamento exige
   valor e cria item comprado, e a fila offline permanece inalterada.
7. Execuções finalizadas ou canceladas não passam a expor a ação; permissões,
   isolamento por grupo e validações continuam no servidor.
8. A versão do cache PWA distribui o contrato visual atualizado sem depender de
   uma conexão contínua depois que a página estiver armazenada.

## Escopo

### Incluído

- Identificadores estáveis, exclusivos e rótulos acessíveis no primeiro campo
  de nome dos formulários de Lista e Compra.
- Link flutuante com `href` para o campo da tela corrente, nome acessível,
  ícone decorativo e uso do padrão visual `.btn-fab` existente.
- Modificador CSS específico para posicionar o atalho acima do status de
  sincronização, considerar áreas seguras, preservar foco visível e reservar
  espaço ao final do conteúdo.
- Margem de rolagem no alvo para que o campo não fique escondido sob a barra de
  navegação fixa.
- Renderização condicional acoplada à disponibilidade do formulário atual:
  Lista e Compra agendada/em andamento.
- Contratos automatizados de estrutura, acessibilidade, estados permitidos,
  preservação offline e distribuição PWA.
- Cenários futuros de navegador documentados para a BL-0011 e validação
  manual mobile/desktop neste item enquanto `tests/ui` não existe no Jaci.

### Excluído

- Duplicar ou mover o formulário para modal, offcanvas ou novo componente.
- Alterar rotas, serviços, banco de dados, payloads, IndexedDB, fila de
  sincronização ou eventos WebSocket.
- Tornar a adição de itens de template offline; o comportamento atual dessa
  submissão é preservado.
- Exibir o atalho em Compra finalizada/cancelada ou em outras páginas.
- Alterar filtros, resumo de orçamento, regras financeiras ou semântica de
  item planejado/comprado entregues pelas BL-0013 a BL-0015.
- Criar infraestrutura Playwright, Page Objects ou arquivos em `tests/ui`; essa
  capacidade continua acompanhada pela BL-0011.
- Reposicionar o FAB de criação de Compra existente na Agenda, salvo correção
  compartilhada estritamente necessária e coberta pelos contratos deste item.

## Riscos e regras preservadas

- Regras de negócio afetadas: nenhuma regra nova; o atalho somente alcança o
  formulário existente e não altera o resultado da submissão.
- Segurança e permissões: o link não carrega IDs novos nem envia dados. Rotas
  atuais continuam exigindo usuário autenticado e recurso autorizado.
- LGPD: nenhum dado pessoal, texto ou valor adicional é coletado, persistido ou
  registrado em log.
- Isolamento por grupo: template, execução e categoria permanecem validados no
  servidor; o fragmento aponta somente para elemento da página autorizada.
- Offline e sincronização: navegação por fragmento funciona sem JavaScript; na
  Compra, a submissão conserva `data-offline-add-item`, fila, retentativa e
  reconciliação atuais. O cache PWA deve entregar o CSS compatível.
- Histórico financeiro: quantidade e valor continuam definidos exclusivamente
  pelo formulário e serviço atuais; nenhum total ou registro histórico muda.
- Recorrência: `N/A` — não há mudança na finalização, data-base ou criação da
  próxima execução.
- Separação entre template e execução: cada página conserva seu próprio
  formulário e endpoint; nenhuma alteração é propagada entre eles.

## Plano de implementação

### Etapa 1 — Atalho flutuante progressivo nas telas mutáveis

#### Ticket 1.1 — Disponibilizar e distribuir o acesso ao formulário existente

##### Fatia 1.1.1 — Contratos TDD e FAB acessível com fallback nativo

- Ordem: `1`
- Objetivo da fatia: escrever os contratos executáveis de todo o escopo e
  implementar, em uma unidade pequena, o link nativo, os alvos estáveis, a
  apresentação responsiva e a distribuição PWA, sem tocar na persistência.
- Dependências: aprovação explícita deste refinamento; BL-0013, BL-0014 e
  BL-0015 já integradas em `develop`.
- Arquivos esperados:
  - `tests/test_item_add_fab.py`
  - `tests/test_offline_cache.py`
  - `tests/test_pwa.py`
  - `app/templates/pages/templates/detail.html`
  - `app/templates/pages/executions/in_progress.html`
  - `app/static/css/jaci-theme.css`
  - `app/static/js/service-worker.js`
  - `tests/README.md`
  - este refinamento e o item `BL-0016`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_item_add_fab.py tests/test_offline_cache.py tests/test_pwa.py --no-cov`
  - confirmar que somente os estados mutáveis renderizam o atalho de Compra
  - validar manualmente toque, teclado, rolagem, sobreposição e adição online
    e offline em viewport móvel e desktop
- Documentação a atualizar:
  - `tests/README.md`
  - este refinamento e o item `BL-0016`

## Cenários TDD

Estes cenários devem ser escritos como testes antes da implementação, depois
da aprovação explícita deste refinamento.

1. Dado o detalhe de uma Lista, existe um único FAB com nome acessível e
   `href` apontando para o primeiro campo do formulário de adição existente.
2. Dada uma Compra `scheduled` ou `in_progress`, o FAB é renderizado dentro da
   mesma condição do formulário; uma Compra `completed` ou `cancelled` não
   expõe a ação.
3. Dado JavaScript indisponível, ativar o link de fragmento ainda navega até o
   campo de nome focável, sem depender de Bootstrap, HTMX ou WebSocket.
4. Dado uso por teclado ou leitor de tela, o controle anuncia "Adicionar item",
   o ícone é decorativo e o foco do FAB e do campo permanece visível.
5. Dada uma lista longa em viewport móvel, o alvo usa margem de rolagem para não
   ficar sob a navbar e o fim do conteúdo reserva espaço para o FAB.
6. Dado o indicador global de sincronização no canto inferior, o modificador do
   FAB usa área segura e deslocamento vertical que impedem sobreposição.
7. Dada a Compra agendada, o atalho alcança o formulário que cria item pendente;
   dada a Compra em andamento, alcança o mesmo formulário que exige valor e cria
   item comprado, sem alterar campos nem endpoint.
8. Dada uma Compra sem conexão, o formulário alcançado conserva
   `data-offline-add-item`, `data-execution-id` e `data-execution-status`, e a
   operação continua usando a fila existente.
9. Dadas as duas telas, não existe segundo formulário, modal, payload ou handler
   de adição introduzido pelo atalho.
10. Dada a publicação do CSS atualizado, a versão do cache PWA muda e invalida
    o shell anterior para entregar o posicionamento compatível.

### Contratos de etapas futuras

- Não há `xfail(strict=True)` planejado: a fatia única implementa todo o
  escopo executável desta demanda.
- A cobertura Playwright permanece futura na BL-0011. Cenários propostos:
  Lista longa com toque/clique e foco; Compra agendada online; Compra em
  andamento online; Compra em andamento offline com item temporário; navegação
  por teclado; ausência do FAB em Compra concluída.

## Estratégia de validação

### Por fatia

- Escrever todos os contratos da fatia antes de alterar templates ou CSS.
- Executar os testes estruturais, de offline e PWA diretamente relacionados.
- Confirmar que nenhum arquivo de rota, serviço, modelo, migração ou
  `tests/ui` foi alterado.
- Validar visualmente mobile-first e desktop, inclusive navegação por teclado,
  foco, rolagem e convivência com o status de sincronização.
- Atualizar item, refinamento, rastreabilidade de testes e resultados antes do
  commit da fatia.

### Validação manual

1. Em viewport móvel estreita, abrir uma Lista longa, rolar até o fim, ativar o
   FAB por toque e confirmar que o campo **Nome do item** fica visível e focado.
2. Repetir por teclado em viewport desktop e confirmar nome acessível, foco
   visível e submissão pelo formulário original.
3. Abrir Compra agendada e Compra em andamento, confirmar que o atalho alcança
   respectivamente o formulário sem valor e o formulário com valor obrigatório.
4. Sem conexão, ativar o FAB da Compra em andamento, adicionar um item e
   confirmar item temporário, totais provisórios e fila existentes; reconectar e
   confirmar reconciliação sem duplicação.
5. Com status de sincronização normal, offline e com pendências, confirmar que
   FAB, status, alertas, último item e footer permanecem acionáveis e legíveis.
6. Abrir Compra concluída e confirmar ausência do FAB; Compra cancelada continua
   seguindo o redirecionamento atual.

### Regressão total

Como a fatia única fecha todo o ticket, executar ao concluí-la e sem
`xfail(strict=True)` deste escopo:

- `venv/bin/alembic upgrade head`
- `timeout 240 venv/bin/pytest`
- UI Playwright: infraestrutura ainda ausente no Jaci; registrar validação
  manual e manter os seis cenários propostos na BL-0011.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 / Ticket 1.1 — Atalho flutuante progressivo | `0/1` | `1` | Pendente |

## Fechamento

- Commits/PRs: ainda não iniciados.
- Resultado das validações focadas: ainda não executadas.
- Resultado da validação manual: ainda não executada.
- Resultado da regressão total: ainda não executada.
- `xfail(strict=True)` pendentes no escopo: nenhum planejado.
- Documentação atualizada: item, índice e este refinamento; rastreabilidade de
  testes será atualizada na implementação.
