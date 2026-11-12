# Refinamento — BL-0019 — Sessão por oito horas de inatividade — 1.5.0

## Rastreabilidade

- Backlog: [BL-0019](../backlog/items/BL-0019-sessao-autenticada-oito-horas-inatividade.md).
- Coordenação: [versão 1.5.0](release-1.5.0-acesso-conta-sessao.md).
- Estado: concluido; aceite manual aprovado e publicação da 1.5.0 confirmada em 2026-11-11.
- Responsável: Engenharia Jaci. Triagem e refinamento em 2026-11-10.
- Branch documental: docs/refinamento-1.5.0, base 9d6a18c, mesma worktree.
- Branch de implementação: feature/BL-0019-sessao-autenticada-oito-horas-inatividade,
  derivada/atualizada com a base consolidada da release, mediante liberação.

## Objetivo e critérios de sucesso

Manter a sessão por oito horas desde a última requisição autenticada ao servidor,
sem confundir expiração do access token com expiração por inatividade. O servidor
é a autoridade do relógio e da revogação. Critérios observáveis:

1. Deadline = last_activity_at UTC + 28.800 segundos. now < deadline autoriza;
   now >= deadline recusa antes de tocar atividade, renovar token ou executar ação.
2. Cada requisição HTTP que chega com sessão válida atualiza last_activity_at e
   o prazo do cookie, inclusive HTMX, APIs, consultas e sincronização automáticas.
   Considerar o tempo do servidor depois de adquirir a trava, sem throttle de 1min.
3. Pings/pongs WS não contam. Frames, broadcast e o simples socket aberto não
   atualizam last_activity_at. O handshake HTTP autenticado, inclusive uma nova
   conexão, e requests HTTP de fragmentos contam como as demais requisições.
4. Cache do navegador/Service Worker sem chegada ao servidor, digitação/rolagem,
   foco e passagem do tempo offline não renovam. Não introduzir timer/heartbeat.
5. Token Tupã válido não é reemitido por request; access vencido só usa refresh
   se sessão local ainda válida. O prazo local é rechecado depois da chamada lenta.
6. Logout, revogação, senha alterada, usuário local inativo ou token inválido
   impedem autorização; próxima requisição já não pode renovar sessão morta.
   Exigência global de revogação depende de D-01 da coordenação, ainda inexistente.
7. Reinício e múltiplos workers compartilham o estado persistente; duas abas
   não podem consumir simultaneamente o mesmo refresh rotativo.
8. Vencimento bloqueia envio ao servidor sem apagar fila/histórico local. Após
   login da mesma pessoa, revalidar autorização por grupo antes de retomar a fila.

## Diagnóstico e classificação da triagem

Evidência estática: app/main.py:add_unread_count renova a partir de jaci_refresh
sem last_activity; set_auth_cookies usa expires_in e refresh cookie de 30 dias.
Dependências HTTP validam JWT, mas não consultam sessão revogável; WS autentica
na abertura por query de JWT. O Tupã em 4cee88f tem access de 15min/refresh de 7d
por padrão, refresh rotativo, sem introspecção de revogação de access. Estes são
valores do código; não houve medição da produção ou leitura de .env privado.

Confirmação: confirmado como lacuna contratual, melhoria N/A de severidade e P1
pela sequência de acesso da release. Não afirmar que existe bug de logout em
15min comprovado: o refresh pode manter login e o ambiente real não foi medido.
Não duplica BL-0010: aquela entrega recuperação/troca; esta controla continuidade,
concorrência e revogação da sessão que os dois fluxos usam.

## Decisões e escopo

O usuário determinou cada request como atividade, esclareceu que ping WS não
conta e aprovou novo login de todos os dispositivos após troca/reset. A política
passiva usa a referência Potira (f17047c7), com cookie opaco, estado persistido,
refresh sob lock e decisão no request. Não copiar filtro por interação humana,
limite idle de 1h, limite absoluto de 12h, overlay, timer ou novo ping.

Incluído: login/cadastro/novo acesso, guarda de sessão por dispositivo, cookie,
HTTP/HTMX/API, handshake e tráfego WS, refresh, logout e retomada da fila. Incluir
compatibilidade AUTH_MOCK e ajuste da informação de sessão na privacidade.
Excluído: criptografia de backup, cópia externa, UI de gerenciar dispositivos,
SSO genérico, alterações de regra de compras e um prazo absoluto adicional que
encerre sessão ativa sem aprovação. O refresh continua sujeito à política real
do provedor; rejeição/expiração definitiva exige novo login, sem forjar validade.

## Contrato técnico proposto

### Estado persistido e credenciais

Adicionar sessão local com ID aleatório de 256 bits; cookie httpOnly contém só
referência opaca, com hash do ID na tabela. Não aceitar user_id/JWT bruto como
substituto de registro válido. Modelo proposto app/models/access_session.py:

- id_hash, user_id local, tupa_subject/product_id, auth_provider (tupa ou mock).
- authenticated_at, last_activity_at, expires_at UTC, revoked_at/reason.
- access_expires_at, par access/refresh protegido no servidor, versão de linha.
- Índices de usuário/expiração e constraints last_activity >= authenticated_at,
  expires_at > last_activity. Tombstones preservam invalidação; limpeza técnica
  de registros expirados/revogados após 30 dias, sem tocar compras ou registros
  ativos. Timestamps futuros/incoerentes são recusados.

Migração aditiva e SQLAlchemy na base já existente, sem Redis obrigatório.
Persistência de tokens usa biblioteca padrão de mercado, proposta Fernet via
cryptography como dependência direta, chave exclusiva SESSION_TOKEN_ENCRYPTION_KEY
estável/igual entre workers e fora do repositório. Isso protege credenciais de
sessão no servidor; não reativa criptografia de backups abortada. Apenas exemplo
de configuração no código futuro; operador prepara a chave em ativação explícita,
sem gerar segredo ou editar .env.test/.env.production automaticamente.

Sem fallback de chave derivada em produção. AUTH_MOCK usa provedor marcado e
chave sintética só no runtime descartável dos testes; o uso exploratório continua
aceitando arquivo/banco existentes do usuário. Não sobrescrever banco ou ambiente
para tornar a sessão mock compatível. Sessão mock não vira real ao mudar a flag.

Cookie jaci_session opaco, Secure em produção, httpOnly, SameSite=Lax, Path=/,
Max-Age limitado ao deadline remanescente. jaci_refresh legado é eliminado na
transição; JWT/refresh não vão para JS, query de socket, IndexedDB ou localStorage.
CSRF da sessão deriva de segredo/contexto no servidor e é validado em POSTs
autenticados; login/cadastro usam contexto CSRF anônimo separado, sem aceitar
sessão prévia forjada. Mesma origem não substitui a validação do segredo.
Cookies antigos exigem um novo login depois da implantação do guard; não migrar
JWT arbitrário para sessão local já renovada. Dados/fila offline permanecem.

### Autorização e atividade em HTTP

Um contexto por request é carregado antes de qualquer dependência/rota ler dados.
Validar registro, relógio, usuário ativo, identidade/product/type/issuer do token,
D-01 e vínculo local. Atualizar atividade só após autenticação bem-sucedida e antes
de liberar a ação. Requests rejeitados por autorização de recurso, como grupo
estrangeiro, não concedem esse recurso; a autenticação válida ainda pode contar.

Não excluir automaticamente requests de static, health ou background se eles
realmente chegam com a sessão e atravessam esse contexto: a regra aprovada é
cada request autenticado. Healthchecks sem cookie, callbacks de serviço e requests
anônimos não pertencem à sessão. Respostas públicas não ganham dados autenticados
por cookie inválido. Rotas de reset/login continuam utilizáveis se a sessão velha
estiver expirada; seu contexto anônimo é independente. Logout/troca/reset são
terminais e não reemitem cookie depois da invalidação.

Roteiros HTML expirados usam 303 ao login; API/HTMX usa 401 estruturado
(session_expired/session_revoked). Header HTMX pode orientar login em interação,
mas polling falho não navega toda a aplicação repetidamente. Não retornar HTML
login como sucesso a um POST JSON. Após login, return_to só navega para página GET
interna validada; não guarda/reenvia corpo de mutação.

### Concorrência, refresh e revogação

SELECT FOR UPDATE na sessão durante leitura, validade, refresh, persistência do
par rotacionado, toque e revogação; liberar antes dos serviços de compra. Relógio
medido após obter lock e depois de roundtrip. Não usar mutex por worker como
única trava. Não reaproveitar pair do browser; par novo fica no mesmo registro,
permitindo que a segunda aba use o resultado sem um segundo refresh.

Fluxo: verificar idle -> validar JWT/par -> refresh só se access venceu ->
verificar D-01 -> revalidar idle -> tocar agora -> commit -> autorizar domínio.
Falha de refresh 401/token inválido revoga localmente; timeout/5xx de provedor
recusa com 503 sem apagar fila, fingir logout ou ampliar last_activity. Retry
posterior continua limitado pelo prazo original. Se o refresh remoto tiver sido
consumido e a persistência falhar, exigir novo login; não manter segredo em cache
ou tentar reutilizar token como se não tivesse rotacionado.

Logout por ação do usuário confirma revogação local antes de limpar cookies e
tenta propagação ao Tupã, sem ressuscitar a sessão se remoto falhar. Encerramento
global por senha depende da transação do Tupã D-01 e do guard em todos os nós.
Resposta atrasada só reemite cookie se a sessão ainda está ativa na hora de
gravação; conferir logout concorrente e a flag terminal do response. Não criar
sessão nova por refresh, request antigo ou cookie forjado.

### WebSocket

Trocar JWT na query por identificação via cookie opaco de sessão no handshake,
verificando Origin e vínculo ao grupo/execução. Consultar estado antes de aceitar,
de tratar frame protegido ou de enviar novo conteúdo privado a um socket. Ping
pode checar validade/fechar canal, mas nunca tocar atividade ou renovar por si só.
Se precisar refresh sem nova requisição HTTP, fechar para reconectar pelo fluxo
HTTP autenticado, sem emitir credencial no socket. Não introduzir abertura/reconexão
artificial para manter a janela viva. Se ocorrer handshake HTTP
autenticado, ele conta como request; ping/pong e frames nunca tocam o relógio.
Sem heartbeat novo para auth.

Canal vencido/revogado fecha 4001 sem laço infinito de reconexão; erro de permissão
fecha 4003. Broadcast verifica sessão do destinatário antes de expor conteúdo.
Uma tela pode permanecer visível com dados já carregados sem requests: a política
passiva não promete apagar conteúdo remoto offline. Persistência/sync continuam HTTP.

### Offline, senha e troca de conta

401/expiração/retorno do reset não invoca clearLocalCache de /auth/logout. Preservar
pending_operations, versões e conflitos, mas suspender envio até novo login válido.
Vincular cache/fila a usuário/provedor/produto; depois do login da mesma identidade,
revalidar cada grupo e status da execução na API. Login de outra conta não pode ler
ou enviar pendências anteriores: manter a partição anterior inacessível e permitir
retorno à conta original, sem apagá-la automaticamente. Tratar caches legados sem
proprietário verificável como quarentena local; não atribuir à conta que entrar.
Logout explícito atual não deve perder operações pendentes silenciosamente;
refinar sua confirmação/guarda usando a mesma partição, mantendo simplicidade.
Não incluir senhas/tokens nem relógio autoritativo no snapshot/fila.

## Riscos e regras preservadas

| Dimensão | Risco e controle |
| --- | --- |
| Segurança | Alto: sessão fixada, token errado, refresh duplicado ou revogação ignorada; ID opaco, CSRF/Origin nas mutações, lock, validação product/type/issuer e D-01 |
| LGPD | Médio: metadados de acesso e dados offline; mínimo necessário, nenhuma credencial em log/cache/JS, retenção técnica delimitada |
| Grupo | Alto: autenticar pessoa não valida grupo; manter autorização de cada recurso e partição local por identidade |
| Offline/sync | Alto: expiração não perde fila nem aplica como outra pessoa; 401 e 503 diferenciados, sem reenviar comandos arbitrários |
| Histórico financeiro | Preservar valores, versões, snapshots e conflitos; sessão não reescreve compra |
| Recorrência | Não recalcular datas/status ao renovar ou relogar |
| Template/execução | Não modificar template ou execução como efeito colateral de autenticação |

## Plano de implementação — duas etapas, seis fatias

Todos os testes listados são contratos futuros, criados somente após aprovação.

### Etapa 1 / Ticket 1 — Guard persistido e continuidade HTTP

| Fatia | Resultado e arquivos esperados | Validação focal futura |
| --- | --- | --- |
| 1.1 | Contratos e política de 28.800s; app/services/access_session_service.py, app/models/access_session.py, app/models/__init__.py, migration aditiva, app/config.py, .env.example, requirements.txt; testes/test_session_policy.py e tests/test_session_auth_flow.py | Limite exato, UTC/SQLite, cookie forjado, constraints, usuário inativo, migração PostgreSQL descartável |
| 1.2 | Repositório/trava e tokens protegidos; app/repositories/access_session_repository.py, adaptador Tupã e AUTH_MOCK; exigir D-01 antes de implementar integração real | Duas conexões PostgreSQL/workers, refresh único, falha de commit, rotação, 503 e relógio após lock |
| 1.3 | Aplicar contexto a login/cadastro, middleware, dependências, cookies e logout; app/main.py, app/dependencies.py, app/utils/security.py, app/routers/auth.py | Request frequente sem throttle, automatic requests contam, vencido não toca/renova/muta, cookies antigos recusados e logout sem reemissão |

### Etapa 2 / Ticket 2 — Canais, fila e aceite

| Fatia | Resultado e arquivos esperados | Validação focal futura |
| --- | --- | --- |
| 2.1 | WS por cookie com guard, remover JWT de query/log; app/websocket/handlers.py, manager.py, static/js/execution-sync.js, templates de execução | Ping não toca, WS sozinho não mantém, término fecha sem loop, nenhuma mensagem privada para revogado |
| 2.2 | Fila/cache particionados e tratamento de sessão; static/js/offline-cache.js, service-worker.js, login/auth_verify, sync-status/central e testes JS/pytest | Mesmo usuário retoma; outro não lê/aplica; 401/503 e expiração por senha preservam fila; requests automáticos válidos contam |
| 2.3 | UI passiva e evidência da política; tests/ui de autenticação e compras com Page Objects/fixtures, tests/README.md, docs/domain/user-flows.md, README e privacidade | Mobile/desktop, recarga/abas/restart, retorno seguro sem replay e regressão integrada |

Cada fatia atualiza histórico/progresso e commita no pai ou filho -nn. Fluxos
comuns de senha são cobertos por BL-0010 depois do guard. Não copiar o banco,
framework ou a política de prazo absoluto do Potira para resolver concorrência.

## Cenários TDD do escopo

1. t=7h59m59s autoriza e passa deadline oito horas adiante; t=8h exatas não autoriza.
2. Request no segundo seguinte toca de novo; não reduzir atividade a janelas de 1min.
3. Polling, snapshot, sync e fragmento HTTP autenticados contam. Ping/pong WS,
   socket parado, request anônimo, cache sem rede e tempo offline não contam.
   Handshake HTTP autenticado conta, sem transformar cada frame em novo request.
4. JWT válido/sem necessidade não chama refresh; vencido/local válida rotaciona.
5. Local vencida impede refresh até com token provider ainda válido; chamada
   lenta cruzando deadline não renova nem executa mutação.
6. Cookie antigo/JWT bruto/ID arbitrário/provider mock em modo real é recusado.
7. Revogação/senha/logout em outra aba impede próxima autorização com D-01,
   mesmo que JWT não tenha expirado. Resposta atrasada não recoloca cookie ativo.
8. Dois workers fazem no máximo um refresh; o segundo lê o novo par; rollback
   ou refresh consumido sem commit não causa overwrite ou sessão zumbi.
9. Assinatura/issuer/type/product/sub inválidos, usuário inativo e grupo estrangeiro
   nunca dão acesso; erro remoto temporário responde 503 e não toca prazo.
10. WS não recebe privado após deadline/revogação; ping e reconexão não renovam.
11. Fila continua após 401/senha; mesma pessoa retoma com autorização; outra conta
    não enxerga/aplica; nenhuma senha/token vai para IndexedDB/Cache API/log.
12. Navegação HTML expirada mantém retorno interno; HTMX/API não recebe login 200;
    POST recusado não é executado nem repetido após autenticação.
13. Sem JS, navegação/formulário mantêm sessão por requests; não há overlay ou
    timer de bloqueio. Com rede ausente, tela/cache não são apagados pelo relógio.
14. Reinício/múltiplas abas conservam timestamps e origem; TTL do cookie é
    deadline real, não a validade de 15min do access nem os 30dias do cookie legado.

## Estratégia de validação e publicação

Quando houver autorização de execução: focais Python por fatia, Node da fila,
HTTP/WS, migração SQLite e PostgreSQL descartáveis e corrida real entre dois
workers. Relógio congelado no backend; não esperar oito horas em teste. Lint dos
Python alterados; graphify AST depois de código. UI pelos runners isolados e
vgx-ui-tests; requer provedor stubado, sem tornar AUTH_MOCK um falso Tupã de senha.

Final: bash scripts/run_tests.sh --coverage com piso 60%; UI e aceite da matriz
com BL-0010; migrations e evidência D-01. Sem ambientes do usuário, infra Oracle,
banco real, tokens reais, reinício ou deploy implícitos. Política de privacidade
corrige descrição de cookies/localStorage para refletir o estado realmente entregue.
Sessão persistida exige implantação coordenada dos workers e novo login de cookies
legados; rollback deve manter guard ou drenar área protegida, sem aceitar de novo
cookies revogados. Documentar antes de publicar; não executar esse procedimento agora.

## Progresso e fechamento documental

| Etapa/ticket | Fatias implementadas | Restantes | Estado |
| --- | --- | --- | --- |
| 1 — Guard/HTTP | 3/3 | 0 | Concluído; aceite e publicação registrados |
| 2 — WS/fila/aceite | 3/3 | 0 | Concluído; aceite e publicação registrados |
| Total | 6/6 | 0 | Concluído; aceite e publicação registrados |

Triagem concluída e refinamento versionado em docs/refinamento-1.5.0.
D-01 não foi registrada/implementada no Tupã; seu ID real/publicação devem ser
associados antes da integração. Aprovação deste documento não autoriza merge,
edição de ambiente, trabalho externo ou execução de testes previamente restringida.


## Implementação autorizada — 2026-11-10

Usuário pediu criar/usar a release e implementar BL-0019. release/v1.5.0 existente
foi avançada por fast-forward até 75ac29e e a branch pai BL-0019 atualizada com ela,
na mesma worktree. develop/main e remoto não foram alterados. Mantida restrição
anterior de não executar testes. Contratos do escopo escritos antes do código.

D-01 continua inexistente no Tupã 4cee88f; implementação local usa seam de provedor
injetável e permanece opt-in (SESSION_GUARD_ENABLED=false por padrão). O adaptador
real não chama uma API imaginária e recusa ativação enquanto o contrato não existir.
Isso permite concluir/revisar componentes locais sem bloquear o ambiente atual ou
fingir revogação global em produção. Chave e migração são preparadas somente pelo
operador; nenhum arquivo de ambiente do usuário será editado. Integração real D-01
e suas evidências não são declaradas implementadas por essa entrega local.

Fatia 1.1 implementada: política/retorno seguro, modelo e migração aditiva,
repositório com lock e contratos do escopo. Conferência AST/diff somente; nenhuma
migração ou teste foi executado. cryptography fixada à versão 47.0.0 já presente
no ambiente, sem instalação de pacote. Integração D-01 permanece pendente.

Fatia 1.2 local implementada: serviço de sessão e provedor mock/injetável,
Fernet, validação temporal antes/depois de refresh, trava de linha, revogação
local e limpeza técnica. O adaptador Tupã permanece fechado e sem requisição
a endpoint não confirmado: a integração real D-01 não foi implementada. Não
confundir componente local entregue com essa dependência resolvida. Sem testes.


### Fatias 1.3 e 2.1–2.3 — Implementação local

- Middleware valida a sessão antes das rotas. O login emite cookie opaco, as
  mutações exigem CSRF e a saída confirmada revoga a sessão local. APIs e HTMX
  recebem 401 estruturado. A navegação permite retornar por GET a uma página
  interna após o login.
- WebSocket usa cookie, Origin e vínculo à execução na abertura. Pings e
  entregas privadas verificam sessão e grupo sem renovar prazo ou token.
- IndexedDB separa filas e snapshots por conta. O service worker guarda páginas
  visitadas por conta com os campos CSRF removidos. Na reconexão, a consulta de
  snapshot recupera o CSRF da sessão vigente antes do envio. A API verifica a
  identidade da fila, inclusive em requisições iniciadas em outra aba.
- Playwright cobre fila offline, expiração, troca de conta e retomada. O runner
  habilita a sessão persistida somente com opt-in no ambiente sintético.
- A limpeza técnica após 30 dias está disponível em
  `python -m scripts.prune_access_sessions`. A execução cabe ao operador no
  ambiente selecionado. O comando e a migração ainda não foram executados.
- D-01 permanece pendente. A revogação após alteração ou recuperação de senha
  exige a integração com o Tupã e os fluxos da BL-0010.

Conferências estáticas registradas na branch da demanda. Aceite executável,
corrida em PostgreSQL e publicação permanecem pendentes.


## Provedor publicado — 2026-11-11

O Tupã 1.1.0 foi publicado e a instância de testes foi disponibilizada na
porta 8005. A consulta autenticada com token sintético confirmou o contrato
de validade. A integração real da fatia 1.2 passa a usar esse contrato.
As referências anteriores à ausência de D-01 descrevem a situação de
2026-11-10. O trabalho segue na branch pai da BL-0019.


## Integração real e evidências — 2026-11-11

- Adaptador `TupaSessionProvider` usa o contrato publicado, com credencial
  de serviço na consulta e Bearer na saída. A consulta autenticada prova
  assinatura e revogação do token. A identidade, tipo, issuer e expiração
  locais devem coincidir com o resultado. Falha na credencial de produto
  ou no provedor preserva a distinção de indisponibilidade.
- Access vencido durante uma consulta pode fazer um único refresh, se a
  sessão local continuar válida. Esse caminho mantém a rechecagem de idle
  e a regra de não renovar pelo WebSocket.
- `./scripts/run_tests.sh --coverage -q`: 351 aprovados, dois xfails
  documentados, 63,27% de cobertura. As correções dos testes existentes
  completaram o scope ASGI sintético e atualizaram a versão esperada do cache.
- Três testes focais WebSocket aprovados, incluindo handshake por cookie,
  ping sem toque, recusa de origem e fechamento depois da revogação.
- Playwright: um cenário aprovado em 8,62 segundos, cobrindo operação
  offline, recarga, expiração, troca de conta e retomada da pendência.
  Servidor e banco foram descartáveis, com arquivo de origem temporário
  fornecido ao runner. Artefatos em
  `reports/playwright/96e8539054fc4759abe19e6ae18bba82`.
- Tupã de testes na porta 8005: login, refresh, revogação de duas sessões
  e novo login com a mesma identidade de fila aprovados. Foi usada uma
  conta sintética exclusiva, removida ao final, e banco Jaci em memória.
- PostgreSQL 15 descartável: cadeia de migrações aplicada até
  `20261110_0006`; duas conexões concorrentes executaram um único refresh
  e persistiram a versão três da sessão após dois requests.
- O bloqueio do TestClient observado dentro do sandbox foi resolvido
  executando o runner isolado fora dessa restrição. O runtime do usuário
  foi preservado.

Ativação operacional exige `SESSION_GUARD_ENABLED=true`, chave privada de
sessão e credenciais do produto configuradas pelo operador. A demanda está
em `em_validacao`, com aceite manual e publicação do Jaci pendentes.

## Correção de primeiro acesso — 2026-11-11

O usuário encontrou aviso de sessão encerrada ao abrir a raiz em navegador
sem cookies. O middleware identificava a ausência de autenticação como
expiração e incluía `expired=1` em todo redirecionamento ao login.

A correção da mesma BL-0019 usa `authentication_required` para acesso
anônimo. A mensagem de expiração fica vinculada à sessão recusada ou à
identificação persistida de uma conta anteriormente autenticada. Cookies
de formulário anônimo não indicam sessão anterior. O retorno interno ao
destino protegido e as respostas 401 de API continuam cobertos.

Validação da correção: 19 testes HTTP/política/sessão aprovados e dois
cenários Playwright aprovados. O cenário de primeiro acesso cobre navegador
sem cookies e formulário anônimo prévio. Sessão recusada e identificação
persistida continuam exibindo a expiração. Artefatos de navegador em
`reports/playwright/bb7e52fae25b404c9ea376686c3e5476`.


## Aceite manual aprovado — 2026-11-11

O usuário confirmou a validação manual e aprovou o resultado da BL-0019,
autorizando em seguida a implementação da BL-0010 na mesma worktree.
O progresso acima reflete esse aceite. Permanecem liberação de integração e
publicação do Jaci 1.5.0; a demanda segue em_validacao até o registro da publicação.


## Publicação confirmada — 2026-11-11

Usuário confirmou a publicação do Jaci 1.5.0. Aceite manual e validações da
implementação já aprovados; demanda passa de em_validacao para concluido.
Registro baseado no relato de publicação, sem executar novo deploy, migração,
consulta à produção ou teste. Nenhuma configuração real foi alterada.

Referências locais conferidas: main 903cb1b, develop 4315e76 e tag v1.5.0 em
d959aff. A preparação 98ece73 está na main/develop, mas não está na tag atual.
O commit efetivamente implantado não foi informado; não atribuir o relato do
deploy ao hash da tag por inferência. Preservar a tag, sem movê-la ou recriá-la.
A divergência de rastreabilidade fica registrada no roteiro da release.
