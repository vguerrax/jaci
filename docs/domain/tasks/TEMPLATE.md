# Refinamento — BL-NNNN — Título

> Crie este documento somente quando o item estiver
> `pronto_para_refinamento`. Adicione links recíprocos e mantenha a
> especificação técnica aqui, não no resumo do backlog.

## Rastreabilidade

- Item de backlog: `<link para docs/domain/backlog/items/BL-NNNN-slug.md>`
- Branch: `feature/BL-NNNN-slug`
- Responsável pelo refinamento: `<nome ou equipe>`
- Estado do refinamento: `<em_refinamento | pronto_para_implementacao | concluido>`

## Objetivo e critérios de sucesso

### Objetivo

_Descreva o resultado de negócio ou técnico._

### Critérios de sucesso

1. `<critério observável e verificável>`
2. `<critério observável e verificável>`

## Escopo

### Incluído

- `<comportamento, domínio ou entrega>`

### Excluído

- `<limite explícito ou trabalho futuro>`

## Riscos e regras preservadas

- Regras de negócio afetadas: `<identificadores e efeito esperado>`
- Segurança e permissões: `<riscos e controles>`
- LGPD: `<riscos e controles>`
- Isolamento por grupo: `<riscos e controles>`
- Offline e sincronização: `<riscos e controles>`
- Histórico financeiro: `<riscos e controles>`
- Recorrência: `<riscos e controles>`
- Separação entre template e execução: `<riscos e controles>`

Use `N/A` com justificativa quando uma dimensão não se aplicar.

## Plano de implementação

As etapas, tickets e fatias devem ser pequenas, ordenadas e verificáveis.

### Etapa 1 — `<resultado da etapa>`

#### Ticket 1.1 — `<resultado do ticket>`

##### Fatia 1.1.1 — `<resultado pequeno e verificável>`

- Ordem: `1`
- Objetivo da fatia: `<resultado>`
- Dependências: `<fatias, decisões, sistemas ou nenhuma>`
- Arquivos esperados:
  - `<caminho>`
- Validações focadas:
  - `<comando ou verificação>`
- Documentação a atualizar:
  - `<caminho>`

Repita para todas as fatias e mantenha somente uma em implementação por vez.

## Cenários TDD

Estes cenários devem ser escritos como testes antes da implementação, depois da
aprovação do refinamento.

1. `<dado um contexto, quando ocorrer uma ação, então o resultado esperado>`
2. `<cenário de erro, autorização, isolamento ou limite relevante>`

### Contratos de etapas futuras

- `<teste e fatia futura correspondente>`

Em migrações ou refatorações, contratos futuros usam `xfail(strict=True)` até a
fatia correspondente. Se não houver, registre isso explicitamente.

## Estratégia de validação

### Por fatia

- Aplicar migrações quando houver mudança de banco.
- Executar lint dos arquivos alterados, quando configurado.
- Executar testes unitários, integração, contratos e UI diretamente relacionados.
- Validar manualmente fluxos críticos, quando aplicável.
- Atualizar regras e documentação afetadas.

### Validação manual

1. `<pré-condição, ação e resultado esperado>`

### Regressão total

Executar somente quando todas as fatias do escopo estiverem concluídas e não
houver `xfail(strict=True)` pendente para ele.

- `<comando de regressão Python>`
- `<comando de UI, quando aplicável>`

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| `<etapa ou ticket>` | `0/N` | `N` | `Pendente` |

## Fechamento

- Commits/PRs: `<links>`
- Resultado das validações focadas: `<resumo>`
- Resultado da validação manual: `<resumo ou N/A justificado>`
- Resultado da regressão total: `<resumo>`
- `xfail(strict=True)` pendentes no escopo: `<nenhum ou lista>`
- Documentação atualizada: `<links>`
