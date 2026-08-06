# Backlog de produção

Este diretório é a fonte de verdade para novas demandas de produção do Jaci.
Ele acompanha bugs, ajustes e melhorias desde a entrada até a publicação, sem
substituir o refinamento técnico obrigatório em `docs/domain/tasks/`.

O [backlog legado](../decisions/backlog.md) registra entregas anteriores à
adoção deste processo. Seus identificadores não participam da numeração
`BL-NNNN` e nunca devem ser reutilizados no backlog atual.

## Entrada rápida

1. Localize o maior identificador `BL-NNNN` em
   `docs/domain/backlog/items/`.
2. Some um ao número, independentemente de tipo, prioridade ou estado. Se não
   houver item, comece em `BL-0001`.
3. Gere um slug curto, estável, em minúsculas, sem acentos e separado por
   hífens.
4. Copie o [template de entrada](TEMPLATE.md) para
   `docs/domain/backlog/items/BL-NNNN-slug.md`.
5. Preencha a entrada, adicione o item à visão ativa e registre mudanças
   relevantes no histórico cronológico.

O identificador nunca é reutilizado, inclusive para demandas duplicadas,
rejeitadas ou não reproduzidas. Renomear o slug não altera o identificador.
Antes de reservar um número, considere arquivos ainda não integrados por outras
pessoas para evitar colisões.

## Classificações

### Tipo

| Valor | Uso |
| --- | --- |
| `bug` | Comportamento existente difere do esperado ou causa falha em produção. |
| `ajuste` | Mudança limitada em comportamento, regra, conteúdo ou operação existente. |
| `melhoria` | Evolução de produto, experiência, arquitetura ou processo. |

### Severidade de produção

Severidade mede o impacto do defeito observado; prioridade define a ordem de
implementação. Os campos permanecem separados.

| Valor | Definição |
| --- | --- |
| `S0` | Incidente crítico, vulnerabilidade, exposição entre grupos, perda ou corrupção de dados ou indisponibilidade. |
| `S1` | Fluxo crítico bloqueado sem alternativa aceitável. |
| `S2` | Degradação relevante com alternativa disponível. |
| `S3` | Impacto pequeno, localizado ou visual. |
| `N/A` | Demanda que não representa defeito de produção. |
| `a_triar` | Valor transitório permitido antes da classificação na triagem. |

Uma demanda `S0` deve ser escalada imediatamente pelo canal de incidente. O
registro no backlog não substitui contenção, comunicação ou recuperação.

### Prioridade de implementação

| Valor | Definição |
| --- | --- |
| `P0` | Ação imediata. |
| `P1` | Próxima janela de trabalho. |
| `P2` | Trabalho planejável. |
| `P3` | Trabalho oportunístico. |
| `a_definir` | Valor inicial antes da triagem. |

Prioridade deve considerar severidade, frequência, alcance, valor, risco,
dependências, custo e capacidade.

## Ciclo de vida

O fluxo principal é:

```text
recebido -> em_triagem -> pronto_para_refinamento -> em_refinamento
         -> pronto_para_implementacao -> em_implementacao -> em_validacao
         -> concluido
```

Durante a triagem, um item pode ir para `aguardando_informacao` e retornar a
`em_triagem` quando a informação chegar.

| Estado | Critério de entrada e saída |
| --- | --- |
| `recebido` | Registro mínimo criado; deve seguir para triagem. |
| `em_triagem` | Evidências, impacto, classificação, riscos e duplicidades estão sendo avaliados. |
| `aguardando_informacao` | Falta informação objetiva para concluir a triagem. |
| `pronto_para_refinamento` | Triagem suficiente e demanda apta a ganhar especificação técnica. |
| `em_refinamento` | Documento em `docs/domain/tasks/` está sendo criado ou revisado. |
| `pronto_para_implementacao` | Objetivo, escopo, fatias, cenários TDD e validações foram refinados. |
| `em_implementacao` | Uma ou mais fatias aprovadas estão em desenvolvimento. |
| `em_validacao` | Implementação encerrada no escopo e submetida às validações previstas. |
| `concluido` | Validações obrigatórias passaram e a publicação foi registrada. |
| `duplicado` | Demanda coberta por outro item, que deve ser referenciado. |
| `rejeitado` | Demanda não será executada, com justificativa registrada. |
| `nao_reproduzido` | Tentativas registradas não confirmaram o comportamento. |

`concluido`, `duplicado`, `rejeitado` e `nao_reproduzido` são terminais.
Impedimentos não são estados: devem registrar impacto, responsável ou
dependência e próximo acompanhamento.

## Triagem e refinamento

A triagem confirma a demanda, classifica severidade e prioridade, identifica
domínio e regras afetadas, avalia riscos de segurança, LGPD, isolamento por
grupo, offline/sincronização, histórico financeiro, recorrência e separação
entre template e execução, procura duplicidades e define responsável e próximo
passo.

Ao entrar em `pronto_para_refinamento`, crie o documento técnico a partir do
[template de refinamento](../tasks/TEMPLATE.md) e adicione links recíprocos. O
item `BL` permanece como resumo operacional; objetivo técnico, escopo, fatias,
arquivos, cenários TDD e validações pertencem ao refinamento.

O estado `pronto_para_implementacao` é um gate: testes executáveis e código só
começam depois da aprovação explícita do refinamento.

## Git Flow

Antes de alterar arquivos versionados de uma demanda:

1. Confirme `git status --short` e `git branch --show-current`.
2. Parta de `develop` e crie `feature/BL-NNNN-slug`.
3. Não misture demandas distintas na mesma branch.
4. Registre a branch no refinamento.
5. Não faça merge, finalize ou remova a branch sem solicitação explícita.

## Evidências e dados sensíveis

Sanitize textos, imagens, logs e anexos. Nunca registre credenciais, tokens,
cookies, chaves, dados pessoais, dados financeiros identificáveis ou
informações de outro grupo. Material sensível deve permanecer em armazenamento
restrito e ser citado apenas por identificador seguro.

## Manutenção das visões

Os arquivos permanecem em `docs/domain/backlog/items/` durante todo o ciclo.
Arquivar significa mover a linha do índice ativo para o arquivado; o arquivo
não muda de caminho nem é apagado.

### Itens ativos

| ID | Título | Tipo | Severidade | Prioridade | Estado | Responsável | Atualizado em |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [BL-0001](items/BL-0001-operacao-offline-cobertura-rastreabilidade.md) | Completar cobertura e rastreabilidade da operação offline | `melhoria` | `a_triar` | `a_definir` | `recebido` | `a_definir` | `2026-07-24` |
| [BL-0002](items/BL-0002-unidades-medida.md) | Adicionar unidades de medida | `melhoria` | `a_triar` | `a_definir` | `recebido` | `a_definir` | `2026-07-24` |
| [BL-0003](items/BL-0003-historico-precos.md) | Disponibilizar histórico de preços por grupo e item | `melhoria` | `a_triar` | `a_definir` | `recebido` | `a_definir` | `2026-07-24` |
| [BL-0004](items/BL-0004-analise-gastos-dashboard-financeiro.md) | Disponibilizar análise de gastos e dashboard financeiro | `melhoria` | `a_triar` | `a_definir` | `recebido` | `a_definir` | `2026-07-24` |
| [BL-0005](items/BL-0005-inteligencia-compras.md) | Evoluir inteligência de compras | `melhoria` | `a_triar` | `a_definir` | `recebido` | `a_definir` | `2026-07-24` |
| [BL-0006](items/BL-0006-integracoes-externas.md) | Implementar integrações externas | `melhoria` | `a_triar` | `a_definir` | `recebido` | `a_definir` | `2026-07-24` |
| [BL-0007](items/BL-0007-replicacao-externa-backups.md) | Replicar backups em armazenamento externo | `melhoria` | `a_triar` | `a_definir` | `recebido` | `a_definir` | `2026-07-24` |
| [BL-0008](items/BL-0008-autoexclusao-anonimizacao-conta.md) | Disponibilizar autoexclusão e anonimização de conta | `melhoria` | `a_triar` | `a_definir` | `recebido` | `a_definir` | `2026-07-24` |
| [BL-0009](items/BL-0009-criptografia-repouso.md) | Implementar criptografia de dados em repouso | `melhoria` | `a_triar` | `a_definir` | `recebido` | `a_definir` | `2026-07-24` |
| [BL-0010](items/BL-0010-reset-senha-login-area-logada.md) | Disponibilizar reset de senha via login e área logada | `melhoria` | `N/A` | `P1` | `pronto_para_refinamento` | Engenharia Jaci | `2026-08-05` |

### Itens arquivados

Nenhum item do processo atual foi arquivado.

## Checklist de passagem ponta a ponta

1. A entrada recebe identificador, arquivo, estado `recebido` e linha ativa.
2. A triagem completa classificação, riscos, duplicidades e próximo passo.
3. Em `pronto_para_refinamento`, a tarefa é criada e ligada nos dois sentidos.
4. Somente com cenários TDD e validações definidos o item chega a
   `pronto_para_implementacao`.
5. Commits, resultados focados e impedimentos são ligados antes da validação.
6. Depois das validações e da publicação, o item muda para `concluido` e sua
   linha vai para a visão arquivada.
