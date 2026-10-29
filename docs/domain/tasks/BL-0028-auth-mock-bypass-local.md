# Refinamento — BL-0028 — AUTH_MOCK como bypass local do Tupã

## Rastreabilidade

- Item: [BL-0028](../backlog/items/BL-0028-auth-mock-bypass-local.md).
- Versão-alvo: 1.4.0; responsável: Engenharia Jaci.
- Estado: em_validacao; aprovação explícita recebida para correção e testes Python/UI.
- Branch: feature/BL-0028-auth-mock-bypass-local, criada de develop 0c03134.
- Item isolado, um ticket com duas fatias sequenciais na mesma branch. Preservar
  branches anteriores e a edição local do usuário em run.py; usar worktree.
- Não alterar código/testes antes da aprovação. Não integrar ou remover a branch
  sem a autorização exigida pelo projeto.

## Objetivo e critérios de sucesso

1. APP_ENV=test e AUTH_MOCK=true ativam o bypass, com qualquer arquivo de ambiente
   ou variáveis de processo e qualquer banco suportado pela aplicação.
2. Usar o e-mail normalizado para localizar usuário existente e ativo na base
   configurada via SQLAlchemy. A senha é ignorada neste modo e pode ficar vazia.
   Usuário desconhecido/inativo falha; login não cria usuários.
3. Não exigir contas do seed, senha fixa, .env.test explícito, marcador de diretório
   ou banco SQLite de domínio. Usuário sem tupa_user_id também funciona.
4. Não consultar token/JWKS/refresh/logout do Tupã no modo mock. Cadastro/migração
   externa continuam indisponíveis nesse modo.
5. Preservar ID, tupa_user_id, hash legado, grupos e permissões do usuário. Somente
   a atualização habitual de last_login_at é permitida durante o login.
6. Preservar sessão assinada, expiração, renovação, rotação, revogação e reinício;
   sessões mock nunca são aceitas no modo real. HTTP, middleware e WebSocket devem
   resolver a mesma identidade local, sem atribuir um ID Tupã inventado ao usuário.
7. O caminho real com AUTH_MOCK=false mantém autenticação Tupã; APP_ENV diferente
   de test com AUTH_MOCK=true continua sendo recusado.
8. Setup, seed e runners automatizados continuam isolando seus dados por marcador;
   essas proteções pertencem às ferramentas, sem condicionar o bypass da aplicação.

## Escopo

Inclui configuração do modo mock, lookup local, identidade/sessões, tratamento da
senha no login, testes e documentação. Sem migração de usuários, alteração de
senhas reais, criação automática de grupos ou mudança nas regras de compras.
Nenhuma alteração do arquivo de ambiente ou banco do usuário será feita nesta
etapa documental. O seed sintético continua opcional para testes automatizados.

## Riscos e regras preservadas

- Segurança: o modo permite selecionar qualquer usuário local ativo pelo e-mail.
  É o bypass solicitado; restringi-lo a APP_ENV=test, manter aviso visual e recusar
  tokens mock no caminho real. Nunca implementar fallback automático após falha Tupã.
- LGPD: testes e artifacts usam dados sintéticos; não carregar base/segredos do
  usuário em fixtures, relatórios, logs ou tokens impressos.
- Grupo: autenticação local preserva verificações reais de pertencimento HTTP/WS,
  inclusive cookies e IDs de grupo adulterados.
- Offline/sincronização: preservar cookies, refresh e logout e executar os dois
  cenários UI existentes de fila/reconexão e conflito/resolução.
- Histórico financeiro: nenhuma migração ou mutação de compras. Não substituir
  usuários, grupos, vínculos ou UUIDs Tupã por valores de teste.
- Recorrência: regras e datas não mudam; regressão existente continua obrigatória.
- Template/execução: sem alteração de vínculos ou propagação automática.

## Plano de implementação

### Etapa 1 / Ticket 1 — Ajustar contrato do AUTH_MOCK

#### Fatia 1.1 — Contratos, configuração e adaptador de identidade local

- Ordem 1; escrever os contratos de todo o escopo antes de alterar produção.
- Arquivos esperados: app/config.py, app/services/test_auth_service.py,
  app/services/tupa_auth_service.py, app/services/auth_service.py,
  app/dependencies.py, app/main.py e tests/test_test_environment.py, com módulos
  auxiliares de teste quando necessários.
- Remover da ativação do AUTH_MOCK as verificações de ENV_FILE e banco marcado;
  manter o gate APP_ENV=test. As validações de runtime dos scripts permanecem.
- Substituir a conexão SQLite específica e whitelist do adaptador por lookup ORM
  na base configurada; senha não participa da decisão do mock. Não exigir vínculo
  Tupã nem preencher/alterar tupa_user_id para satisfazer o login.
- Distinguir identidade mock pelo emissor e ID local. Centralizar resolução dos
  claims para serviço, dependências HTTP/WS e middleware; caminho real mantém sub
  Tupã. Revalidar existência/atividade do usuário ao validar e renovar a sessão.
- Desacoplar o armazenamento interno de sessão do arquivo do banco de domínio.
  Reaproveitar a estrutura leve de sessões/segredo já existente, inicializada
  automaticamente em cache temporário privado, sem marcador ou configuração
  adicional. Segregar pelo projeto e fingerprint da conexão, sem expor URL/segredos.
  Não criar um novo banco de domínio, exigir seed ou adicionar migração de produção.
- Garantir geração segura do segredo, permissões privadas, rotação e revogação,
  persistência entre reinícios no mesmo host/cache e recusa de token adulterado.
- Focal: configuração e serviço, cenários HTTP/WS, mock sem rede e guards das
  ferramentas. SQLite temporário comum, sem marcador, e configurações PostgreSQL
  devem ser aceitas; o lookup usa o mesmo ORM dos demais serviços.

#### Fatia 1.2 — Formulário, regressão e documentação de uso

- Ordem 2; depende da fatia 1.1.
- Arquivos esperados: app/routers/auth.py, app/templates/pages/login.html,
  README.md, .env.test.example, tests/README.md, testes de auth/ambiente e cenários
  UI existentes; app/templates/base.html apenas se necessário para o aviso.
- Manter formulário e fluxo existentes. Senha opcional/ignorada quando mock está
  ativo; no caminho real a obrigatoriedade continua. Exibir indicação clara de
  autenticação simulada, sem exigir senha especial ou conta do seed.
- Login de usuário ativo sem grupos não deve falhar por user.groups[0]; respeitar
  o fluxo de perfil/grupos existente, sem criar grupos ou conceder acesso alheio.
- Separar na documentação o bypass com duas flags do ambiente sintético opcional
  preparado por setup_test_env.sh. Atualizar os testes antigos que exigem senha
  fixa/whitelist/restrição global de banco, preservando guards dos scripts.
- Preservar compatibilidade com as três contas do seed usadas pelos nove UI;
  acrescentar cenário de usuário local fora do seed, sem vínculo Tupã, senha vazia.
- Atualizar rastreabilidade BL-0026/BL-0028, grafo AST, resultados e progresso.

## Cenários TDD

1. Duas flags permitem Settings com ENV_FILE ausente/nome arbitrário e URLs de
   bancos suportados; nenhum acesso a banco ocorre só para validar Settings.
2. production/development/default recusam AUTH_MOCK antes de autenticar/conectar;
   AUTH_MOCK=false mantém o cliente real e recusa tokens mock.
3. Usuário local ativo fora da whitelist entra com senha vazia ou qualquer valor,
   sem consulta externa e sem validar hash legado. E-mail é normalizado.
4. Usuário ausente/inativo é recusado sem criação; sem tupa_user_id é aceito e seu
   campo permanece intacto. Não reutilizar o get_or_create_tupa_user nesse caminho.
5. Sessões HTTP/WS/middleware resolvem o ID local correto, preservam grupos e
   rejeitam acesso a grupo alheio. Usuário sem grupos não causa erro interno.
6. Token adulterado/expirado é recusado; refresh rotaciona e não pode ser reutilizado;
   logout revoga; reinício conserva a sessão; usuário inativado perde acesso.
7. Cadastro/migração não consultam Tupã no mock; o caminho real continua exercitado
   por mocks de rede. Nenhum teste depende de Tupã ou banco do usuário.
8. Setup/seed/runners ainda recusam destino não marcado/externo, mesmo que Settings
   aceite a configuração da aplicação. Não apagar as proteções das ferramentas.
9. Formulário aceita e-mail existente sem senha no mock; caminho real exige senha.
   Novos contratos UI usam somente dados sintéticos em servidor/base descartáveis.

Contratos da segunda fatia podem usar xfail(strict=True) durante a primeira;
nenhum permanece ao fechar o ticket. Dois FL-08 fora do escopo continuam pendentes.

## Estratégia de validação

- Por fatia: testes focais de configuração/auth/mock, lint quando configurado,
  compileall e revisão de ausência de alterações de identidades/vínculos.
- Compatibilidade SQLite/PostgreSQL: testes de lookup ORM e configuração; executar
  integração PostgreSQL somente com instância descartável, nunca base do usuário.
  Registrar explicitamente se validação comportamental PostgreSQL não disponível.
- Manual após aprovação: base temporária comum e arquivo de ambiente com outro
  nome, usuário sintético fora do seed e sem tupa_user_id; autenticar sem senha,
  consultar grupo autorizado, renovar, reiniciar e encerrar sessão.
- Final do ticket: bash scripts/run_tests.sh --coverage, piso 56,18% preservado,
  sem falhas/XPASS ou contratos próprios pendentes; Node via wrapper existente.
- UI: após autorização de execução, ENV_FILE=.env.test bash scripts/run_ui_tests.sh;
  repetir nove cenários existentes e o novo cenário do bypass. CI e artifacts mantêm
  isolamento; autorização anterior para os nove fluxos não cria aprovação de código
  para esta demanda.
- Atualizar grafo com venv/bin/graphify update . após código; commit de cada fatia
  validada. Merge final requer autorização específica, publicação/aceite antes de
  concluido. Não mexer no run.py editado pelo usuário sem necessidade aprovada.

## Progresso

| Etapa/ticket | Fatias concluídas | Restantes | Estado |
| --- | --- | --- | --- |
| 1 — Bypass local | 2/2 | 0 | Implementado e validado; integração pendente |

## Fechamento documental

- Backlog, refinamento, índice e visão de releases atualizados.
- Validações: links e diff documental; nenhum teste executável ou código alterado.
- Branch feature/BL-0028-auth-mock-bypass-local preservada em worktree isolada.
- Implementação, execução de novos testes, integração executável e publicação
  pendentes. Esta especificação substitui as restrições do mock da BL-0026 após
  aprovação e implementação, sem reescrever sua evidência histórica.

## Aprovação e início

Usuário aprovou 1ef2a8f após apresentação do refinamento, incluindo testes Python/UI
e integração documental. Documentação integrada em 2543931 antes dos executáveis.
Trabalho em worktree isolada; run.py do usuário preservado.

## Fatia 1.1 — Adaptador e identidade local

Doze falhas foram reproduzidas nos contratos antes da produção. O lookup agora
usa ORM na conexão configurada, senha ignorada e ID local no emissor jaci-test;
nenhum vínculo Tupã é preenchido. Cache privado de segredo/sessões é inicializado
automaticamente, por projeto/conexão, mantendo rotação, revogação e reinício.
Guards dos scripts continuam marcando seus próprios bancos sintéticos.

Validação: 30 passes/2 contratos futuros do formulário no focal completo; após
novo contrato de startup sem SMTP, 15 passes/2 futuros no módulo BL-0028. A falha
SMTP foi reproduzida antes do ajuste mínimo em app/utils/email.py: só o mock aceita
campos ausentes no mailer que não utiliza. Três UI (login, fila/reconexão e
conflito/resolução) passaram em 27,91s, run 393eea00e8c545df8b23f88d5bceccaa.
Compileall, diff e grafo AST aprovados. Contratos da fatia 1.2 permanecem futuros;
regressão total será feita quando ambos forem concluídos.

## Fatia 1.2 — Formulário e regressão final

- Fatia 1.1 versionada em 10931df. Dois contratos de formulário falharam antes do
  ajuste: senha obrigatória no mock e login sem grupos. Agora senha é opcional no
  mock, obrigatória no caminho real, com indicação visível; usuário sem grupos
  autentica sem indexação inválida. Nenhum usuário/grupo é criado no login.
- PostgreSQL 17 descartável revelou integer = varchar no lookup do sub textual.
  O erro 500 foi reproduzido, e um contrato do bind PostgreSQL falhou antes da
  conversão explícita para int. Mesmo cenário aprovado após a correção.
- Smoke PostgreSQL: venv/bin/python /tmp/jaci-bl0028-postgres-smoke.py. Instância Docker própria com tmpfs e porta efêmera localhost;
  cinco migrações aplicadas, development.env com as duas flags, sem SMTP/seed/
  marcador. Usuário sintético existente sem tupa_user_id entrou sem senha;
  autorização de grupo, sessão após reinício, logout/401 e preservação de IDs/hash/
  grupos aprovados. Servidor, container e diretório próprios removidos.
- Focal final de auth/formulário: 21 passes. Regressão pelo runner isolado:
  **307 passes/2 xfail FL-08 em 88,68s**, cobertura **60,02%**, piso 56,18% mantido.
  Nenhum xfail da BL-0028; 19 avisos de depreciação datetime.utcnow do python-jose.
- UI final autorizada: **10 passes em 33,66s**, run
  16f8e7ec471140a3b4424f4ecf9e9d5f. Inclui usuário fora do seed, senha vazia e
  tupa_user_id preservado, além dos nove fluxos anteriores. Artifacts sintéticos
  em reports/playwright/<run>/result.json, sem traces/vídeos/cookies publicados.
- A primeira rodada de regressão foi interrompida pelo reinício do servidor de
  execução; não foi considerada aprovação. A rodada final acima concluiu após
  a correção PostgreSQL. Compileall, pip check, diff e grafo AST aprovados.
  Pylint indisponível no ambiente; não instalado ad hoc.
- README, exemplo sintético e matriz de testes distinguem bypass manual (duas
  flags/base existente) dos guards dos scripts automatizados. Sem migração de
  esquema ou modificação do run.py/arquivo de ambiente/banco do usuário.
- Implementação 2/2 fatias, zero pendências próprias; CI remoto aprovado conforme registro abaixo.
  Integração executável na develop e publicação da 1.4.0 ainda pendentes.

## CI remoto / entrega para integração

- PR em rascunho: https://github.com/vguerrax/jaci/pull/45.
- Candidato 98c788de81afd73f53cf23d36bd09a0417662e7b aprovado no
  [run 40952438864](https://github.com/vguerrax/jaci/actions/runs/40952438864).
  Jobs Python coverage e Chromium mobile and desktop concluíram com success,
  incluindo as dez UI, preparação isolada e publicação dos artifacts previstos.
- Commits das fatias: 10931df e 98c788d. Progresso: 2/2, zero pendências próprias.
  O registro posterior ao CI altera somente os dois documentos de acompanhamento.
- Branch feature/BL-0028-auth-mock-bypass-local preservada; integração executável
  na develop aguarda autorização específica. A edição do usuário em run.py e sua
  base de desenvolvimento permanecem preservadas; sem deploy.
- Publicação e aceite da 1.4.0 pendentes; estado em_validacao.
