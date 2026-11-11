# Refinamento da versão 1.5.0 — Acesso à conta e continuidade da sessão

## Rastreabilidade e aprovação

- Coordenação: [roadmap](../backlog/releases.md); responsável: Engenharia Jaci.
- Demandas: [BL-0010](../backlog/items/BL-0010-reset-senha-login-area-logada.md)
  e [BL-0019](../backlog/items/BL-0019-sessao-autenticada-oito-horas-inatividade.md).
- Refinamentos: [BL-0010](BL-0010-reset-senha-login-area-logada.md) e
  [BL-0019](BL-0019-sessao-autenticada-oito-horas-inatividade.md).
- Data: 2026-11-10. Estado documental: pronto_para_implementacao, aguardando
  aprovação explícita destes documentos versionados; nenhuma execução liberada.
- Branch documental: docs/refinamento-1.5.0, criada na worktree atual a partir de
  9d6a18c, que registra o aborto/replanejamento. Mantidos o backup legado e piso
  de cobertura de 60%. Não criar outras worktrees.

## Resultado esperado

Recuperar/trocar senha pelo Jaci usando o Tupã e manter a sessão por oito horas
após a última requisição autenticada, com encerramento verificável e sem perda
da fila offline. A versão não inclui criptografia, cópia automática ou retomada
das BL-0007/BL-0009, abortadas. O backup diário em dump e cópia manual permanecem.

## Decisões explícitas do usuário

1. Cada requisição ao servidor autenticada com a sessão renova o prazo de oito
   horas. Inclui navegação, HTMX, APIs, polling e sincronização automática; o
   critério é chegada ao servidor e autenticação, não detectar interação humana.
2. Pings/pongs do WebSocket não contam. Frames da conexão, broadcasts e o
   simples socket aberto não renovam. O handshake HTTP autenticado, inclusive
   uma nova conexão, conta como request; atualizações de fragmento por HTTP
   também contam se chegarem autenticadas ao servidor.
3. Recuperar ou trocar a senha exige novo login em todos os dispositivos,
   preservando operações de compra pendentes e sem reaproveitá-las para outra conta.
4. O comportamento é passivo como a referência Potira: não criar heartbeat,
   polling, timer de logout ou formulário em memória para prolongar a sessão.
   Não importar os limites de 1h/12h ou a filtragem de requests do Potira: no Jaci
   o limite aprovado é 8h de inatividade por requisições autenticadas.

O usuário corrigiu a proposta inicial de atividade humana: ela foi substituída
pela regra acima. Não usar marcadores X-Activity, foco ou presença como requisito.
Requests automáticos existentes podem manter uma aba autenticada indefinidamente
se ocorrerem antes de oito horas; isso decorre da regra aprovada, não de um novo
job. Sem requests, a sessão vence; o próximo acesso decide autorização.

## Diagnóstico e fontes locais

Inspeção estática do Jaci em 9d6a18c; nenhum login, relógio de sessão, banco ou
serviço foi exercitado. A duração efetiva da produção não foi medida.

| Fonte | Constatação |
| --- | --- |
| app/utils/security.py | Cookie jaci_session com max_age=expires_in e jaci_refresh de 30 dias |
| app/main.py:add_unread_count | Renovação em qualquer requisição com refresh quando JWT inválido/ausente; sem prazo local de inatividade e sem lock compartilhado |
| app/dependencies.py e app/services/tupa_auth_service.py | JWT por JWKS; não há estado local revogável de sessão nem introspecção remota |
| app/routers/auth.py | Troca no perfil é stub 501, mínimo legado de seis caracteres; recuperação pública não está implementada |
| app/templates/pages/login.html e profile.html | Login sem recuperação; perfil remete ao Tupã |
| app/static/js/service-worker.js | Navegações de autenticação não têm exclusão explícita do cache |
| app/static/js/offline-cache.js | 401 preserva fila; /auth/logout executa clearLocalCache e precisa de tratamento distinto para término por senha |
| app/static/js/execution-sync.js e websocket/handlers.py | JWT exposto na query/log do socket; autenticação só na abertura e ping periódico |

Tupã local: develop, 4cee88f55b487c89b4531115c13bd22a2cfad17e; repositório limpo
na inspeção, somente leitura. Fontes: app/routers/auth.py, schemas/auth.py,
services/auth_service.py, security.py, models/auth.py e docs/consumer-api.md.
O access token tem padrão de 15 minutos e refresh de sete dias; valores são do
código, não da configuração real. Refresh rotaciona/revoga o anterior. Reset usa
opaco de uma hora e revoga refresh; troca autenticada não revoga refresh.
Validação de access é por assinatura/prazo, sem consulta de revogação.

Potira local: f17047c7, referência somente leitura em app/core/access_sessions.py,
app/services/access_session_service.py, app/repositories/access_sessions.py,
app/models/access_session.py, docs/TUPA.md e testes de BL-0044. A referência útil
é sessão opaca persistida, refresh sob lock e decisão passiva no request. O código
atual do Potira filtra requests automáticos e tem limite absoluto: esses detalhes
não são o contrato aprovado pelo usuário para o Jaci e não serão copiados.

## Dependência externa D-01 — Revogação no Tupã

Contrato publicado no Tupã 1.1.0, confirmado pelo usuário em 2026-11-11.
Implementação em `e30b639`, publicador em `47b262f` e integração à main do
Tupã em `78244b6`. O repositório Tupã registra a entrega em
`docs/release-1.1.0.md` e `docs/consumer-api.md`. A instância de testes foi
informada na porta 8005.

- Reset, troca autenticada e logout invalidam os access e refresh tokens
  anteriores da conta no produto. Mudança de senha e revogação compartilham
  transação e trava de usuário com emissão e refresh.
- `POST /auth/session/validate` exige `X-Service-Token` e recebe
  `{"access_token":"…"}`. A resposta ativa contém `active/sub/product_id/exp`.
  Token inválido, vencido ou de outro produto retorna `200 {"active":false}`.
  Credencial de produto inválida retorna `401`. Indisponibilidade retorna
  `503`. A consulta não rotaciona tokens nem registra atividade.
- O Jaci deve conferir essa validade antes de autorizar HTTP, handshake e
  entregas WS protegidas. O prazo local de oito horas é rechecado antes de
  refresh e após chamadas lentas.
- `POST /auth/reset-password` mantém o token opaco. O envio da credencial de
  serviço vincula o reset ao produto consumidor. O Jaci deve enviar essa
  credencial e preservar o token fora de logs e cache.
- Conteúdo e operações já guardados no dispositivo continuam sob o controle
  offline do consumidor. A integração não reaplica uma mutação recusada como
  efeito do novo login.

A publicação da D-01 libera o adaptador real da BL-0019 já autorizada.
O aceite de integração do Jaci e os fluxos da BL-0010 continuam a ser
acompanhados nesta release.

## Política comum de senha e sessão

- Tupã permanece fonte de identidade, senha, reset e revogação; não implementar
  hash local, comparar senha com dados locais ou criar token de recuperação Jaci.
- Formulários respeitam mínimo 8 caracteres, máximo 128 e teto de 72 bytes UTF-8
  do contrato Tupã, além da confirmação local. Validação definitiva é do provedor.
- Sucesso em recuperação/troca leva ao login, sem login automático. Logout por
  senha/expiração tem motivo próprio e não usa o caminho que limpa a fila offline.
- HTML protegido sem sessão redireciona ao login com return_to local validado;
  HTMX/API responde 401 com código de sessão, sem HTML de login recebido como 200.
  503 não vira 401. Mutação vencida é recusada antes do serviço e não é reenviada
  automaticamente depois do login. A fila persistida usa seu fluxo próprio.
- Destino de retorno só aceita path/query relativos de páginas permitidas,
  sem host, //, controles, backslash, fragmento, rotas técnicas/auth ou destino de
  mutação. GET/POST do login validam novamente; fallback /. Nunca armazenar body
  de formulário/senha para replay.
- AUTH_MOCK continua bypass local de usuário existente ativo, APP_ENV=test,
  banco/arquivo de ambiente escolhidos pelo usuário. Recuperação/troca reais
  ficam indisponíveis no mock (501 claro), sem sair para Tupã. Testes de contrato
  reais usam cliente injetado/stub, não alteram esse significado do mock.
- Guards locais e mutações devem manter validação de vínculo ao grupo; a sessão
  autentica a pessoa e não concede autorização a IDs do cliente.

## Ordem da versão e integração

1. Registrar/aprovar a dependência D-01 no Tupã antes de afirmar seus contratos;
   preparar testes Jaci com respostas sintéticas só após aprovação dos refinamentos.
2. BL-0019: persistência, guard e refresh concorrente; integrar HTTP/WS/cache/fila.
3. BL-0010: recuperação pública, troca no perfil e terminação global usando os
   contratos já conferidos, com encaixe no guard da BL-0019.
4. Validar integração das duas tasks, regressão, UI mobile/PWA e gate externo.

A implementação futura deve partir da base consolidada do novo roadmap. A
release/v1.5.0 existente ainda está em 1cedb61 e contém só o escopo anterior;
ela e develop não receberam 9d6a18c nem este refinamento. Não desenvolver da
base antiga sem reconciliar os documentos e o piso de 60%, mediante autorização.

Branches previstas: feature/BL-0019-sessao-autenticada-oito-horas-inatividade e
feature/BL-0010-reset-senha-login-area-logada; atualizar com a base consolidada
antes do código. Subtarefas opcionais -01/-02/-03 derivam e retornam só ao pai;
a worktree permanece no pai até liberação. Tasks retornam a release/v1.5.0
somente com liberação do usuário, depois dos checks aplicáveis. Sem novas worktrees.

Esta branch documental deriva de uma branch com histórico de código abortado
(e piso independente). Não aplicar merge documental automático: o Git Flow do
projeto e a instrução do usuário reservam a integração explícita. O pacote está
versionado para revisão na branch documental; não misturar código abortado em
merge de refinamento, nem retomar backup por associação ao nome da release.

## Validação futura e publicação

Nenhum código, migration, teste executável, asset, ambiente ou repositório externo
é alterado neste refinamento. Os comandos abaixo são futuros e precisam de
liberação de execução; a restrição anterior de não executar testes não foi revogada
por este pedido de triagem/refinamento.

- Focais por fatia: unitários/integração de sessão, senha, mock, PWA, isolamento e
  fila Node; relógio congelado, cliente Tupã stubado e recursos descartáveis.
- Migração aditiva em SQLite e PostgreSQL descartáveis; concorrência real com
  dois workers/duas abas deve usar PostgreSQL, não só SQLite/memória.
- Regressão final quando liberada: bash scripts/run_tests.sh --coverage, piso 60%;
  a execução histórica de 60,04% não comprova os novos fluxos.
- UI quando liberada: ENV_FILE=.env.test bash scripts/run_ui_tests.sh, pelos
  runners isolados e com extensão de Page Objects/fixtures via vgx-ui-tests.
- AUTH_MOCK mantém significado atual. O contrato de senha/sessão real usa provedor
  sintético independente, com reset/validade determinísticos; nenhuma credencial
  real ou serviço remoto sem autorização.
- Aceite: login, requisições antes/depois de 8h, automatic requests, WS sem renovar,
  reset, troca, duas abas/dispositivos, 503, replay/CSRF, isolamento e fila retida.
- Publicação exige evidência de D-01 e de URL pública/e-mail do Jaci no Tupã,
  regressão/UI aprovadas, atualização PWA e aceite manual registrado. Código
  implementado não é concluido até publicar. Não há dependência de backup age/SFTP.

## Progresso

| Escopo | Implementado | Restante | Estado |
| --- | --- | --- | --- |
| BL-0019 | 6/6 fatias | Aceite manual/publicação | Em validação; integração real e automática aprovadas |
| BL-0010 | 0/6 fatias | 6 | Refinamento pronto; aprovação de implementação pendente |
| Release | 0/2 tasks concluídas | 2 | Publicação do provedor confirmada; integração Jaci em andamento |

## Fechamento desta etapa documental

Triagem BL-0019 e refinamentos 1.5.0 versionados nesta branch. Validação apenas
de coerência entre item/índice, links locais, datas e diff. Sem teste, migração,
login remoto, confirmação de duração em produção ou alteração do Tupã/Potira.
A aprovação do refinamento versionado é o próximo gate, mantendo D-01 explícita.

Referências técnicas consultadas: [sessões OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
e [recuperação de senha OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html).
As decisões de atividade e oito horas são do usuário, não desses guias.


## Atualização da dependência externa — 2026-11-11

Publicação Tupã 1.1.0 confirmada pelo usuário. A instância de testes na porta
8005 respondeu ao health e ao OpenAPI. A consulta autenticada pelo produto
recusou o token sintético inválido com `200 {"active":false}` e
`Cache-Control: no-store`. A evidência é de consulta, sem alteração de contas.


A integração da BL-0019 foi validada com a instância informada, com
regressão, Playwright e PostgreSQL descartáveis. O provedor foi publicado e
a BL-0019 está em validação. A BL-0010 conserva seu gate próprio.
