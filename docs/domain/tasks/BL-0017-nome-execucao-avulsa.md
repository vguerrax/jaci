# Refinamento — BL-0017 — Nome da execução avulsa

## Rastreabilidade

- Item de backlog: [BL-0017](../backlog/items/BL-0017-nome-execucao-avulsa.md)
- Branch: `feature/BL-0017-nome-execucao-avulsa`
- Responsável pelo refinamento: Engenharia Jaci
- Estado do refinamento: `concluido`
- Item relacionado: `BL-0011`, para futura cobertura Playwright
- Decisões de produto: nome opcional com fallback "Compra Avulsa"; somente
  execução sem template (`template_id IS NULL`) pode ser nomeada ou renomeada.
- Aprovação de implementação: emitida explicitamente em `2026-08-05`, depois
  do commit documental `e76c9a1`.

## Objetivo e critérios de sucesso

### Objetivo

Permitir que compras avulsas sem lista sejam identificadas por um nome próprio
desde a criação e durante a edição agendada, sem permitir que execuções
vinculadas a templates sejam renomeadas nem alterar contratos offline
existentes.

### Critérios de sucesso

1. O formulário sem lista oferece nome opcional, limitado a 150 caracteres;
   valor ausente, vazio ou composto por espaços usa "Compra Avulsa".
2. O nome informado é normalizado, persistido e exibido no detalhe, agenda,
   dashboard, notificações e snapshot offline pelos contratos existentes.
3. Apenas execução agendada com `template_id IS NULL` permite alterar o nome,
   tanto online quanto pela fila offline.
4. Execução vinculada a template não oferece controle editável de nome; data e
   orçamento permanecem editáveis enquanto ela estiver agendada.
5. Compra extra baseada em lista, ainda que tenha `is_standalone=true`, não
   pode ser renomeada porque mantém `template_id`.
6. Tentativa adulterada de renomear execução vinculada falha no servidor sem
   persistência parcial; a API offline responde `422`.
7. Nomes históricos já divergentes em execuções vinculadas são preservados,
   mas ficam bloqueados para novas alterações.
8. Criação baseada em template ignora nome enviado pelo cliente e continua
   copiando o nome do template.

## Escopo

### Incluído

- Campo de nome opcional na criação server-rendered de compra sem lista.
- Normalização, fallback e limite do nome no serviço de criação avulsa.
- Restrição de renomeação centralizada no serviço de edição agendada.
- Apresentação editável do nome somente para execução sem template; execução
  vinculada apresenta o nome como informação não editável.
- Compatibilidade do formulário e da operação `UPDATE_EXECUTION` para que
  execuções vinculadas continuem alterando data e orçamento online e offline.
- Rejeição no servidor de parâmetros adulterados, preservando atomicidade.
- Atualização da documentação de edição agendada e da rastreabilidade de testes
  depois da implementação.
- Cenários futuros de navegador registrados para a BL-0011, sem criação de
  infraestrutura Playwright nesta demanda.

### Excluído

- Alterar nomes de templates ou propagar nomes de execução para templates.
- Renomear execuções vinculadas, inclusive compras extras com
  `is_standalone=true`.
- Reescrever nomes históricos ou migrar dados existentes.
- Alterar recorrência, status, orçamento, eventos WebSocket, esquema do banco,
  modelo `Execution` ou formato do payload offline.
- Criar compra offline, infraestrutura Playwright ou arquivos em `tests/ui`.

## Riscos e regras preservadas

- Regras de negócio afetadas: o nome passa a ser personalizável exclusivamente
  quando `template_id IS NULL`; status diferentes de `scheduled` continuam
  imutáveis pela edição existente.
- Segurança e permissões: rotas mantêm autenticação e carregamento autorizado;
  a regra no serviço impede contorno por POST ou sincronização adulterados.
- LGPD: o campo textual já existe, permanece limitado a 150 caracteres e não
  será incluído em novos logs ou evidências.
- Isolamento por grupo: criação continua vinculada ao grupo ativo e edição usa
  `get_execution_by_id`, que valida participação do usuário no grupo.
- Offline e sincronização: `UPDATE_EXECUTION` conserva o wire shape atual. Para
  execução vinculada, envia o nome corrente sem torná-lo editável; divergência
  recebida pelo servidor retorna `422` sem salvar data ou orçamento.
- Histórico financeiro: nenhuma migração, total, preço ou registro histórico é
  alterado; nomes existentes são preservados.
- Recorrência: `is_standalone` conserva sua semântica atual. A possibilidade de
  renomear depende apenas da ausência de template.
- Separação entre template e execução: criação vinculada copia o nome do
  template; nenhum fluxo modifica o template, e a execução vinculada não pode
  receber novo nome.

## Plano de implementação

### Etapa 1 — Nome exclusivo para compra sem lista

#### Ticket 1.1 — Criação e edição coerentes online/offline

##### Fatia 1.1.1 — Contratos TDD e implementação completa

- Ordem: `1`
- Objetivo da fatia: escrever os contratos executáveis de todo o escopo e
  entregar criação nomeada, restrição de edição e compatibilidade offline numa
  única unidade coerente.
- Dependências: aprovação explícita deste refinamento versionado.
- Arquivos esperados:
  - `tests/test_scheduled_execution_editing.py`
  - `tests/test_offline_cache.py`
  - `app/services/execution_service.py`
  - `app/routers/executions.py`
  - `app/templates/pages/executions/create.html`
  - `app/templates/pages/executions/in_progress.html`
  - `docs/domain/scheduled-execution-editing.md`
  - `tests/README.md`
  - este refinamento e o item `BL-0017`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_scheduled_execution_editing.py tests/test_offline_cache.py`
  - `timeout 180 env PYTHONPATH=. venv/bin/pylint app/services/execution_service.py app/routers/executions.py app/routers/offline.py --errors-only`
  - validar manualmente criação e edição online/offline em viewport móvel
- Documentação a atualizar:
  - `docs/domain/scheduled-execution-editing.md`
  - `tests/README.md`
  - este refinamento e o item `BL-0017`

## Cenários TDD

Estes cenários devem ser escritos como testes antes da implementação, depois da
aprovação explícita deste refinamento.

1. Dada criação sem template, nome informado é aparado e persistido na execução.
2. Dado nome ausente, vazio ou composto por espaços, a criação sem template
   persiste o fallback "Compra Avulsa".
3. Dado nome com mais de 150 caracteres, a criação falha sem persistência.
4. Dado POST sem template com nome válido, a rota cria a execução nomeada e
   redireciona para seu detalhe; erro reapresenta valores e mensagem acessível.
5. Dado POST com template e parâmetro de nome adulterado, a execução conserva o
   nome copiado do template.
6. Dada execução agendada sem template, edição online ou offline altera nome,
   data e orçamento e mantém notificação e atualização visual existentes.
7. Dada execução agendada vinculada, edição com o mesmo nome altera somente data
   e orçamento; o formulário não expõe controle editável de nome.
8. Dada execução vinculada e tentativa de mudar o nome, o serviço rejeita a
   operação sem salvar nenhum campo; a rota HTML não persiste e a API offline
   responde `422`.
9. Dada compra extra com template e `is_standalone=true`, a mesma tentativa de
   renomeação é rejeitada.
10. Dada execução vinculada cujo nome histórico já diverge do template, editar
    data ou orçamento preserva esse nome e continua impedindo nova renomeação.
11. Dado status `in_progress`, `completed` ou `cancelled`, a edição continua
    rejeitada independentemente de a execução possuir template.
12. Dada a interface de criação/edição, o campo de nome possui rótulo, limite e
    obrigatoriedade coerentes e aparece como editável somente sem template.

### Contratos de etapas futuras

- Não há `xfail(strict=True)` planejado: a fatia única implementa todo o
  escopo executável desta demanda.
- A BL-0011 deve futuramente cobrir em Playwright: criação avulsa nomeada e com
  fallback; edição avulsa online/offline; ausência de campo editável em compra
  vinculada; manutenção de data e orçamento da compra vinculada.

## Estratégia de validação

### Por fatia

- Escrever todos os contratos acima antes de alterar serviço, rota ou template.
- Executar testes de serviço, rota, renderização e sincronização offline.
- Executar lint dos módulos Python tocados; indisponibilidade do `pylint` deve
  ser registrada como limitação ambiental.
- Confirmar que não houve mudança de modelo, migração, payload offline ou
  arquivo em `tests/ui`.
- Atualizar documentação, backlog e progresso antes do commit da fatia.

### Validação manual

1. Em viewport móvel, criar compra sem lista com nome e confirmar o nome no
   detalhe; repetir sem nome e confirmar "Compra Avulsa".
2. Criar compra a partir de lista e confirmar ausência do campo de nome e uso do
   nome da lista.
3. Em execução avulsa agendada, editar nome, data e orçamento online e confirmar
   a atualização visual.
4. Repetir a edição avulsa sem conexão, confirmar estado local, fila e
   reconciliação após reconectar.
5. Em execução vinculada agendada, confirmar nome não editável e alteração de
   data/orçamento online e offline sem mudar o nome.
6. Adulterar o nome enviado para execução vinculada e confirmar rejeição sem
   alteração parcial.

### Regressão total

Como a fatia única fecha todo o ticket, executar ao concluí-la e sem
`xfail(strict=True)` deste escopo:

- `venv/bin/alembic upgrade head`
- `timeout 240 venv/bin/pytest`
- UI Playwright: infraestrutura ausente no Jaci; manter os quatro cenários
  futuros na BL-0011 e registrar validação manual.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 / Ticket 1.1 — Nome exclusivo sem lista | `1/1` | `0` | Concluído |

## Fechamento

- Commits/PRs: fatia 1.1.1 `4f91170`; branch
  `feature/BL-0017-nome-execucao-avulsa`.
- Resultado das validações focadas: 56 testes aprovados em
  `tests/test_scheduled_execution_editing.py` e `tests/test_offline_cache.py`;
  57 testes ampliados de agenda, dashboard, recorrência, templates e aprendizado
  aprovados; módulos Python compilados. O `pylint` não está instalado no venv.
- Resultado da validação manual: o aceite da versão `1.2.0` em produção foi
  informado pelo usuário; renderização, condicionais da interface e contratos
  offline possuem cobertura automatizada.
- Resultado da regressão total: migrações no head; 225 testes aprovados e 5
  `xfail` legados fora do escopo.
- `xfail(strict=True)` pendentes no escopo: nenhum.
- Documentação atualizada: regra de edição agendada, matriz de testes, item,
  índice e este refinamento; grafo atualizado após a implementação.
- Publicação: produção, versão `1.2.0`, tag `v1.2.0` no commit `7364294`,
  publicada em `2026-08-05`.
