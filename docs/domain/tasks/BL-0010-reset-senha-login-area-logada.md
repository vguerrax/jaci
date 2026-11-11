# Refinamento — BL-0010 — Recuperação e troca de senha — 1.5.0

## Rastreabilidade

- Backlog: [BL-0010](../backlog/items/BL-0010-reset-senha-login-area-logada.md).
- Coordenação: [1.5.0 — acesso e sessão](release-1.5.0-acesso-conta-sessao.md).
- Relacionada: [BL-0019](BL-0019-sessao-autenticada-oito-horas-inatividade.md).
- Estado: em_implementacao; aprovação do usuário em 2026-11-11.
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
  Necessita demanda própria registrada/refinada/aprovada no Tupã; ID ainda não
  atribuído. Nenhum arquivo do Tupã é alterado neste pedido.
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

Sem contratos de migração/refatoração futuros a marcar agora: esta é documentação,
não existem testes executáveis/xfail desta demanda. Quando aprovados, futuros
contratos por fatia podem usar xfail(strict=True), sem pendência no fechamento.

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
| 1 — Contrato/recuperação | 1/3 | 2 | Núcleo/contratos validados; adaptadores HTTP na próxima fatia |
| 2 — Perfil/sessão/aceite | 0/3 | 3 | Núcleo preparado; adaptadores e UI pendentes de commit |
| Total | 1/6 | 5 | Implementação em andamento na branch pai |

Links/escopo/estado conferidos documentalmente; não houve teste, mudança de banco,
asset ou ambiente, login remoto, acesso à Oracle, envio de e-mail ou alteração no
Tupã/Potira. Branch documental mantida na worktree atual. A disponibilidade deste
refinamento versionado precede a aprovação; publicação/aceite dependem das duas
tasks e evidências externas da coordenação.


## Dependência publicada — 2026-11-11

A publicação Tupã 1.1.0 foi confirmada pelo usuário. O endpoint de consulta
é `POST /auth/session/validate` com credencial de serviço. O reset fica
vinculado ao produto ao enviar `X-Service-Token`. A integração do guard
continua na BL-0019. A aprovação específica para implementar a BL-0010
permanece pendente.


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
