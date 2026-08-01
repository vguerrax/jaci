# BL-0012 — Gestão documental compartilhada dos projetos VGX

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0012` |
| Título | Gestão documental compartilhada dos projetos VGX |
| Tipo | `ajuste` |
| Estado | `concluido` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-07-30` |
| Origem | Solicitação direta para consolidar as políticas de Moara e Potira |
| Ambiente/versão | Configuração local do Codex e documentação dos repositórios Jaci, Moara e Potira |
| Responsável | Engenharia VGX |
| Atualizado em | `2026-08-01` |

### Comportamento observado

As regras de registro, triagem, refinamento e acompanhamento de demandas estão
duplicadas entre `AGENTS.md`, a skill `vgx-development` e os documentos locais.
Moara e Jaci usam o catálogo `BL-NNNN`, enquanto Potira mantém múltiplos
prefixos e outro fluxo de arquivamento.

### Comportamento esperado

Uma skill global `vgx-doc-management` deve concentrar os invariantes
compartilhados e delegar a cada projeto somente caminhos, identificadores,
estados, matrizes de risco e templates locais.

### Impacto e abrangência

- Impacto: reduzir divergência entre políticas documentais usadas por agentes.
- Abrangência: configuração local do Codex e documentação de Jaci, Moara e Potira.
- Frequência: `sempre`.

### Passos de reprodução

1. Ler as instruções de gestão de demandas nos três projetos.
2. Comparar caminhos, identificadores, estados e gates.
3. Observar regras comuns duplicadas e convenções locais incompatíveis entre si.

### Evidências sanitizadas

- `AGENTS.md`
- `docs/domain/backlog/README.md`
- `~/.codex/skills/vgx-development/SKILL.md`
- Itens relacionados: Moara `BL-0030` e Potira `BL-0010`.

### Workaround

Ler e reconciliar manualmente todas as políticas a cada demanda.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Duplicação de processo documental entre projetos e skills |
| Domínio afetado | Governança de documentação e backlog |
| Regras de negócio afetadas | Gestão Obrigatória de Demandas e gate de aprovação |
| Risco de segurança | `não` — não altera autenticação ou autorização |
| Risco de LGPD | `não` — a política compartilhada preservará sanitização de evidências |
| Risco de isolamento por grupo | `não` — sem alteração em consultas ou dados da aplicação |
| Risco offline/sincronização | `não` — sem alteração no produto |
| Risco ao histórico financeiro | `não` — sem alteração em dados históricos |
| Risco à recorrência | `não` — sem alteração no domínio |
| Risco à separação template/execução | `não` — sem alteração no domínio |
| Dependências | Acesso de escrita a `~/.codex/skills` e coordenação com Moara `BL-0030` e Potira `BL-0010` |
| Duplicidades | Nenhuma |
| Responsável pela próxima etapa | Engenharia VGX |
| Próximo passo | Revisar e aprovar o refinamento antes da criação da skill |

## Acompanhamento até produção

- Documento refinado: [Refinamento BL-0012](../../tasks/BL-0012-vgx-doc-management.md)
- Implementação (commits/PRs): `80f8ba9` e `a1ab978` no Jaci; `c11064f` e
  `bd1b381` no Moara; `0c34a2e` e merge `14d753c` no Potira; skills globais
  instaladas localmente sem repositório Git
- Validações: `quick_validate.py` aprovado para `vgx-doc-management` e
  `vgx-development`; oito cenários documentais revisados; buscas estáticas e
  `git diff --check` aprovados nos três projetos
- Publicação: skill instalada em `~/.codex/skills`; adaptadores integrados às
  branches `develop` do Jaci (`a1ab978`), Moara (`bd1b381`) e Potira
  (`14d753c`) em `2026-08-01`
- Itens relacionados: Moara `BL-0030`; Potira `BL-0010`

### Impedimentos

- Nenhum.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-30 23:53 -03` | Codex | Item criado em `recebido` | Solicitação direta do usuário |
| `2026-07-30 23:53 -03` | Codex | Triagem concluída; item promovido a `pronto_para_refinamento` | Políticas e estruturas dos três projetos comparadas |
| `2026-07-30 23:53 -03` | Codex | Refinamento criado; estado alterado para `em_refinamento` | Escopo, fatias, cenários e validações documentados |
| `2026-07-30 23:53 -03` | Codex | Estado alterado para `pronto_para_implementacao` | Refinamento completo, aguardando aprovação explícita |
| `2026-07-31 00:07 -03` | Usuário/Codex | Refinamento aprovado; estado alterado para `em_implementacao` | Aprovação explícita recebida após apresentação dos três refinamentos |
| `2026-07-31 00:07 -03` | Codex | Estado alterado para `em_validacao` | Skill criada, integração concluída e validações documentais aprovadas |
| `2026-08-01 20:32 -03` | Usuário/Codex | Integração das branches autorizada e realizada | Adaptadores presentes em `develop` no Jaci (`a1ab978`), Moara (`bd1b381`) e Potira (`14d753c`) |
| `2026-08-01 20:32 -03` | Codex | Estado alterado para `concluido` | Validações aprovadas, skill instalada e publicação coordenada registrada |
