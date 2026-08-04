# Refinamento — BL-0016 — Botão flutuante para adicionar itens

## Rastreabilidade

- Item de backlog: [BL-0016](../backlog/items/BL-0016-botao-flutuante-adicionar-itens.md)
- Branch: `feature/BL-0016-botao-flutuante-adicionar-itens`
- Responsável pelo refinamento: Engenharia Jaci
- Estado do refinamento: `concluido`
- Itens relacionados: `BL-0011`, `BL-0013`, `BL-0014` e `BL-0015`
- Revisão de produto: em `2026-08-04`, o link que rolava até o formulário
  foi rejeitado por retirar o usuário da posição atual; esta versão o substitui
  por um modal.
- Aprovação de implementação: emitida explicitamente em `2026-08-04`, depois
  do commit documental `b777d55`.

## Objetivo e critérios de sucesso

### Objetivo

Manter a adição de itens acessível durante toda a rolagem das telas de
detalhe de Lista e Compra por meio de um botão flutuante que abre o formulário
existente em modal, sem retirar o usuário da posição atual nem duplicar campos,
regras, estado ou persistência.

### Critérios de sucesso

1. A Lista e as Compras `scheduled` e `in_progress` exibem um único FAB de
   adição enquanto a mutação correspondente estiver disponível.
2. Ao ativar o FAB por toque, clique ou teclado, o formulário único abre em
   modal sem modificar a posição vertical da página e o foco vai para
   **Nome do item**.
3. Fechar por **Cancelar**, botão de fechamento ou `Esc` conserva a rolagem e
   devolve o foco ao FAB que abriu o modal.
4. Uma inclusão bem-sucedida atualiza os itens visíveis, fecha e limpa o modal
   e devolve foco e controle ao mesmo ponto da lista, sem recarregar a página.
5. Erro de validação mantém o modal aberto, preserva os valores informados e
   apresenta feedback acessível sem persistência parcial.
6. O modal possui título associado, semântica adequada, foco contido enquanto
   aberto e controles alcançáveis em viewport móvel e desktop.
7. Existe somente um formulário canônico por tela. Sem JavaScript, o FAB fica
   indisponível e esse mesmo formulário é apresentado inline como fallback.
8. O FAB respeita `safe-area-inset`, permanece acima do indicador global de
   sincronização e não encobre itens, alertas, ações nem o footer.
9. A Compra continua usando o mesmo `data-offline-add-item`: agendada cria item
   pendente, em andamento exige valor e cria item comprado, e a fila offline
   permanece a fonte local da operação.
10. Execuções finalizadas ou canceladas não expõem o FAB; permissões,
    isolamento por grupo e validações continuam no servidor.
11. O controlador do modal e o CSS são locais e versionados no cache PWA; abrir
    e fechar o modal offline não depende do CDN do Bootstrap, da API ou de
    WebSocket.

## Escopo

### Incluído

- FAB com nome acessível, ícone decorativo, foco visível e uso do padrão
  `.btn-fab` existente.
- Um modal server-rendered por tela, com o formulário atual movido integralmente
  para ele, sem segunda cópia do `form` nem de seus campos.
- Controlador Vanilla JavaScript local para abertura, foco inicial, contenção
  de foco, fechamento por todos os controles, restauração de foco e preservação
  de `scrollY`, com fallback no utilitário local `JaciModal` quando necessário.
- Apresentação responsiva: modal compacto em desktop e adequado à altura/largura
  disponível em mobile, sem esconder campos quando o teclado virtual abrir.
- Modificador CSS do FAB para área segura, distância do status de sincronização
  e espaço reservado ao final do conteúdo.
- Fallback progressivo sem JavaScript que oculta o FAB e exibe inline o mesmo
  formulário, preservando a capacidade básica de adicionar.
- Atualização HTMX da lista de itens de Template após adição, com extração de
  fragmento reutilizável e manutenção do POST/redirect como fallback sem JS.
- Reuso da atualização HTMX e da fila offline já existentes na Compra, fechando
  o modal somente depois de uma resposta ou enfileiramento bem-sucedido.
- Feedback de validação dentro do modal, sem limpar campos ou fechar em erro.
- Contratos automatizados de estrutura, acessibilidade, estados mutáveis,
  preservação de posição, HTMX, offline e distribuição PWA.
- Cenários futuros de navegador documentados para a BL-0011 e validação
  manual mobile/desktop neste item enquanto `tests/ui` não existe no Jaci.

### Excluído

- Manter um formulário inline e outro no modal, clonar campos ou sincronizar
  valores entre duas instâncias.
- Criar endpoint novo, serviço, modelo, migração ou regra de persistência.
- Alterar payloads, IndexedDB, semântica da fila de sincronização ou eventos
  WebSocket da Compra.
- Tornar a adição de itens de Template offline; o fallback sem JavaScript
  preserva a submissão online atual.
- Exibir o FAB em Compra finalizada/cancelada ou em outras páginas.
- Alterar filtros, resumo de orçamento, regras financeiras ou semântica de item
  planejado/comprado entregues pelas BL-0013 a BL-0015.
- Criar infraestrutura Playwright, Page Objects ou arquivos em `tests/ui`; essa
  capacidade continua acompanhada pela BL-0011.
- Reposicionar o FAB de criação de Compra da Agenda, salvo correção
  compartilhada estritamente necessária e coberta por contrato deste item.

## Riscos e regras preservadas

- Regras de negócio afetadas: nenhuma regra nova; o modal apenas hospeda o
  formulário atual e a resposta continua determinada pelas rotas e serviços.
- Segurança e permissões: o FAB e o modal não autorizam operações. Rotas atuais
  continuam exigindo usuário autenticado e recurso autorizado.
- LGPD: nenhum dado pessoal, texto ou valor adicional é coletado, persistido ou
  registrado em log pelo modal.
- Isolamento por grupo: template, execução e categoria permanecem validados no
  servidor; respostas HTMX usam o recurso já limitado ao grupo autenticado.
- Offline e sincronização: o controlador de modal é local e armazenado no shell;
  a Compra conserva `data-offline-add-item`, fila, retentativa e reconciliação.
  Falha de rede ou WebSocket não fecha nem perde o formulário indevidamente.
- Histórico financeiro: quantidade e valor continuam definidos exclusivamente
  pelo formulário e serviço atuais; nenhum total ou registro histórico muda.
- Recorrência: `N/A` — não há mudança na finalização, data-base ou criação da
  próxima execução.
- Separação entre template e execução: cada modal conserva seu próprio
  formulário e endpoint; nenhuma alteração é propagada entre domínios.

## Plano de implementação

### Etapa 1 — Adição contextual por modal nas telas mutáveis

#### Ticket 1.1 — Abrir, submeter e fechar sem perder a posição

##### Fatia 1.1.1 — Contratos TDD e fluxo modal completo online/offline

- Ordem: `1`
- Objetivo da fatia: escrever os contratos executáveis de todo o escopo e
  entregar, em uma unidade coerente, o formulário único em modal, preservação
  de rolagem/foco, atualização parcial das listas e distribuição PWA.
- Dependências: aprovação explícita desta revisão; BL-0013, BL-0014 e BL-0015
  já integradas em `develop`.
- Arquivos esperados:
  - `tests/test_item_add_fab.py`
  - `tests/test_template_execution_flow.py`
  - `tests/test_offline_cache.py`
  - `tests/test_pwa.py`
  - `app/templates/pages/templates/detail.html`
  - `app/templates/pages/templates/_items_fragment.html`
  - `app/templates/pages/executions/in_progress.html`
  - `app/routers/templates.py`
  - `app/static/js/item-add-modal.js`
  - `app/static/css/jaci-theme.css`
  - `app/static/js/service-worker.js`
  - `tests/README.md`
  - este refinamento e o item `BL-0016`
- Validações focadas:
  - `node --check app/static/js/item-add-modal.js`
  - `timeout 180 venv/bin/pytest tests/test_item_add_fab.py tests/test_template_execution_flow.py tests/test_offline_cache.py tests/test_pwa.py --no-cov`
  - `timeout 180 env PYTHONPATH=. venv/bin/pylint app/routers/templates.py --errors-only`
  - validar manualmente toque, teclado, foco, rolagem, erro, sucesso e adição
    online/offline em viewport móvel e desktop
- Documentação a atualizar:
  - `tests/README.md`
  - este refinamento e o item `BL-0016`

## Cenários TDD

Estes cenários devem ser escritos como testes antes da implementação, depois
da aprovação explícita desta revisão.

1. Dado o detalhe de uma Lista, existe um único FAB com nome acessível que abre
   um modal associado ao único formulário de adição da página.
2. Dada uma Compra `scheduled` ou `in_progress`, FAB, modal e formulário são
   renderizados pela mesma condição; Compra `completed` ou `cancelled` não
   expõe a ação.
3. Dada uma posição arbitrária em lista longa, abrir e fechar o modal não muda
   `scrollY`; ao abrir, o nome recebe foco e, ao fechar, o foco retorna ao FAB.
4. Dado uso por teclado, `Esc`, fechar e cancelar encerram o modal, a ordem de
   tabulação permanece contida e todos os controles possuem nomes acessíveis.
5. Dada uma Lista com JavaScript, a inclusão válida usa o endpoint atual via
   HTMX, atualiza somente o fragmento de itens, limpa e fecha o modal sem
   recarregar nem reposicionar a página.
6. Dada uma Lista sem JavaScript, o FAB fica oculto, o mesmo formulário aparece
   inline e o POST/redirect atual continua funcional.
7. Dado nome ausente ou erro do servidor, o modal continua aberto, preserva os
   valores e apresenta mensagem acessível sem trocar o fragmento por erro.
8. Dada uma Compra agendada, a submissão pelo modal cria item pendente; dada a
   Compra em andamento, exige valor e cria item comprado, sem mudar os campos,
   endpoint ou regras atuais.
9. Dada uma Compra sem conexão, o formulário conserva `data-offline-add-item`,
   enfileira a operação, renderiza o item temporário e fecha o modal somente
   depois do enfileiramento local bem-sucedido.
10. Dada falha de rede, validação ou enfileiramento, o modal permanece aberto e
    os dados não são descartados; WebSocket não participa da decisão.
11. Dado Bootstrap indisponível por falta de rede, o controlador local usa o
    fallback modal do Jaci para abrir, fechar e restaurar foco/rolagem.
12. Dado o indicador global de sincronização e `safe-area-inset`, FAB, modal,
    último item, alertas e footer continuam visíveis e acionáveis.
13. Dada a publicação dos ativos atualizados, a versão do cache PWA muda,
    inclui o controlador local e invalida o shell anterior.
14. Dadas as duas telas, existe exatamente um `form` de adição e não há novo
    endpoint, payload de sincronização ou regra de persistência.

### Contratos de etapas futuras

- Não há `xfail(strict=True)` planejado: a fatia única implementa todo o
  escopo executável desta demanda.
- A cobertura Playwright permanece futura na BL-0011. Cenários propostos:
  Lista longa abre/fecha sem mudar `scrollY`; Lista adiciona e atualiza o
  fragmento sem recarga; Compra agendada online; Compra em andamento online;
  Compra em andamento offline com item temporário; erro preserva o modal e os
  campos; teclado mantém foco contido e o devolve ao FAB; Compra concluída não
  apresenta o FAB.

## Estratégia de validação

### Por fatia

- Escrever todos os contratos da fatia antes de alterar templates, rota ou
  ativos.
- Executar os testes estruturais, de fluxo de Template, offline e PWA
  diretamente relacionados.
- Verificar sintaxe do controlador JavaScript e lint da rota alterada.
- Confirmar que nenhum serviço, modelo, migração, payload offline ou arquivo em
  `tests/ui` foi alterado.
- Validar visualmente mobile-first e desktop: foco, rolagem, teclado virtual,
  erros, sucesso e convivência com o status de sincronização.
- Atualizar item, refinamento, rastreabilidade de testes e resultados antes do
  commit da fatia.

### Validação manual

1. Em viewport móvel estreita, abrir uma Lista longa, registrar a posição,
   ativar o FAB e confirmar modal aberto, fundo imóvel e foco em **Nome**.
2. Fechar por `Esc`, botão e **Cancelar**; em cada caso confirmar a mesma
   posição e foco devolvido ao FAB.
3. Adicionar item válido na Lista e confirmar atualização do fragmento, modal
   fechado, campos limpos e permanência no ponto anterior.
4. Provocar erro de validação e confirmar modal aberto, valores preservados e
   mensagem acessível; repetir com JavaScript desabilitado e validar o
   formulário inline/POST tradicional.
5. Repetir abertura e inclusão em Compra agendada e em andamento, confirmando
   respectivamente item pendente e item comprado com valor obrigatório.
6. Sem conexão, adicionar na Compra em andamento e confirmar item temporário,
   totais provisórios e fila; reconectar e confirmar reconciliação sem
   duplicação.
7. Simular indisponibilidade do Bootstrap CDN e confirmar que o controlador
   local abre/fecha o modal sem mover a página ou perder foco.
8. Com status de sincronização normal, offline e pendente, confirmar que FAB,
   status, alertas, último item e footer permanecem acionáveis e legíveis.
9. Abrir Compra concluída e confirmar ausência do FAB; Compra cancelada continua
   seguindo o redirecionamento atual.

### Regressão total

Como a fatia única fecha todo o ticket, executar ao concluí-la e sem
`xfail(strict=True)` deste escopo:

- `venv/bin/alembic upgrade head`
- `timeout 240 venv/bin/pytest`
- UI Playwright: infraestrutura ainda ausente no Jaci; registrar validação
  manual e manter os oito cenários propostos na BL-0011.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 / Ticket 1.1 — Adição contextual por modal | `1/1` | `0` | Concluído |

## Fechamento

- Commits/PRs: commit da fatia a registrar no fechamento de rastreabilidade;
  branch `feature/BL-0016-botao-flutuante-adicionar-itens`.
- Resultado das validações focadas: 97 testes aprovados; sintaxe de
  `item-add-modal.js`, `offline-cache.js` e `service-worker.js` aprovada;
  módulos Python compilados sem erro. O `pylint` não está instalado no
  ambiente virtual e a opção `--no-cov` não está disponível nesta instalação
  do pytest.
- Resultado da validação manual: pendente em navegador real; infraestrutura
  Playwright continua acompanhada pela BL-0011 e não foi criada neste item.
- Resultado da regressão total: migrações no head; 209 testes aprovados e 5
  `xfail` legados fora do escopo.
- `xfail(strict=True)` pendentes no escopo: nenhum.
- Documentação atualizada: item, índice, rastreabilidade de testes e este
  refinamento; grafo atualizado após a implementação.
