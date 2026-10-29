# Refinamento — BL-0026 — Ferramentas e ambiente de testes

## Rastreabilidade

- Item: [BL-0026](../backlog/items/BL-0026-ferramentas-ambiente-testes.md).
- Versão-alvo: 1.4.0; responsável: Engenharia Jaci.
- Estado: em_validacao; aprovação explícita recebida após versionamento.
- Branch: feature/BL-0026-ferramentas-ambiente-testes, criada de develop.
- Após merge documental, preservar e atualizar a branch com develop; será a branch
  de integração deste item. Branches filhas feature/BL-0026-t1-ambiente e
  feature/BL-0026-t2-scripts saem dela e retornam somente para ela.
  Merge final executável na develop requer autorização; não agregar BL-0011/BL-0001.

## Objetivo e critérios de sucesso

1. Abrir manualmente o Jaci e executar testes sem Tupã usando identidades sintéticas.
2. Recusar AUTH_MOCK fora de APP_ENV=test antes de criar banco, migrar ou iniciar servidor.
3. Autorização por grupo, cookies, renovação e logout continuam sendo exercitados.
4. Setup, seed, servidor e testes possuem comandos comuns local/CI e falham com código útil.
5. Backlog mantém IDs/estados/histórico com versão-alvo e visão de releases ligadas aos itens.

## Escopo

Inclui ambiente, adaptador de autenticação de teste, seeds, scripts e metadados
aditivos de planejamento. Não inclui migração da arquitetura, nova política de
sessão, senhas locais de produção, métricas/Playwright/CI ou novos domínios offline.
Métricas e suíte UI são BL-0011; reconciliação FL-09 é BL-0001.

## Riscos e regras preservadas

- Segurança: AUTH_MOCK=false por padrão; APP_ENV padrão production, valores
  development/test/production explícitos; mock só com test. Nunca derivar segurança
  de DEBUG, hostname ou presença de pytest. Testar configuração por processos novos.
- LGPD: e-mails example.com e credenciais sintéticas; nenhum segredo de produção.
- Grupo: usuários de teste consultados no banco e submetidos às dependências reais.
- Offline: cookies e duas sessões independentes devem funcionar com a fila existente.
- Histórico: setup/seed/limpeza restritos a diretório exclusivo .test-runtime/ ou
  diretório temporário criado pelos scripts e identificado por marcador de execução;
  recusar URLs/bancos externos e não carregar .env/.env.production implicitamente.
- Recorrência e template/execução: sem mudanças funcionais; seeds preservam snapshots.

## Plano de implementação

### Etapa 1 / Ticket 1 — Ambiente e autenticação de teste

#### Fatia 1.1 — Configuração e banco isolados

- Arquivos esperados: app/config.py, scripts/setup_test_env.sh,
  scripts/seed_test_data.py, .env.test.example, .gitignore, testes de contratos.
- .env.test local ignorado, criado a partir do exemplo sem ler env real;
  SQLite em arquivo para servidor e navegador; pytest atual mantém banco em memória.
- Executar com ENV_FILE explícito; bloquear sobrescritas ambientais de banco fora
  do diretório autorizado. Migrações/seed só depois de validar destino e marcador.
- Seed idempotente cria dois grupos e contas owner, member, outsider em example.com;
  nomes determinísticos no ambiente, IDs locais consultados, UUIDs Tupã sintéticos.
  Cleanup remove apenas o diretório da execução, nunca dados reais ou volumes Docker.
- Validar recusa de destino real, repetição sem duplicar e ambiente faltante.

#### Fatia 1.2 — AUTH_MOCK na fronteira Tupã

- Arquivos esperados: app/services/tupa_auth_service.py, módulo auxiliar de mock,
  testes de autenticação; ajustes mínimos em config/README.
- Preservar funções públicas do cliente; selecionar adaptador exclusivamente pela
  configuração validada. Login normal aceita apenas contas sintéticas sem cadastro
  arbitrário; operações não implementadas respondem erro explícito, sem chamar Tupã.
- Emitir tokens assinados de teste com segredo aleatório por ambiente, expiração e
  identificação inequívoca; não aceitar esses tokens no caminho real. Não aceitar
  token/cookie cujo conteúdo apenas declara usuário. Não reintroduzir senha local real.
- Cobrir token, decode, refresh e logout usados pelo middleware e pelas dependências
  HTTP/WebSocket, inclusive expiração/revogação. Registrar sessões de teste no SQLite
  isolado para sobreviver a reinício; reter vínculo com usuário sintético.
- Não adicionar login público de bypass; usar formulário existente. Interface de teste
  deve indicar ambiente simulado; sem credenciais reais e sem dependência de rede externa.
- Validar proprietário/membro/outsider, grupo adulterado, token inválido, sessão revogada,
  mock recusado em produção e caminho real sem alteração quando mock=false.

### Etapa 2 / Ticket 2 — Scripts e operação local

#### Fatia 2.1 — Comandos comuns

- Arquivos esperados: scripts/run_test_server.sh, scripts/run_tests.sh,
  scripts/setup_test_env.sh, README.md e contratos dos scripts.
- setup cria ambiente e seed; servidor usa APP_ENV=test, AUTH_MOCK explícito,
  host 127.0.0.1 e porta configurável (padrão 8014), sem reload.
- run_tests executa testes Python excluindo tests/ui; encaminha seletores e mantém
  código de saída. Para UI, o comando futuro é scripts/run_ui_tests.sh (BL-0011).
- Scripts usam venv/bin/python por padrão e falham se dependências estiverem ausentes;
  não instalar pacotes silenciosamente. Documentar instalação e operação em checkout limpo.
- Servidor manual mantém banco até limpeza explícita do seu diretório; automação usa
  diretório novo por execução e encerra apenas processos que iniciou, mesmo sob falha.
- Não chamar publish.sh, recriar containers reais ou acessar banco configurado no shell.
- Atualizar grafo após código; documentação de comandos e resultados acompanha cada fatia.

### Entrega documental já autorizada

Versionar releases.md, versão-alvo dos itens ativos e campos nos templates.
Manter estados no índice/itens, progresso e evidências nos refinamentos; sem duplicar
uma máquina de estados no roadmap. Esta entrega não aprova as etapas executáveis.

## Cenários TDD

Escrever após aprovação: configuração inválida falha antes da conexão; seed repetido;
comando com env ausente/real; execução sem Tupã; dois grupos sem vazamento; login
owner/member/outsider; tokens inválidos/expirados/revogados; refresh após reinício;
logout; host local; seleção de testes/código de saída; cleanup em erro sem tocar dados
alheios; modo real permanece sem mock. Cada teste deve verificar comportamento.

### Contratos futuros

Após aprovação, criar contratos do escopo antes do código; marcar apenas as fatias
futuras com xfail(strict=True), removendo-os na fatia correspondente. Não criar xfail
para funcionalidades de outras demandas nem alterar agora tests/ui.

## Estratégia de validação

- Por fatia: contratos pertinentes, bash -n nos scripts, lint configurado, diff check,
  migrações apenas no banco isolado e atualização de documentação.
- Manual: checkout limpo → setup → servidor → login sintético → troca de grupo →
  logout → reinício; confirmar falha explícita ao solicitar mock em produção.
- Ao fechar ticket e item: scripts/run_tests.sh; sem xfail próprio pendente.
- Playwright só na BL-0011 após aprovação e solicitação explícita de execução UI.
- Release: verificar AUTH_MOCK desativado em produção, aceite, regressão e publicação.

## Progresso

| Etapa/ticket | Fatias concluídas | Restantes | Estado |
| --- | --- | --- | --- |
| 1 — Ambiente/mock | 2/2 | 0 | Concluída |
| 2 — Scripts | 1/1 | 0 | Concluída |

## Fechamento

- Tarefas 1 e 2 concluídas (3/3 fatias); nenhuma credencial/ambiente real alterado.
- Validações documentais: links, índices, estados e diff conferidos.
- Validação executável e smoke HTTP aprovados; aceite visual em navegador,
  integração final na develop e publicação da 1.4.0 pendentes.
- Aprovação recebida; implementação conduzida com vgx-development.

## Evidência da fatia 1.1

Contratos do escopo criados antes do código; seis falhas iniciais reproduzidas.
Configuração exige APP_ENV=test e banco SQLite marcado para AUTH_MOCK; setup e seed
isolados e idempotentes. Fatias futuras têm xfail(strict=True) temporário.
O diretório sintético é excluído do Git e do contexto Docker, incluindo segredo.

## Evidência da fatia 1.2 / tarefa 1

Mock de login/refresh/logout implementado na fronteira Tupã. Sessões SQLite e
segredo aleatório por ambiente sobrevivem a reinício. Token adulterado/expirado,
refresh reutilizado e sessão revogada são rejeitados. O caminho real rejeita
issuer de teste antes de consultar JWKS. Operações não suportadas falham sem rede.
SMTP é suprimido no mock e a interface sinaliza autenticação simulada.
Regressão da tarefa 1: **274 passes e 7 xfail**, dos quais dois contratos temporários
da fatia 2.1; cinco são legados fora do escopo. Isolamento HTTP, cookies e logout
validados com TestClient local e bloqueio de clientes externos nos testes.
A execução restrita de TestClient bloqueou; a mesma validação local foi aprovada
com execução escalada. Nenhum browser Playwright foi criado ou executado.

## Evidência da fatia 2.1 / tarefa 2

- Scripts setup_test_env.sh, run_test_server.sh e run_tests.sh entregues com
  instalação explícita de dependências, host 127.0.0.1, porta padrão 8014 e sem reload.
- Runner Python configura banco em memória sem mock nesse processo, preservando
  as fixtures legadas; os contratos específicos usam subprocessos de mock isolados.
  Ambiente herdado da aplicação é descartado, sem ler .env/.env.production.
- Dois contratos de scripts falharam antes do código; depois dele, testes de seleção,
  código de saída, configuração herdada e limpeza passaram. Cleanup só em diretório
  marcado, e subprocessos pertencentes à execução são encerrados em falha/sinal.
- Regresso final pelo runner: **278 passes, 5 xfail em 34,32s**, sem falhas/XPASS;
  nenhum xfail próprio pendente. Os cinco existentes pertencem a BL-0001/0003/0004.
- Smoke com servidor real em porta efêmera local: setup, login owner, indicação de
  ambiente simulado, snapshot apenas da Casa A e logout/401 aprovados. Servidor e
  diretório temporários foram removidos. HTTP e dependência de identidade WebSocket
  testados; não foi feito aceite visual em navegador ou teste de browser offline.
- Migrações aplicadas repetidamente somente nos bancos SQLite temporários do setup;
  nenhuma revisão de esquema de produção foi criada. AUTH_MOCK persiste sessões em
  arquivo SQLite separado, fora das tabelas do domínio.
- bash -n dos três scripts e diff check aprovados; grafo AST atualizado;
  pylint indisponível no ambiente, sem instalação ad hoc.
- Commits da tarefa 1: b6a3b47 e 245aa0e; merge e54974b na integração BL-0026.
  Branch da tarefa 2: feature/BL-0026-t2-scripts; retorna exclusivamente para a
  feature/BL-0026-ferramentas-ambiente-testes. develop permanece sem código da demanda.
- Próximo passo: aceite do ambiente e autorização explícita de integração na develop
  antes de iniciar BL-0011 com a fundação disponível. Publicação da 1.4.0 não efetuada.
