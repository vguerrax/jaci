# Refinamento — BL-0011 — Cobertura, navegador e CI

## Rastreabilidade

- Item: [BL-0011](../backlog/items/BL-0011-ampliar-cobertura-testes-ui.md).
- Versão-alvo: 1.4.0; responsável: Engenharia Jaci.
- Estado: em_implementacao; aprovação explícita recebida após versionamento.
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
| 2 — UI | 0/2 | 2 | Pendente ambiente BL-0026 |
| 3 — CI | 0/1 | 1 | Pendente |

## Fechamento

- Código/testes/workflow: não iniciados; nenhum arquivo tests/ui alterado.
- Validação nesta etapa: somente links, estados, índice e diff documental.
- Medição de cobertura e execuções Python/UI/CI: pendentes, sem percentual presumido.
- Publicação: pendente; implementação requer aprovação deste refinamento versionado.

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
