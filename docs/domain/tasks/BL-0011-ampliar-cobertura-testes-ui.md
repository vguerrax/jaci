# Refinamento — BL-0011 — Cobertura, navegador e CI

## Rastreabilidade

- Item: [BL-0011](../backlog/items/BL-0011-ampliar-cobertura-testes-ui.md).
- Versão-alvo: 1.4.0; responsável: Engenharia Jaci.
- Estado: em_validacao; aprovação explícita recebida após versionamento.
- Branch documental: feature/BL-0011-refinamento-1-4-0, criada da develop.
  Preservar a branch anterior feature/BL-0011-ampliar-cobertura-testes-ui e seus commits.
- Depois do merge documental, atualizar esta branch pela develop antes do código;
  usá-la como integração deste item. Branches filhas feature/BL-0011-t1-cobertura,
  feature/BL-0011-t2-ui e feature/BL-0011-t3-ci derivam dela e retornam só para ela.
  Integração final na develop exige aprovação; não agregar código de outros IDs.

## Objetivo e critérios de sucesso

1. Medir linhas/branches do Python da aplicação e publicar relatórios reproduzíveis.
2. Exercitar fluxos críticos em Chromium real, viewport móvel, sem depender do Tupã.
3. Rodar os mesmos scripts localmente e em GitHub Actions, com falha propagada.
4. Registrar escopo real, lacunas e evidências; não confundir Python coverage com JS/UI.
5. Preservar a suíte atual e os dois xfail de funcionalidades FL-08 não entregues.

## Escopo

Inclui métricas Python, estrutura tests/ui, Page Objects/fixtures/factories mínimos,
runner UI e GitHub Actions. Não inclui AUTH_MOCK/seeds (BL-0026), reconciliação dos
três contratos offline legados (BL-0001), regressão visual ou todos os browsers.
As contagens históricas 262 passes/5 xfail são inventário; execução atual será evidência.

## Riscos e regras preservadas

- Segurança: executar guardas da BL-0026, nunca segredos de produção no CI ou artifacts.
- LGPD: screenshots/traces somente de fixtures sintéticas; não publicar cookies nem tokens.
- Grupo: owner/member/outsider com grupo ativo validado, sem simular autorização.
- Offline: usar navegador offline e persistência IndexedDB; não substituir fila por mock.
- Histórico: comparar valores persistidos e snapshots; fixtures não consultam banco real.
- Recorrência: finalização não duplica próximo ciclo; data de conclusão rege o ciclo.
- Template/execução: aprendizagem somente por confirmação e identidade preservada.

## Plano de implementação

### Etapa 1 / Ticket 1 — Medição Python

#### Fatia 1.1 — Baseline e relatórios

- Arquivos esperados: requirements-dev.txt, configuração coverage, scripts/run_tests.sh,
  tests/README.md, contratos do runner.
- Acrescentar pytest-cov em dependências de desenvolvimento com versão compatível
  verificada na implementação; medir app/ com branch coverage, terminal, XML e HTML.
- Rodar a suíte atual e versionar baseline numérico apurado nesta fatia; não inventar
  percentual. CI falha abaixo dessa baseline; avanços só a aumentam, redução exige
  revisão documentada. Relatórios em reports/coverage, ignorados no Git.
- Separar coleta Python de UI. Encaminhar seletores/args sem mascarar saída de erro.
- Validar relatório gerado, seleção focal, resultado não zero em falha e aplicação
  do piso medido, sem testes que apenas repetem configuração literal.

### Etapa 2 / Ticket 2 — Navegador real

#### Fatia 2.1 — Runner e fixtures UI

- Depende de BL-0026 concluída no escopo ambiente/mock/scripts e aprovada localmente.
- Arquivos esperados: scripts/run_ui_tests.sh, dependências dev, tests/ui/conftest.py,
  tests/ui/helpers/, fixtures/ e pages/, .gitignore e README.
- Adotar pytest-playwright com Chromium e instalação explícita documentada; sem alterar
  arquitetura da aplicação. Page Objects usam nomes/roles e controles existentes.
- ENV_FILE=.env.test bash scripts/run_ui_tests.sh é a entrada; runner cria diretório
  e banco novos, seed, servidor próprio em 127.0.0.1, aguarda health com timeout,
  executa testes e limpa somente recursos próprios no sucesso/erro/interrupção.
- Não reutilizar servidor sem marcador da execução nem matar processo por número da porta.
- Usar JACI_RUN_PLAYWRIGHT=1 pelo runner; coleta geral mantém UI desabilitada com
  motivo explícito. Não importar flags ou tenants de Moara: domínio local é grupo.
- Começar com UI_TEST_WORKERS=1 para servidor/banco únicos por execução; paralelismo
  exige isolamento por worker e fica fora desta entrega. Seletores de teste são aceitos.
- Traces e screenshots apenas em falha em reports/playwright; limpar contexto entre
  casos e manter evidências sintéticas. Não registrar headers/cookies em logs.

#### Fatia 2.2 — Fluxos críticos

- Arquivos esperados: tests/ui/test_*_playwright.py, pages/, fixtures/, factories/.
- Cobrir login sintético e logout; criar template e execução snapshot; compra de item
  com total; BL-0020 (nome protegido, avulso renomeável, incorporação confirmada);
  isolamento de grupos; dois contextos concorrentes com conflito explícito;
  fila offline após recarga, reconexão sem duplicação e resolução explícita.
- Dados gerados por fixtures limitados ao ambiente/execução, com quantidades e preços
  sintéticos. Assertar HTML visível e efeito persistido, sem sleeps fixos.
- Viewport 390x844; acrescentar smoke desktop 1280x800 para navegação/layout básico.
- Mapeamento dos cenários à regra e fluxo em tests/README.md; não contar cenário
  especificado como executado. BL-0001 reutiliza esses cenários, sem duplicar código.

### Etapa 3 / Ticket 3 — CI e evidências

#### Fatia 3.1 — GitHub Actions

- Arquivos esperados: .github/workflows/tests.yml, documentação de execução e relatórios.
- Pull requests e pushes para develop/main disparam jobs Python e Chromium UI,
  Python 3.12, ambiente test e AUTH_MOCK, dados sintéticos, sem segredos Tupã.
- Python chama scripts/run_tests.sh com cobertura; UI chama o runner comum com
  ENV_FILE explícito. Job UI depende do sucesso Python; nenhum job publica aplicação.
- Instalação explícita do browser com suas dependências; cache não deve conter banco,
  sessões ou tokens. Dependências fixadas, sem instalar pacotes silenciosamente no runner.
- Armazenar relatórios de cobertura e artifacts de falha por 7 dias, sanitizados.
  Timeout de job 15 minutos; qualquer falha real impede sucesso do workflow.
- Documentar como tornar os checks obrigatórios no serviço GitHub; alteração de
  proteção de branch não é presumida nem necessária para criar o workflow.

## Cenários TDD e contratos futuros

Depois da aprovação, escrever contratos de runners/isolamento/relatórios e cenários
UI antes de sua implementação; xfail(strict=True) só para fatias futuras deste item.
Não escrever nem executar testes UI durante o refinamento. Para a execução UI,
obter solicitação explícita e usar sempre scripts/run_ui_tests.sh, conforme vgx-ui-tests.

## Estratégia de validação

- Por fatia: testes diretamente afetados, bash -n, lint configurado e diff check;
  configurar e validar guardas antes de iniciar qualquer servidor.
- Manual: executar comandos de um checkout limpo, observar diretório isolado,
  código de erro, artifacts e ausência de acesso externo ao Tupã.
- Fechamento de ticket/item: scripts/run_tests.sh e suíte focal/total de UI quando
  explicitamente solicitada; jamais usar resultado de skip como aprovação do browser.
- Validar workflow em branch de trabalho; registrar link/run/commit e resultados reais.
  Sem disponibilidade do GitHub ou Chromium, registrar impedimento e não concluir.
- Atualizar grafo após código; acompanhar cenários, percentuais e limites no refinamento.
- Publicação da 1.4.0 exige registro dos jobs aprovados e aceite mobile/offline.

## Progresso

| Etapa/ticket | Fatias concluídas | Restantes | Estado |
| --- | --- | --- | --- |
| 1 — Cobertura | 1/1 | 0 | Concluída |
| 2 — UI | 2/2 | 0 | Nove cenários aprovados |
| 3 — CI | 1/1 | 0 | Python e Chromium aprovados no GitHub |

## Fechamento

- Cobertura entregue em 048a000, integrada somente na branch BL-0011.
  Runner e nove cenários UI escritos na branch feature/BL-0011-t2-ui, sem
  execução de navegador; workflow CI ainda não implementado.
- Validação: 281 passes na tarefa 1 e 55,97% de cobertura; cinco contratos
  focais de cobertura/guardas aprovados após criação do runner.
- UI autorizada e executada: nove cenários aprovados; CI remoto aprovado em ambos os jobs.
- Publicação: pendente; refinamento aprovado e em implementação.
  Execução UI aguarda solicitação explícita exigida pela skill vgx-ui-tests.

## Início da implementação

BL-0026 integrada com autorização explícita em b289771. Branch de integração
BL-0011 atualizada e tarefa 1 iniciada em feature/BL-0011-t1-cobertura.

## Evidência da tarefa 1 — Cobertura

- pytest-cov 7.1.0 / coverage 7.17.0 instalados e fixados no requirements-dev.
  Compatibilidade conferida nos metadados do pacote e instalação no Python 3.12.
  Referência: https://pypi.org/project/pytest-cov/7.1.0/.
- Três contratos vermelhos precederam o runner --coverage. Os três agora passam:
  relatórios para seleção focal, piso 100 reprovando seleção aprovada e falha de teste
  preservada. O runner comum mantém uso sem cobertura para ciclos focais.
- Regressão com cobertura: **281 passes e 7 xfail**, sendo dois contratos futuros da
  tarefa UI; cinco legados permanecem fora do escopo. Sem falhas/XPASS.
- Baseline combinada de linhas e branches: **55,97%**, armazenada em .coveragerc.
  Relatórios XML/JSON/HTML em reports/coverage, ignorados no Git e no Docker.
- Medição do processo pytest, não JavaScript, browser ou subprocessos não instrumentados.
  Testes de mock/seed em subprocessos continuam aprovados mas não alimentam essa métrica;
  porcentagem não representa cobertura integral de todos os processos do produto.
- scripts/run_tests.sh --coverage aplica o piso; seleções focais podem usar
  --cov-fail-under=0 explicitamente sem alterar a baseline versionada.
- Redução do piso exige revisão documentada; aumentos acompanham evolução medida.

## Preparação UI — execução ainda pendente

Runner, fixtures, Page Objects e nove cenários escritos; Chromium baixado em cache
local. Dependências pytest-playwright 0.10.0 / playwright 1.64.1 fixadas.
Os dois contratos de recusa do runner passaram sem iniciar browser.
Bootstrap 5.3.3 e HTMX 2.0.4 são os bundles reais do produto: cache de teste explícito
com hashes versionados em tests/ui/assets.json, sem instalar framework na aplicação.
Instalação dos assets é separada do runner para não depender de CDN durante o teste.
Artifacts públicos são limitados a screenshots sintéticos de falha e status JSON;
traces/vídeos são desativados porque podem registrar cookies/corpos de login.
A skill vgx-ui-tests exige solicitação explícita de execução UI após criar os testes;
a autorização foi pedida, sem executar os cenários por inferência.

Dependências verificadas por pip check, sem incompatibilidades; compileall e diff
aprovados. A preparação UI não foi integrada à branch do item por faltar a
validação de navegador. Código da BL-0011 permanece fora da develop.

## Evidência da tarefa 2 — Navegador

- Execução UI explicitamente solicitada pelo usuário em 2026-10-29. Primeira rodada:
  7 passes e 2 falhas. Defeito de incorporação sem categoria registrado como BL-0027,
  refinado em e25a531, corrigido em 12ee496 e integrado à develop com autorização.
- Espera do teste concorrente corrigida para o evento real jaci:sync-error após
  persistência da fila; não usar Promise assíncrona como condição booleana. Os dois
  contextos mantêm seus cookies e IndexedDB independentes; valor remoto preservado
  após resolução explícita Usar servidor.
- Runner corrigido para recriar pasta vazia removida pelo Playwright antes de gravar
  resumo; limpeza de processos/diretório ocorre mesmo se houver erro de artifacts.
- Rodada final: **9 passes em 20,65s**, run abd0941017004287bd800d4b7517fec6.
  Resultados sintéticos em reports/playwright/<run>/result.json; não há screenshots
  de sucesso, traces, vídeos, cookies ou payloads de login publicados.
- Cenários: login/logout móvel; compra/total/nome protegido; isolamento outsider;
  desktop; criar lista/execução snapshot; avulso renomeável; incorporação confirmada
  sem categoria; fila persistida após recarga/reconexão sem duplicação; concorrência
  e resolução explícita. Mesmos dados da falha de categoria foram mantidos.
- Compilação Python, guards do runner, bash -n e diff aprovados. Chromium e bundles
  reais em cache, sem mock da fila. Workflow foi preparado em branch de tarefa
  isolada e aprovado por actionlint; só será integrado após validação remota.

Regressão da tarefa 2: **288 passes/5 xfail legados**, cobertura **56,18%**.
Piso elevado para 56,18% com arredondamento à precisão do coverage, sem truncamento
manual. Nenhum xfail próprio pendente. O piso inicial medido na tarefa 1 foi 55,97%
na apresentação; o valor numérico versionado atual acompanha a regressão final.

## Preparação CI

Workflow tests.yml com jobs Python/Chromium em ubuntu-24.04, Python 3.12 e
Actions oficiais v7 fixadas por hashes. Python usa runner comum e piso 56,18%;
UI depende do sucesso Python, prepara Chromium/assets/ambiente e usa o runner.
Artifacts limitados a cobertura e screenshots sintéticos/status, por sete dias.
Token GitHub com contents:read, checkout sem persistir credenciais e nenhum deploy.
YAML aprovado por actionlint (imagem b1934ee5f1c5). Execução remota em PR de
rascunho será registrada antes de concluir a tarefa; merge final do item segue
pendente de autorização explícita. Branch de tarefa: feature/BL-0011-t3-ci.

## Evidência da tarefa 3 / entrega para integração

- Workflow em 78cbfb1, branch feature/BL-0011-t3-ci. PR rascunho:
  https://github.com/vguerrax/jaci/pull/43 (somente validação, sem merge).
- GitHub Actions run 40814194309, head 78cbfb19fe2960cdad516ebb61a09698f9705054:
  https://github.com/vguerrax/jaci/actions/runs/40814194309.
  Jobs Python coverage e Chromium mobile and desktop concluíram com success,
  incluindo instalação, runners isolados e publicação dos artifacts previstos.
- Regressão local final: 288 passes/5 xfail legados e 56,18% de cobertura combinada;
  nove Playwright aprovados em 20,65s. Nenhum xfail próprio pendente.
- Commits: 048a000 (tarefa 1), c15e453 (tarefa 2) e 78cbfb1 (workflow).
  Tarefa 3 retorna somente à feature/BL-0011-refinamento-1-4-0; integração final na
  develop aguarda autorização explícita. Branches e worktrees preservados.
- Progresso: 4/4 fatias implementadas e validadas. Publicação da 1.4.0 pendente;
  não marcar concluido. Proteção de branch do GitHub não foi alterada.
- O PR de rascunho comprova o workflow; não houve deploy nem autorização de
  integração da branch individual da tarefa.
