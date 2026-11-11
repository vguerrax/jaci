# Planejamento de releases após a 1.3.0

Base anterior: v1.3.0, commit ff16202, em 2026-10-28.
Publicação atual: v1.4.0, commit a1e188e, em 2026-10-29, informada pelo usuário.
Validação offline confirmada pelo usuário; entregas da 1.4.0 concluídas no índice.
Plano solicitado pelo usuário em 2026-10-28. Versões são alvos sem datas fixas;
associação não altera prioridade, estado nem substitui aprovação do refinamento.
O [índice](README.md) e os itens são a fonte dos estados; esta visão não os duplica.

| Versão-alvo | Resultado | Demandas |
| --- | --- | --- |
| 1.4.0 | Ferramentas, ambiente isolado, testes e rastreabilidade offline | [BL-0026](items/BL-0026-ferramentas-ambiente-testes.md), [BL-0011](items/BL-0011-ampliar-cobertura-testes-ui.md), [BL-0001](items/BL-0001-operacao-offline-cobertura-rastreabilidade.md) |
| 1.5.0 | Redefinição de senha e continuidade da sessão | [BL-0010](items/BL-0010-reset-senha-login-area-logada.md), [BL-0019](items/BL-0019-sessao-autenticada-oito-horas-inatividade.md) |
| 1.6.0 | Exclusão e anonimização de conta | [BL-0008](items/BL-0008-autoexclusao-anonimizacao-conta.md) |
| 1.7.0 | Ordenação de compras, categorias e autocomplete | [BL-0023](items/BL-0023-priorizar-compras-status-data.md), [BL-0022](items/BL-0022-unificar-lista-categorias.md), [BL-0024](items/BL-0024-autocomplete-itens-historico.md) |
| 1.8.0 | Unidades de medida | [BL-0002](items/BL-0002-unidades-medida.md) |
| 1.9.0 | Histórico de preços | [BL-0003](items/BL-0003-historico-precos.md) |
| 1.10.0 | Recomendações para próximas compras | [BL-0005](items/BL-0005-inteligencia-compras.md) |
| 1.11.0 | Dashboard financeiro | [BL-0004](items/BL-0004-analise-gastos-dashboard-financeiro.md) |
| 1.12.0 | API de integrações máquina a máquina | [BL-0021](items/BL-0021-api-integracoes-execucoes.md) |
| 1.13.0 | Calendário e compartilhamento iniciado pelo usuário | [BL-0006](items/BL-0006-integracoes-externas.md) |

## Organização da 1.4.0

- [BL-0026](items/BL-0026-ferramentas-ambiente-testes.md) é coordenadora do ambiente, AUTH_MOCK, scripts e metadados documentais;
  não coordena um merge único dos três IDs: cada demanda tem branch e aceite próprios.
- [BL-0011](items/BL-0011-ampliar-cobertura-testes-ui.md) usa esse ambiente para cobertura Python, Playwright e GitHub Actions.
- [BL-0001](items/BL-0001-operacao-offline-cobertura-rastreabilidade.md) reconcilia os três contratos Python legados de FL-09 e sua documentação.
  Não depende da conclusão da [BL-0011](items/BL-0011-ampliar-cobertura-testes-ui.md); se entregue antes dela, usa contratos JavaScript
  executados via Node e mantém os cenários em navegador vinculados à [BL-0011](items/BL-0011-ampliar-cobertura-testes-ui.md).
- Sequência de execução preferida: [BL-0026](items/BL-0026-ferramentas-ambiente-testes.md) → [BL-0011](items/BL-0011-ampliar-cobertura-testes-ui.md) → [BL-0001](items/BL-0001-operacao-offline-cobertura-rastreabilidade.md). Gate separado por item.
- Nenhuma migração arquitetural de módulos integra a reorganização: trata-se de
  estrutura de trabalho, ferramentas e ambiente de testes.

## Dependências das próximas versões

- O escopo de backups da 1.5.0 foi abortado em 2026-11-10. Permanecem dump
  diário e retenção padrão de 30 dias; cópias são manuais, sem criptografia.
  Seus critérios de ativação anteriores não são pendências do roadmap atual.
  A 1.5.0 foi reaproveitada para acesso à conta e continuidade da sessão.
- 1.5.0 e 1.6.0 confirmam contratos do Tupã; mudanças nele precisam de ID e branch
  próprios. BL-0019 foi triada/refinada em 2026-11-10; a dependência de revogação
  D-01 foi publicada no Tupã 1.1.0, conforme confirmação de 2026-11-11.
  A integração e o aceite do consumidor são acompanhados na BL-0019 e BL-0010.
- Unidades precedem comparações de preços e quantidades: [BL-0002](items/BL-0002-unidades-medida.md) → [BL-0003](items/BL-0003-historico-precos.md) e [BL-0005](items/BL-0005-inteligencia-compras.md).
- [BL-0004](items/BL-0004-analise-gastos-dashboard-financeiro.md) não depende tecnicamente do histórico de preços; sua posição é estratégica.
- Revisar [BL-0021](items/BL-0021-api-integracoes-execucoes.md) depois de unidades e da fundação de testes, incluindo o contrato
  de unidades e o Redis ainda não configurado. Seu refinamento atual não autoriza código.
- [BL-0006](items/BL-0006-integracoes-externas.md) mantém confirmação do usuário, sem WhatsApp Business API ou envio automático.

## Contrato de acompanhamento

1. Versão-alvo fica no item; mudar alvo exige atualizar esta visão e registrar motivo
   no histórico. A visão é uma proposta de escopo, não evidência de publicação.
2. Dependências técnicas ficam na triagem; ordem estratégica não cria bloqueios artificiais.
3. Tarefas, fatias, progresso, comandos e resultados ficam no refinamento; evidências
   ligadas ao item incluem commit, ambiente e data, sem dados sensíveis.
4. Manter IDs, diretórios, estados e históricos; adicionar campos sem migrar os arquivos.
5. Cada implementação segue gate documental, TDD e validação; releases exigem aceite
   dos fluxos afetados, regressão e publicação registrada antes do encerramento.
6. Correções de releases publicadas usam 1.x.y; não preencher uma versão-alvo como entregue.
7. Depois da 1.4.0, refinar apenas a próxima release; este plano não antecipa decisões
   de produto ou infraestrutura das demais versões.

## Correções descobertas na validação da 1.4.0

[BL-0027](items/BL-0027-incorporar-item-sem-categoria.md): incorporação sem
categoria rejeitada no fechamento; correção independente necessária para o aceite UI.


## Ajuste de contrato do AUTH_MOCK antes da 1.4.0

[BL-0028](items/BL-0028-auth-mock-bypass-local.md): o usuário esclareceu que
APP_ENV=test e AUTH_MOCK=true devem habilitar login para usuários ativos da base
configurada, sem validação de senha no Tupã, contas fixas, nome de arquivo de
ambiente obrigatório ou banco marcado. O ambiente sintético dos scripts continua
isolado e opcional para esse uso manual. Refinamento versionado exige aprovação
antes de testes/código; não confundir a BL-0026 já implementada com este ajuste.


## Registro de publicação da 1.4.0

Tag v1.4.0 conferida em a1e188eecaff68cf1a24d65e7286c595338c7516, merge do
PR #46. Entregas: BL-0026, BL-0011, BL-0001 e correções BL-0027/BL-0028, mantendo
os identificadores já existentes. Regressão final: 307 passes/2 xfail FL-08,
dez cenários Chromium, PostgreSQL 17 e CI aprovados; cobertura 60,02%. Publicação e validação offline confirmadas pelo usuário. A próxima versão-alvo é 1.5.0;
este registro não inicia seu refinamento ou implementação.


## Validação e encerramento da 1.4.0

Usuário confirmou a operação offline. CI final em main/a1e188e aprovado pelo
[run manual 40978823250](https://github.com/vguerrax/jaci/actions/runs/40978823250),
com Python e Chromium em success e dois artifacts. A execução anterior por push
40978445816 havia falhado em Chromium; o rerun manual aprovou o mesmo commit.
BL-0026, BL-0011, BL-0001, BL-0027 e BL-0028 passam a concluido e suas linhas vão
para a visão arquivada. Registro documental mantido na branch da BL-0026 até
liberação do usuário; a 1.5.0 permanece somente como próxima versão planejada.


## Histórico da branch de integração da 1.5.0

Por solicitação explícita do usuário, release/v1.5.0 foi criada da develop após
integrar os refinamentos 3660568 (BL-0009) e 44842b1 (BL-0007). Esta é a base de
integração da versão; não altera o fluxo padrão das demais releases.

Usar somente a worktree atual do repositório. As seis worktrees temporárias
criadas anteriormente foram removidas a pedido do usuário; branches e commits
foram preservados. As branches das duas tasks devem ser atualizadas com esta base
antes do código; subtarefas opcionais -nn retornam somente à própria task.
Integração da task à release e da release à develop/main continua dependendo de
liberação do usuário. A integração documental não aprova testes ou implementação.
A tag publicada v1.4.0 permanece em a1e188e; main recebeu apenas o fechamento
documental da 1.4.0, enquanto os refinamentos da 1.5.0 ficam em develop/release.


## Cancelamento do escopo da 1.5.0 — 2026-11-10

O usuário abortou BL-0007 e BL-0009: o backup automático existente em dump,
diário e com retenção de pelo menos 30 dias foi considerado suficiente. A cópia
externa será manual; não haverá criptografia dos backups. Demandas arquivadas em
rejeitado, sem publicação e sem integração de seus códigos na release.

Branches e commits ficam preservados como histórico. O registro anterior da
base de release não autoriza retomar as tasks. A versão 1.5.0 passa ao escopo de acesso à conta e continuidade da sessão,
conforme o roadmap refeito solicitado em seguida; versões seguintes antecipadas
em uma posição. O piso de cobertura de 60%, pedido separadamente, permanece.


## Roadmap refeito e novo escopo da 1.5.0 — 2026-11-10

Após o aborto, o usuário solicitou o roadmap refeito e a composição da 1.5.0.
A sequência remanescente foi antecipada em uma posição, preservando IDs, ordem,
estados e dependências. A tabela inicial é a sequência vigente; as referências
históricas acima descrevem o planejamento anterior.

A versão 1.5.0 passa a conter:

- BL-0010: iniciar recuperação/redefinição de senha pela tela de login e troca
  de senha na área logada, com identidade/credenciais sob responsabilidade do Tupã.
  Refinada em [BL-0010](../tasks/BL-0010-reset-senha-login-area-logada.md),
  pronta para aprovação; 0/6 fatias implementadas.
- BL-0019: manter sessão com atividade e encerrá-la após oito horas de inatividade,
  preservando logout, revogação, troca de senha e recusa de tokens inválidos.
  Triada/refinada em [BL-0019](../tasks/BL-0019-sessao-autenticada-oito-horas-inatividade.md),
  pronta para aprovação; 0/6 fatias implementadas. A inspeção é estática, não medição
  da duração em produção.
- Piso de cobertura de 60% mantido como ajuste independente já solicitado;
  a suíte anterior apresentou 60,04%, sem nova execução neste replanejamento.

Sem criptografia, cópia SFTP automática ou pendências de ativação das tasks
abortadas no novo escopo. Manter dump diário existente, retenção padrão de 30 dias
e cópias externas manuais. A branch release/v1.5.0 permanece preservada como base;
a mudança documental na branch atual não integra código ou documentação nela.
Refinamentos e aprovação explícita ainda são necessários para começar as tasks
novas da versão. Não foram criadas branches, worktrees, demandas ou implementações.


## Refinamento versionado da nova 1.5.0 — 2026-11-10

[Coordenação e decisões](../tasks/release-1.5.0-acesso-conta-sessao.md):
BL-0019 (guard/concorrência/HTTP/WS/fila) precede a integração final da BL-0010
(recuperação/troca/perfil). Cada request HTTP autenticado, inclusive automático,
atualiza deadline em oito horas; pings/pongs e permanência WS não contam. Nenhum
novo heartbeat ou polling para sessão. Novo login global após senha, com fila
preservada e partição por identidade.

Tupã 4cee88f não oferece toda a semântica de revogação exigida. D-01 registra o
contrato necessário, sem fingir endpoint disponível ou demanda externa já criada.
A aprovação documental Jaci não autoriza modificar Tupã. Nenhuma nova chamada ou
execução de teste foi feita; 12 fatias futuras no total, aguardando aprovação.
Pacote em docs/refinamento-1.5.0, base 9d6a18c; sem merge à develop/release/main,
que continuam precisando da consolidação documental liberada pelo usuário.


## Provedor de sessões publicado — 2026-11-11

Tupã 1.1.0 publicado pelo usuário. A dependência externa D-01 está disponível
para a integração da release Jaci 1.5.0. BL-0019 está em validação após integração real, regressão e cenário de
navegador. BL-0010 aguarda sua aprovação específica.


## Implementação da nova 1.5.0 — 2026-11-11

BL-0019 teve aceite manual aprovado pelo usuário. BL-0010 foi autorizada e suas
seis fatias estão implementadas e em validação na branch pai, baseada em bfd31dc,
com recuperação pelo login, troca no perfil e revogação global via Tupã 1.1.0.
A [coordenação](../tasks/release-1.5.0-acesso-conta-sessao.md) registra progresso,
evidências e o aceite/publicação pendentes. A integração das tasks à release e
à develop/main depende da liberação do usuário; não houve publicação Jaci nova.
