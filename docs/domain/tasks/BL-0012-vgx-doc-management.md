# Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX

## Rastreabilidade

- Item de backlog: [BL-0012](../backlog/items/BL-0012-vgx-doc-management.md)
- Branch: `feature/BL-0012-vgx-doc-management`
- Responsável pelo refinamento: Engenharia VGX
- Estado do refinamento: `pronto_para_implementacao`
- Demandas coordenadas: Moara `BL-0030`; Potira `BL-0010`

## Objetivo e critérios de sucesso

### Objetivo

Disponibilizar a skill global `vgx-doc-management` como contrato comum de
registro, triagem, refinamento e acompanhamento de demandas, preservando os
perfis documentais próprios de Jaci, Moara e Potira.

### Critérios de sucesso

1. A skill é autodetectável em `~/.codex/skills/vgx-doc-management` e passa na
   validação oficial de skills.
2. `vgx-development` delega a gestão documental à nova skill sem perder o gate
   entre refinamento e implementação.
3. Os três projetos exigem a skill e descrevem somente seus adaptadores locais,
   sem normalizar prefixos, estados ou diretórios.
4. Nenhuma alteração de aplicação, migração, template de UI ou teste executável
   integra a demanda.

## Escopo

### Incluído

- Criar `vgx-doc-management` com política comum e metadados de interface.
- Integrar `vgx-development` por delegação explícita.
- Adaptar a política de agentes e a referência de automação documental do Jaci.
- Coordenar os refinamentos locais de Moara `BL-0030` e Potira `BL-0010`.

### Excluído

- Uniformizar os catálogos ou migrar itens históricos entre projetos.
- Alterar regras de domínio, código, testes executáveis ou pipelines.
- Criar um repositório separado para distribuir a skill.
- Integrar ou remover branches sem solicitação explícita.

## Riscos e regras preservadas

- Regras de negócio afetadas: somente a Gestão Obrigatória de Demandas.
- Segurança e permissões: solicitar autorização para escrita em
  `~/.codex/skills`; não ampliar permissões da aplicação.
- LGPD: preservar a proibição de segredos e dados pessoais nas evidências.
- Isolamento por grupo: `N/A` — nenhuma consulta ou mutação de dados.
- Offline e sincronização: `N/A` — nenhuma alteração no produto.
- Histórico financeiro: preservar registros, estados, índices e histórico das
  demandas existentes.
- Recorrência: `N/A` — nenhuma alteração no domínio.
- Separação entre template e execução: `N/A` — nenhuma alteração no domínio.

## Plano de implementação

### Etapa 1 — Skill compartilhada

#### Ticket 1.1 — Criar o contrato documental comum

##### Fatia 1.1.1 — Inicializar e preencher `vgx-doc-management`

- Ordem: `1`
- Objetivo da fatia: criar a skill global com fluxo comum, referência detalhada
  e metadados de interface.
- Dependências: aprovação explícita deste refinamento.
- Arquivos esperados:
  - `~/.codex/skills/vgx-doc-management/SKILL.md`
  - `~/.codex/skills/vgx-doc-management/references/backlog-lifecycle.md`
  - `~/.codex/skills/vgx-doc-management/agents/openai.yaml`
- Validações focadas:
  - `quick_validate.py ~/.codex/skills/vgx-doc-management`
  - revisão dos cenários documentais definidos abaixo
- Documentação a atualizar:
  - este refinamento e o item `BL-0012`

### Etapa 2 — Composição entre skills

#### Ticket 2.1 — Delegar documentação a `vgx-doc-management`

##### Fatia 2.1.1 — Integrar `vgx-development`

- Ordem: `2`
- Objetivo da fatia: manter desenvolvimento, TDD e validação em
  `vgx-development`, delegando registro, triagem e refinamento documental.
- Dependências: fatia 1.1.1.
- Arquivos esperados:
  - `~/.codex/skills/vgx-development/SKILL.md`
  - `~/.codex/skills/vgx-development/agents/openai.yaml`
- Validações focadas:
  - `quick_validate.py ~/.codex/skills/vgx-development`
  - busca por regras duplicadas ou contraditórias entre as duas skills
- Documentação a atualizar:
  - este refinamento e o item `BL-0012`

### Etapa 3 — Adaptadores dos projetos

#### Ticket 3.1 — Integrar Jaci e coordenar Moara e Potira

##### Fatia 3.1.1 — Referenciar a skill no Jaci

- Ordem: `3`
- Objetivo da fatia: substituir instruções duplicadas para agentes por uma
  referência obrigatória à skill e pelo perfil local do Jaci.
- Dependências: fatias 1.1.1 e 2.1.1.
- Arquivos esperados:
  - `AGENTS.md`
  - `docs/domain/backlog/README.md`
- Validações focadas:
  - busca estática por `vgx-doc-management`
  - `git diff --check`
- Documentação a atualizar:
  - item e refinamento `BL-0012`

##### Fatia 3.1.2 — Validar os adaptadores coordenados

- Ordem: `4`
- Objetivo da fatia: confirmar que Moara `BL-0030` e Potira `BL-0010`
  preservam caminhos, identificadores, estados, riscos e arquivamento locais.
- Dependências: refinamentos locais aprovados.
- Arquivos esperados:
  - documentação prevista nos refinamentos de Moara e Potira
- Validações focadas:
  - busca estática nos três `AGENTS.md`
  - `git diff --check` em cada repositório
- Documentação a atualizar:
  - os três itens e refinamentos coordenados

## Cenários TDD

Como esta demanda altera somente instruções e metadados, os contratos são
cenários de comportamento documental e não testes executáveis.

1. Dada uma demanda nova no Jaci ou Moara, a skill identifica o catálogo
   `BL-NNNN`, reserva o próximo ID sem reutilização e separa item e refinamento.
2. Dada uma demanda no Potira, a skill preserva o prefixo e o fluxo local em vez
   de impor `BL-NNNN` ou os estados de Jaci.
3. Dada uma mudança entre repositórios, cada projeto recebe ID e branch próprios
   e mantém referências aos itens coordenados.
4. Dado um pedido apenas de registro, triagem ou refinamento, nenhum teste
   executável, código, migração, template ou ativo é alterado.
5. Dado um refinamento completo sem aprovação explícita, a skill interrompe
   antes da implementação.
6. Dada uma evidência com segredo ou dado pessoal, a skill registra somente um
   identificador sanitizado e não copia o conteúdo.
7. Dada uma implementação validada mas ainda não publicada, a demanda permanece
   fora do estado terminal.
8. Dada uma skill `vgx-development` acionada para demanda ainda não refinada,
   ela delega o fluxo documental a `vgx-doc-management`.

### Contratos de etapas futuras

Não há contratos executáveis futuros neste escopo.

## Estratégia de validação

### Por fatia

- Executar o validador oficial nas duas skills.
- Revisar manualmente os oito cenários documentais.
- Executar buscas estáticas nas referências dos projetos.
- Executar `git diff --check` nos três repositórios.
- Não executar migrações ou testes da aplicação por ausência de alteração
  executável.

### Validação manual

1. Simular a entrada de uma demanda em cada perfil sem criar arquivos.
2. Confirmar que os caminhos, IDs, estados e gates selecionados são os locais.
3. Confirmar que o fluxo interrompe antes de código quando falta aprovação.

### Regressão total

Não se aplica às aplicações. A regressão desta demanda é a validação estrutural
das duas skills e a revisão estática das três integrações.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 — Skill compartilhada | `0/1` | `1` | Aguardando aprovação |
| Etapa 2 — Composição entre skills | `0/1` | `1` | Aguardando aprovação |
| Etapa 3 — Adaptadores dos projetos | `0/2` | `2` | Aguardando aprovação |

## Fechamento

- Commits/PRs: ainda não iniciados
- Resultado das validações focadas: ainda não iniciado
- Resultado da validação manual: ainda não iniciado
- Resultado da regressão total: `N/A` para as aplicações
- `xfail(strict=True)` pendentes no escopo: nenhum
- Documentação atualizada: item e refinamento `BL-0012`
