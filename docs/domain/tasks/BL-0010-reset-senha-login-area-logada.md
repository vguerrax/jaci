# Refinamento — BL-0010 — Recuperação e troca de senha — 1.5.0

## Rastreabilidade

- Backlog: [BL-0010](../backlog/items/BL-0010-reset-senha-login-area-logada.md).
- Coordenação: [1.5.0 — acesso e sessão](release-1.5.0-acesso-conta-sessao.md).
- Relacionada: [BL-0019](BL-0019-sessao-autenticada-oito-horas-inatividade.md).
- Estado: concluido; aceite manual aprovado e publicação da 1.5.0 confirmada em 2026-11-11.
- Responsável: Engenharia Jaci, 2026-11-10.
- Branch documental docs/refinamento-1.5.0, base 9d6a18c, mesma worktree.
- Branch pai feature/BL-0010-reset-senha-login-area-logada, avançada para
  bfd31dc antes do código. Sem branches filhas ou novas worktrees.

## Objetivo e critérios de sucesso

Oferecer “Esqueci minha senha” no login e troca de senha no perfil. Tupã gerencia
credenciais e notifica por e-mail. Jaci apresenta formulários, encaminha contratos
e preserva compras, grupos e fila. Critérios:

1. Solicitação pública dá a mesma confirmação para conta existente/inexistente,
   sem apresentar token ou indicar cadastro. Não criar usuário por recuperação.
2. Link oficial GET /reset-password?token=... funciona com a base_url do produto
   Jaci cadastrada no Tupã; token é opaco, temporário e de uso único no provedor.
3. Confirmar nova senha e repetição antes do envio. Senha inválida, token expirado,
   usado, ausente, incorreto ou estrangeiro não altera credencial nem autentica.
4. Perfil solicita senha atual, nova e confirmação; identidade vem da sessão,
   nunca de e-mail/user_id enviados pelo cliente. Senha atual errada é explícita.
5. Sucesso de reset/troca exige novo login em todos os dispositivos, como aprovado
   pelo usuário; D-01 do Tupã e guard da BL-0019 precisam estar validados.
6. Credenciais/token não entram em log, analytics, cache offline, banco Jaci,
   fila, URL de redirecionamento ou resposta de erro. A query de chegada do link
   requer redaction de logs de aplicação/proxy conforme ativação explícita.
7. Indisponibilidade retorna erro recuperável, sem falso sucesso, vazamento de
   detalhe remoto ou repetição automática de operação sensível de resultado incerto.
8. Reset/troca/expiração não apagam operações pendentes; reautenticar a mesma
   pessoa permite retomar pela API com grupo/versão revalidados.

## Evidência atual e contratos existentes

Jaci inspecionado em 9d6a18c: login sem link de recuperação; perfil só orienta
canal externo. POST /auth/profile/password valida mínimo legado de seis caracteres
e termina em 501; não chama Tupã. O cliente não tem forgot/reset/change wrappers.

Tupã local develop 4cee88f55b487c89b4531115c13bd22a2cfad17e, somente leitura:

| Contrato existente | Entrada | Resultado/limite observado |
| --- | --- | --- |
| POST /auth/forgot-password | product_id do Jaci e email normalizado | 200 genérico; provedor envia e-mail se usuário existir |
| Link emitido | Product.base_url + /reset-password?token=opaco | Fallback global PRODUCT_BASE_URL ainda existe e deve ser evitado por configuração correta do produto |
| POST /auth/reset-password | token, new_password | Token hash no Tupã; prazo de uma hora, uso único, refresh revogado; access existente ainda não é revogado |
| POST /auth/change-password | Bearer do usuário; current_password/new_password | 200 em sucesso; 401 senha atual incorreta; refresh/access existentes não são invalidados por esta função |
| Validação de senha | 8..128 caracteres e no máximo 72 bytes UTF-8 | Contrato de schemas/auth.py; a validação final e hash pertencem ao Tupã |

Não usar PUT administrativo /auth/users/{user_id}/password para contornar senha
atual no fluxo de perfil. Não chamar o provedor com token de serviço no lugar de
identidade da pessoa para mudar senha autenticada. A configuração real de e-mail
e base_url não foi consultada ou alterada.

## Escopo e fluxos

### Solicitação pública

- GET /auth/forgot-password renderiza formulário mobile com e-mail e retorno ao
  login; POST da mesma rota encaminha product_id fixado no backend, nunca do HTML.
- Validar sintaxe, normalizar e-mail e aplicar limite de abuso consistente entre
  workers: proposta inicial 5 solicitações por e-mail/produto e 20 por origem em
  15min; limites finais configuráveis/documentados. Chave é hash com segredo;
  retenção técnica só da janela, sem salvar e-mail/IP em claro para esse controle.
- Rate limit no provedor/proxy compartilhado deve ser verificado. Caso ausente,
  implementar bucket atômico em PostgreSQL no Jaci; não usar dicionário por worker
  como única proteção. Nenhum novo Redis/serviço é obrigatório nesta versão.
- Mesma mensagem para conta inexistente/limitada por conta, sem diferenciar por
  texto/status. Limite global da origem pode retornar 429 genérico. Timeout/5xx
  da infraestrutura é 503 genérico igual para qualquer e-mail. Não expor o detalhe
  recebido do Tupã nem afirmar que o e-mail chegou sem evidência do provedor.
- Processamento não pode revelar conta por diferença determinística de retorno:
  validar com provedor sintético e tratar a emissão assíncrona/normalização de
  tempo no contrato externo, sem prometer tempo constante absoluto na rede.
- Não enfileirar token/senha para operação offline. AUTH_MOCK apresenta operação
  indisponível sem chamada remota ou alteração do usuário local.

### Entrada do link e formulário limpo

GET /reset-password é alias obrigatório da URL produzida pelo Tupã. Recebe token
opaco com tamanho máximo defensivo de 4096 caracteres, sem tentar decodificar JWT.
Apenas prepara contexto temporário seguro, sem consumir token ou alterar senha.
Mover token para cookie httpOnly, Secure em produção, SameSite=Lax, Path restrito
a /auth/reset-password e Max-Age até uma hora, com integridade/contexto do fluxo;
303 para GET /auth/reset-password sem query. Assinatura do contexto não substitui
a validação do token pelo Tupã. Não gravar token opaco em banco Jaci ou web storage.

GET limpo renderiza nova senha/confirmar e campo CSRF sem expor token em hidden,
HTML/JS, link ou mensagem. POST /auth/reset-password usa cookie/contexto somente
para chamada servidor-servidor. Sem token/contexto, mostrar link para pedir nova
recuperação. Ler o link por scanner de e-mail não o consome; só POST válido pode
solicitar alteração ao provedor.

Respostas da entrada e do formulário: Cache-Control: no-store, Referrer-Policy:
no-referrer; sem analytics ou requisições externas na página que recebe segredo.
Service Worker faz bypass de /reset-password e dos endpoints /auth/forgot-password,
/auth/reset-password e /auth/profile/password. Nunca guardar navegação com token
em Cache API. Remover só caches de rotas sensíveis legadas se encontrados, sem
apagar fila/IndexedDB. Revisar assets da página limpa para não carregar recursos
externos com referer de segredo; não criar dependência frontend nova.

Logs da aplicação precisam filtrar query/body das rotas sensíveis antes do access
log. Incluir teste de redaction com token sintético para uvicorn/httpx/logger.
No Caddy, ativação manual pelo operador confere que URI/query destas rotas não
são registradas. Não editar Caddy/ambiente por conta própria. O redirect posterior
não apaga um token que já tenha sido registrado pelo proxy; essa verificação é
critério de publicação do fluxo real.

### Confirmação de reset e troca no perfil

Nova senha: 8..128 caracteres e <=72 bytes UTF-8, confirmação idêntica; frontend
ajuda, backend valida. O valor não volta para template após erro. Token ausente,
expirado/usado/inválido responde mensagem única “Link inválido ou expirado”, com
ação de nova solicitação, sem ecoar token. GET não verifica senha/token no provedor.
Em sucesso limpar contexto de reset e cookies locais, revogar sessão local quando
houver e redirecionar ao login com mensagem. Não autenticar automaticamente.

Perfil troca a orientação antiga por formulário com senha atual/nova/confirmar,
CSRF e feedback acessível. POST /auth/profile/password exige sessão local válida,
Bearer ativo do usuário no servidor e mesma origem; user_id/email/product de
formulário são ignorados/recusados. Senha atual incorreta não termina uma sessão
válida e não é confundida com Bearer revogado; distinguir pelo contexto do contrato
remoto. Em timeout de resultado incerto não repetir automaticamente a senha.

D-01 deve fazer a alteração e revogação global na mesma transação. Após commit,
nenhuma outra aba/dispositivo pode autorizar a próxima ação mesmo com JWT não
vencido. O Jaci não pode resolver isso apenas apagando cookie da aba atual ou
chamando logout como segunda operação sujeita a falha depois da troca. A interface
não diz “sessões encerradas” antes de confirmação do contrato. Falha de e-mail
após commit não pode retornar 5xx que leve a repetir alteração já realizada.

Reset atual do Tupã não recebe product_id: token de outro produto não pode ser
aceito como fluxo Jaci. Incluir em D-01 vinculação do reset ao produto consumidor
por extensão compatível/autenticada do contrato. O produto vem da configuração
do backend; não confiar em campo do browser. A definição final será versionada
no Tupã antes do wrapper real. Não simular essa garantia apenas na UI.

## Segurança, offline e riscos obrigatórios

| Dimensão | Controle |
| --- | --- |
| Segurança | Alto: resposta genérica, isolamento de produto, CSRF/Origin nos POSTs, throttling compartilhado, token opaco fora de logs/cache, TLS e D-01 |
| LGPD | Médio: e-mail apenas para recuperação; sem senha/token em auditoria, usar código de resultado e correlação sem dados pessoais |
| Grupo | Identidade da sessão e produto fixado; não usar IDs cliente; não alterar vínculo/grupo como parte de reset |
| Offline/sincronização | Credenciais não enfileiram; indisponibilidade clara; 401/503 não limpam pendências; retorno exige mesma identidade e autorização |
| Histórico financeiro | Nenhum item/valor é modificado; não perder fila de compras ao mudar credencial |
| Recorrência | Nenhuma criação/reagendamento/recalculo de execução por senha |
| Template/execução | Não propagar observações/itens ou reescrever snapshots |

Novo login é consequência de senha e não passa pelo clearLocalCache de logout.
A partição por usuário/provedor da BL-0019 impede que outra conta herde a fila.
Depois da autenticação, encaminhar para página interna segura; não repetir POST
que iniciou antes da expiração. AUTH_MOCK é bypass local, não provedor de senha:
retorna 501 de forma clara; contratos HTTP/UI desta task usam injeção de cliente
Tupã sintético. Não exigir rede/contas reais para regressão.

## Dependências e limites

- BL-0019: guard de sessão, contexto de token servidor, CSRF, revogação e fila.
- D-01: revogação global atômica/introspecção, reset isolado por produto, resposta
  inequívoca quando notificação falha e contrato de abuso/enumeração conferido.
  Implementado e publicado no Tupã 1.1.0 (e30b639), com aprovação própria.
  Nenhum arquivo do Tupã é alterado nesta implementação do consumidor.
- Configuração de Product.base_url do Jaci e e-mail no Tupã, consultada/ativada
  pelo operador quando autorizado. Não remover fallback global de outros produtos.
- Hashes de senha, emissão/expiração de reset, entrega de e-mail e políticas de
  identidade permanecem no provedor. Não ampliar escopo para cadastro, mudança de
  e-mail, exclusão de conta, callbacks LGPD ou backup age/SFTP.

## Plano de implementação — duas etapas, seis fatias

Contratos futuros só serão criados após aprovação explícita deste refinamento.

### Etapa 1 / Ticket 1 — Contratos e recuperação pública

| Fatia | Resultado e arquivos esperados | Validação focal futura |
| --- | --- | --- |
| 1.1 | Wrappers/DTOs e política de entrada; app/services/tupa_auth_service.py, app/services/password_service.py, app/config.py se limite for configurável, tests/test_password_recovery.py | Payloads exatos, status/timeout/erros sanitizados, product_id fixo, 72 bytes, 501 mock, sem log; aguardar contrato D-01 final |
| 1.2 | Link no login e GET/POST forgot; app/routers/auth.py, templates/pages/login.html e forgot_password.html; limitador compartilhado/fixture | Conta existente/inexistente, enumeração, abuso em dois workers e erro de e-mail uniforme; nenhum usuário criado |
| 1.3 | Alias /reset-password e contexto cookie/redirect limpo; auth router, template reset, security/service-worker e redaction de logging | Scanner GET não consome, query removida, no-store/no-referrer, CSRF, sem token em HTML/cache/log |

### Etapa 2 / Ticket 2 — Senha nova, perfil e sessão

| Fatia | Resultado e arquivos esperados | Validação focal futura |
| --- | --- | --- |
| 2.1 | POST reset, política de senha/erros e retorno ao login; auth router, password_service, template | Token usado/expirado/ausente/estrangeiro, confirmação, sucesso sem auto-login, nenhuma senha refletida |
| 2.2 | Formulário de perfil e mudança autenticada, integração com guard BL-0019 e D-01 | Senha atual errada vs sessão inválida, duas abas/dispositivos, revogação atômica/refresh concorrente, fila preservada |
| 2.3 | Page Objects e cenários UI, docs de ativação/e-mail/URL/logs, README e fluxos de usuário | Mobile/desktop, rede ausente, abrir link do e-mail sintético, recuperar acesso com nova senha, antiga recusada, PWA atualizado |

Se limitação compartilhada precisar de tabela, migration é aditiva e só de
metadados técnicos; não alterar tabelas de compra nem armazenar token/senha.
Cada fatia atualiza progresso e commita no pai/filho -nn; nenhuma fatia vai direto
à develop/main. Task só integra à release com liberação do usuário.

## Cenários TDD

1. Login exibe recuperação e o perfil oferece formulário sem canais externos
   obrigatórios; ambos acessíveis no mobile e teclado com feedback claro.
2. E-mail conhecido/desconhecido recebem mesma resposta pública; normalização,
   product fixo, rate limit e erro remoto não revelam cadastro ou segredo.
3. Tupã envia link para o produto correto; alias sem token oferece nova tentativa;
   token nunca é decodificado como JWT ou registrado; GET/scanner não consome.
4. Cookie/contexto não é lido por JS; redirect limpa URL, SW não intercepta/reset
   não é servido do cache, headers de referrer/cache e redaction são efetivos.
5. CSRF ausente/forjado, Origin estrangeiro, token adulterado ou produto estrangeiro
   recusam antes da alteração. Validação final de vínculo ao produto é do Tupã.
6. Nova senha curta/longa/>72 bytes, confirmação divergente e token ausente/expirado/
   usado/incorreto não alteram credencial; senha não aparece no response/log.
7. Reset válido confirma uma vez e exige login; reuso falha. Corrida de reset
   consome uma vez no provedor e não cria sessão automaticamente.
8. Perfil sem usuário vai ao login; sessão de outra pessoa não permite escolher
   alvo por form; senha atual incorreta mostra erro sem revogar sessão válida.
9. Troca/reset invalida sessões de dois dispositivos na próxima autorização,
   incluindo access válido e refresh concorrente, sem janela parcial de commit.
10. Timeout/5xx e notificação falha são tratados pelo contrato, sem repetir operação
    sensível de resultado incerto nem limpar pendências ou prometer sucesso falso.
11. Fila prévia conserva payload/versão/conflito; mesma pessoa retoma, outra não;
    nenhum POST de compra capturado é reenviado como efeito do novo login.
12. AUTH_MOCK continua login de usuário local ativo sem validar senha, arquivo ou
    banco especial; forgot/reset/change são indisponíveis sem chamada remota.
13. Nova senha autentica com provedor sintético e a antiga falha; autorização de
    grupo e snapshots não mudam. Nenhuma alteração de ciclo recorrente/financeiro.

Os cenários acima foram transformados em contratos executáveis após aprovação.
Não há xfail desta demanda. Os dois xfail FL-08 da regressão são preexistentes,
referentes ao histórico de preços/análise de gastos e fora desta versão.

## Estratégia de validação

Depois da autorização de execução: focais unitários e HTTP de senha/CSRF/erro,
serviço Tupã injetado, fila Node e AUTH_MOCK; UI via vgx-ui-tests com Page Objects,
provedor/e-mail sintéticos isolados. Testar que o secret de reset não aparece em
traces/screenshots/artifacts. Nenhum e-mail real ou credencial do usuário.

Revisar logging/access logs em massa sintética, cabeçalhos e bypass SW; validar
fluxo sem JS na recuperação e troca, conforme melhoria progressiva. Correção PWA
não remove IndexedDB/pending_operations. Relógio congelado e consumo de token
são do stub; contrato real do Tupã precisa de evidência do próprio repositório.

Final quando liberado: bash scripts/run_tests.sh --coverage (piso 60%), UI pelo
runner isolado e aceite manual login/reset/perfil/sessão/pendência. Build/checks
adicionais apenas se houver mudança pertinente. Configurar URL/e-mail/redaction
real somente em ativação autorizada, sem alterar .env.test/.env.production.
O histórico 60,04% não é validação desta implementação futura.

## Progresso e fechamento

| Etapa/ticket | Fatias implementadas | Restantes | Estado |
| --- | --- | --- | --- |
| 1 — Contrato/recuperação | 3/3 | 0 | Wrappers, recuperação pública e contexto seguro validados |
| 2 — Perfil/sessão/aceite | 3/3 | 0 | Reset/perfil/UI/documentação e aceite manual aprovados |
| Total | 6/6 | 0 | Concluído; aceite e publicação registrados |

O refinamento original de 2026-11-10 foi exclusivamente documental, antes da
aprovação. Os registros abaixo substituem o progresso anterior e descrevem a
implementação autorizada em 2026-11-11. Nenhuma publicação Jaci foi registrada.


## Dependência publicada — 2026-11-11

A publicação Tupã 1.1.0 foi confirmada pelo usuário. O endpoint de consulta
é `POST /auth/session/validate` com credencial de serviço. O reset fica
vinculado ao produto ao enviar `X-Service-Token`. A integração do guard
continua na BL-0019. Esse registro precedeu a aprovação específica da BL-0010,
concedida pelo usuário no início da implementação descrito a seguir.


## Início da implementação — 2026-11-11

Refinamento aprovado pelo pedido de implementação após aceite da BL-0019.
Branch pai feature/BL-0010-reset-senha-login-area-logada, baseada em bfd31dc
na worktree atual. Os contratos do Tupã 1.1.0 estão publicados.


## Fatia 1.1 — Núcleo e contratos validados — 2026-11-11

Wrappers reais de forgot/reset/change, política de senha/normalização, contexto
Fernet por produto e limitador persistido por HMAC. Migração aditiva
20261111_0007 cria apenas auth_rate_limits; adoção SQLite legada também cria
as tabelas técnicas de sessão/limite sem perder usuários. Contador usa UPSERT
atômico, compartilhado por conexões/processos. Contexto dura uma hora e não
persiste token ou senha no banco Jaci.

Contratos unitários e HTTP focais: 28 aprovados, incluindo falha remota, expiração,
CSRF, produto estrangeiro e revogação. PostgreSQL 15 descartável: cadeia de
migrações completa, downgrade 0007 → 0006 → upgrade, 24 tentativas em oito
conexões concorrentes com contagem exata, reabertura da janela e limpeza vencida.
Nenhum serviço, conta, e-mail ou banco real usado nessa validação.


## Fatias 1.2/1.3/2.1/2.2 — Fluxos HTTP e sessão — 2026-11-11

Núcleo versionado em 2721091. Login oferece recuperação; perfil oferece senha
atual/nova/confirmação. Alias de e-mail move o opaco para contexto HttpOnly e
redireciona 303 à URL limpa. Contexto é dividido em até quatro cookies de 3500
caracteres para suportar token de até 4096 bytes sem ultrapassar o limite por
cookie; não há token em hidden, HTML, web storage ou banco Jaci.

CSRF/Origin são obrigatórios, inclusive sem guard no fluxo de senha. O formulário
público usa HMAC de nonce HttpOnly. Formulários com no-referrer podem emitir
Origin:null no Chromium; esse caso só é aceito nessas rotas com CSRF assinado
válido. Origem estrangeira, nonce forjado e campo ausente são recusados.

Reset/troca exigem novo login via revogação atômica do Tupã 1.1.0. Erro de senha
atual é separado de Bearer revogado por consulta autenticada. Após confirmação
remota, falha de limpeza local não volta a alegar que a senha não mudou. Reset
não propaga logout global de uma conta diferente eventualmente aberta no browser.
A fila de compras não é apagada nem credenciais são enfileiradas.

Worker v34 ignora as quatro rotas sensíveis e limpa suas entradas em caches
retidos durante a ativação, sem tocar IndexedDB. Logs uvicorn/httpx redigem as
queries preservando o formato exigido pelo AccessFormatter. Respostas sensíveis
incluem no-store/no-referrer; detalhes do provedor nunca voltam ao formulário.

Focais: 28 aprovados, incluindo privacidade/worker Node. Regressão: 378 aprovados,
2 xfailed preexistentes FL-08, cobertura 66,93% (piso 60%). A rodada final incluirá
os quatro contratos adicionais aprovados depois dessa regressão. UI nova: três
cenários aprovados, incluindo desktop sem JavaScript; sessão anterior: dois;
compras anteriores: dez. Fixtures e evidência final seguem na fatia 2.3.


## Fatia 2.3 — UI, documentação e entrega — 2026-11-11

Page Objects e fixtures seguem vgx-ui-tests. Provedor sintético expõe JWKS,
contratos de senha/sessão e caixa de saída local; não existe em rotas do Jaci
nem usa contas/e-mails reais. Runner prepara banco e servidor descartáveis,
completa o fluxo sem AUTH_MOCK e encerra ambos os servidores ao terminar.
O arquivo de entrada `.env.test` é somente lido para confirmar APP_ENV=test;
banco/credenciais existentes não são usados nem reescritos nesse modo.

| Validação executada | Resultado |
| --- | --- |
| ./scripts/run_tests.sh --coverage -q -o faulthandler_timeout=30 | 382 aprovados, 2 xfailed FL-08; 67,07% acima de 60%; 71,47s |
| Focais password_recovery/password_http/password_privacy | 28 aprovados; 5,14s |
| JACI_UI_PASSWORD_FLOWS=1 ./scripts/run_ui_tests.sh -q --tb=short | 3 aprovados; 9,27s |
| JACI_UI_SESSION_GUARD=1 ./scripts/run_ui_tests.sh tests/ui/test_access_session_playwright.py | 2 aprovados; 7,34s |
| Suíte UI habitual de compras, no modo mock isolado | 10 aprovados; cenários de senha/guard separados; 20,28s |
| PostgreSQL 15 descartável | Migração desde zero, downgrade 0007/0006 e upgrade; 24 UPSERTs em oito conexões, janela/limpeza aprovadas |
| SQLite legado e novo | Adoção conserva usuário e cria metadados; bancos novos preparados pelo runner/Alembic |
| Privacidade e PWA | Redaction Uvicorn/cliente, cookie/CSRF, no-store/no-referrer, bypass e limpeza seletiva aprovados |

Artifacts UI sintéticos: reports/playwright/0c8a46b1e915439c85a1f60582548a9e
(senha), 16ff9ee5673b4466a923c240edec192d (guard),
f06abf93a9774b3a9e7485c8c35ed6ab (compras). Sem tracing/vídeo e sem envio de
mensagens reais. Os 57 warnings da regressão são a depreciação utcnow do python-jose.

README, fluxos/regras, matriz de testes, índice, item e coordenação atualizados.
O grafo foi atualizado com venv/bin/graphify update . (AST, sem LLM/rede).
A migração não foi aplicada ao banco do usuário; run.py a aplica na próxima
inicialização autorizada. `.env.test`, `.env.production`, infraestrutura Caddy,
Tupã existente e dados de compra foram preservados.

### Critérios restantes de ativação/publicação

Aceite manual da BL-0010 pelo usuário: receber e-mail real no endereço correto,
abrir link de teste/produção conforme Product.base_url e concluir recuperação e
perfil com dois dispositivos; verificar retomada da fila e atualização PWA.
Operador deve conferir redaction de query no Caddy/coletor, HTTPS/cookies e origem
real percebida pelo Uvicorn para o limite compartilhado. Esses pontos não são
comprovados pelo stub ou pelo filtro da aplicação e não foram alterados por nós.

BL-0019 já tem aceite manual aprovado. Manter a worktree no pai
feature/BL-0010-reset-senha-login-area-logada, com 2721091 e a559476 e commit de
UI/evidência que acompanha este registro. Integração à release/develop/main e
publicação dependem da liberação do usuário; nenhum novo gate de implementação
ou nova demanda de correção foi criado.

## Ajuste visual após revisão — 2026-11-11

Subtarefa da BL-0010, solicitada pelo usuário na validação: links de recuperação
e retorno ao login passam a seguir o padrão já usado em criar/acessar conta.
Pergunta seguida de link verde, texto menor e centralizado, reutilizando
text-help/text-night/fw-medium. No login, recuperação fica na linha acima de
criar conta. O mesmo padrão se aplica ao retorno e novo link na redefinição.

Validação focal: 16 testes auth_pages/password_http aprovados e três cenários
Chromium de senha aprovados (14,26s), incluindo desktop sem JavaScript.
Templates Jinja e git diff --check válidos; grafo atualizado por AST.
Ajuste mantido na branch pai; escopo principal continua 6/6, em_validacao.


## Aceite manual aprovado — 2026-11-11

Após a implementação e o ajuste visual 080a571, o usuário confirmou que a
validação manual da BL-0010 foi finalizada e aprovada. Etapa 1: 3/3; etapa 2:
3/3; nenhuma fatia de implementação ou aceite manual restante.

BL-0010 e BL-0019 têm aceite manual aprovado. Este registro não comprova por
si só configuração de logs/origem do Caddy ou de produção: as conferências
operacionais da publicação permanecem com o operador. A versão 1.5.0 aguarda
liberação de integração e publicação; manter a worktree na branch pai da BL-0010.
Estado em_validacao preservado até registrar a publicação exigida pelo projeto.
Somente documentação atualizada neste aceite; testes anteriores não foram repetidos.


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
