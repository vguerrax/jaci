# Refinamento — BL-0021 — API externa para gestão de execuções

## Rastreabilidade

- Item de backlog: [BL-0021](../backlog/items/BL-0021-api-integracoes-execucoes.md)
- Branch: `feature/BL-0021-api-integracoes-execucoes`
- Responsável pelo refinamento: Engenharia Jaci
- Estado do refinamento: `pronto_para_implementacao`
- Itens relacionados: [BL-0006](../backlog/items/BL-0006-integracoes-externas.md)
  e [BL-0011](../backlog/items/BL-0011-ampliar-cobertura-testes-ui.md)

## Objetivo e critérios de sucesso

### Objetivo

Disponibilizar uma API REST máquina a máquina, autenticada por chave vinculada
a um grupo, para consultar categorias e execuções, criar execuções avulsas e
editar o planejamento de execuções agendadas sem contornar regras de domínio,
isolamento, idempotência ou bloqueio otimista.

### Critérios de sucesso

1. Somente o proprietário cria e revoga múltiplas chaves nomeadas; o segredo é
   exibido uma vez, nunca persistido em texto puro e pode ter expiração.
2. Uma chave válida acessa exclusivamente dados do próprio grupo; recursos de
   outro grupo não são enumerados.
3. A API cria atomicamente uma execução avulsa com itens opcionais e permite
   editar somente cabeçalho e campos planejados de itens enquanto agendada.
4. Repetições de `POST` não criam duplicatas e versões obsoletas falham com
   `409`, sem sobrescrita ou persistência parcial.
5. Operações externas são atribuídas ao emissor e à chave, auditadas sem
   payload sensível e refletidas por WebSocket apenas depois da persistência.
6. Redis aplica limite distribuído por chave sem tornar as telas e APIs
   internas dependentes do limitador externo.
7. OpenAPI e documentação de integração descrevem autenticação, contratos,
   paginação, erros, idempotência, concorrência, rotação e exemplos seguros.

## Contrato HTTP v1

### Autenticação e escopo

- Prefixo base: `/api/v1`.
- Cabeçalho: `Authorization: Bearer <api-key>`.
- Formato opaco com prefixo público pesquisável e segredo aleatório de alta
  entropia; somente o hash do segredo é persistido e comparado em tempo
  constante.
- O grupo é derivado da chave. Nenhum payload, query ou path aceita `group_id`.
- Chave inexistente, malformada, revogada ou expirada retorna `401` genérico.
- Execução, item ou categoria fora do grupo retorna `404` para evitar
  enumeração.
- A permissão da v1 é fixa: leitura do planejamento do grupo e escrita do
  planejamento de execuções agendadas. Escopos configuráveis ficam fora.

### Recursos e operações

| Método e rota | Contrato |
| --- | --- |
| `GET /api/v1/executions` | Lista por cursor, `limit=50` e máximo `100`, ordenada por `scheduled_date DESC, id DESC`; filtros opcionais `status`, `scheduled_from` e `scheduled_to` |
| `GET /api/v1/executions/{execution_id}` | Retorna cabeçalho e itens planejados, inclusive para estados somente leitura |
| `POST /api/v1/executions` | Cria execução avulsa agendada com itens opcionais em uma transação |
| `PATCH /api/v1/executions/{execution_id}` | Altera nome, data e orçamento com `version` obrigatória |
| `POST /api/v1/executions/{execution_id}/items` | Adiciona item planejado a uma execução agendada |
| `PATCH /api/v1/executions/{execution_id}/items/{item_id}` | Altera campos planejados com `version` obrigatória |
| `DELETE /api/v1/executions/{execution_id}/items/{item_id}` | Remove item ainda removível, exigindo `version` atual |
| `GET /api/v1/categories` | Lista ID, nome, cor e ordenação das categorias do grupo |

### Representações e validações

- Execução: `id`, `name`, `scheduled_date`, `budget`, `status`, `version`,
  `created_at` e `items` no detalhe.
- Item: `id`, `execution_id`, `template_item_id`, `name`, `category_id`,
  `planned_quantity`, `notes`, `version` e `sort_order`.
- A API não expõe como contrato v1 quantidade comprada, valor unitário, local,
  conclusão ou totais financeiros por item.
- `scheduled_date` usa `YYYY-MM-DD`, interpretado por `parse_local_date` em
  `America/Sao_Paulo`, conforme ADR 0001.
- Nome de execução e item é obrigatório, normalizado e limitado a 150
  caracteres. Observação aceita `null` e até 255 caracteres.
- Orçamento aceita `null` para limpar ou número maior que zero; quantidade
  planejada é maior que zero com até três casas decimais.
- `PATCH` distingue campo omitido de `null`; `null` só limpa campos anuláveis.
- Cabeçalho usa `Execution.version`; item usa `ExecutionItem.version`. Cada
  mutação aceita incrementa exatamente a versão da entidade alterada.
- Escritas em execução `in_progress`, `completed` ou `cancelled` retornam
  `409`; não há reabertura implícita.
- Execuções vinculadas podem ter data e orçamento editados, mas não o nome.
  Itens vinculados mantêm o nome imutável; itens avulsos permanecem
  renomeáveis. Nenhuma alteração propaga ao template.

### Idempotência, erros e limite

- Todo `POST` exige `Idempotency-Key`, único por chave por 24 horas.
- A chave de idempotência armazena hash canônico da requisição, status e corpo
  mínimo da resposta. Repetição idêntica devolve a resposta original; mesma
  chave com outro conteúdo retorna `409 idempotency_key_reused`.
- Registros expirados são removidos de forma segura por limpeza incremental;
  não armazenam segredo nem cabeçalho de autorização.
- Erros usam envelope estável com `error.code`, `error.message`, detalhes
  sanitizados e `request_id`; códigos previstos: `401`, `404`, `409`, `422`,
  `429` e `503`.
- Redis aplica janela distribuída configurável, padrão de 60 requisições por
  minuto por chave. Excesso retorna `429` e `Retry-After`.
- Se Redis estiver indisponível, rotas externas retornam `503` antes de
  persistir; rotas HTML, offline e demais APIs internas continuam funcionando.

## Escopo

### Incluído

- Modelos e migração incremental para chaves, idempotência, auditoria e versão
  de execução, preservando registros existentes com versão inicial `1`.
- Emissão, listagem de metadados e revogação de chave pelo proprietário na
  página server-rendered do grupo, mobile-first e funcional sem JavaScript.
- Expiração opcional, `last_used_at`, revogação imediata e rotação por criação
  de nova chave seguida da revogação da anterior.
- Atribuição `created_by` ao proprietário emissor e auditoria de toda mutação
  com chave, emissor, grupo, ação, recurso, instante e `request_id`.
- Rotas, schemas Pydantic e serviços da API v1 definidos acima.
- Autorização derivada da chave e validação de categoria, execução e item no
  mesmo grupo.
- Criação atômica de execução e itens e concorrência explícita por versão.
- Redis, configuração, health/readiness aplicável e rate limit por chave.
- Broadcast complementar após commit, com ator de tipo integração e nome da
  chave, sem expor segredo.
- OpenAPI e guia de integração com exemplos sanitizados.
- Testes de modelo, migração, serviço, rota, segurança, isolamento,
  idempotência, concorrência e rate limit.
- Cenário Playwright futuro relacionado à BL-0011 e validação manual da UI de
  chaves nesta demanda.

### Excluído

- Criar execução a partir de template pela API.
- Iniciar, finalizar, cancelar, reabrir ou excluir execução.
- Escrever quantidade comprada, valor unitário, local ou conclusão do item.
- Expor dados financeiros calculados ou histórico de preços.
- Alterar templates, recorrência, sugestões de aprendizado ou categorias.
- Escopos customizáveis, chave por membro, OAuth, webhooks, SDKs ou API
  GraphQL.
- Sincronização automática do cliente externo, fila local do terceiro ou
  entrega garantida de eventos WebSocket.
- Notificações humanas para cada mutação externa.
- Criar infraestrutura Playwright ainda acompanhada pela BL-0011.

## Riscos e regras preservadas

- Regras de negócio afetadas: RN01/RN08 preservam snapshots e templates;
  RN02/RN05 bloqueiam estados não agendados; RN07 mantém criações avulsas sem
  recorrência; RN09/RN10/RN14 exigem escopo e conflito; RN12 mantém WebSocket
  complementar; ADR 0001 rege datas civis.
- Segurança e permissões: somente proprietário administra chaves; segredo é
  mostrado uma vez, hash é comparado em tempo constante, revogação e expiração
  são verificadas a cada chamada, rate limit é distribuído e logs são
  sanitizados.
- LGPD: respostas expõem somente campos necessários ao planejamento;
  idempotência tem retenção de 24 horas e auditoria não guarda payload,
  segredo, Authorization ou valores de compra.
- Isolamento por grupo: o grupo vem exclusivamente da chave; todos os
  carregamentos incluem `group_id` e relações item/execução; IDs externos nunca
  concedem acesso e falhas entre grupos são `404`.
- Offline e sincronização: a API não entra na fila local do navegador;
  versões detectam estado obsoleto, WebSocket só acelera a visualização e o
  snapshot/API remota continuam responsáveis pela reconciliação.
- Histórico financeiro: estados operacionais e dados comprados são somente
  leitura e não entram na representação pública; execuções não agendadas são
  imutáveis pela integração.
- Recorrência: a API cria somente avulsas, não finaliza compras nem chama
  geração de próximo ciclo; editar snapshot vinculado não muda calendário do
  template.
- Separação entre template e execução: nome de execução/item vinculado segue
  as invariantes existentes; itens adicionados externamente pertencem somente
  à execução e nunca são incorporados automaticamente.
- Confiabilidade: persistência e auditoria são atômicas; falha de WebSocket não
  reverte commit, e indisponibilidade do rate limiter falha antes da mutação.

## Plano de implementação

### Etapa 1 — Persistir identidade, concorrência e rastreabilidade

#### Ticket 1.1 — Criar a fundação segura da integração

##### Fatia 1.1.1 — Modelos, migração e contratos de domínio

- Ordem: `1`
- Objetivo da fatia: criar primeiro os testes de modelos e migração e então
  entregar chaves com segredo protegido, idempotência, auditoria e versão de
  execução sem alterar o comportamento das rotas existentes.
- Dependências: aprovação explícita deste refinamento versionado.
- Arquivos esperados:
  - `tests/test_external_api_models.py`
  - `tests/test_database_operations.py`
  - `app/models/api_integration.py`
  - `app/models/execution.py`
  - `app/models/__init__.py`
  - `migrations/versions/*_external_api_foundation.py`
- Validações focadas:
  - `venv/bin/alembic upgrade head`
  - `timeout 180 venv/bin/pytest tests/test_external_api_models.py tests/test_database_operations.py`
  - compilação e lint dos módulos alterados
- Documentação a atualizar:
  - item e refinamento `BL-0021`

### Etapa 2 — Administrar e autenticar chaves

#### Ticket 2.1 — Entregar ciclo de vida e proteção operacional

##### Fatia 2.1.1 — Serviço, UI do proprietário, Redis e autenticação

- Ordem: `2`
- Objetivo da fatia: escrever contratos de segurança e rotas HTML antes de
  implementar emissão única, listagem, expiração, revogação, autenticação
  Bearer, atualização de último uso e rate limit distribuído.
- Dependências: fatia 1.1.1; Redis disponível na configuração de teste.
- Arquivos esperados:
  - `tests/test_api_key_management.py`
  - `tests/test_external_api_auth.py`
  - `app/services/api_key_service.py`
  - `app/dependencies.py`
  - `app/routers/groups.py`
  - `app/templates/pages/groups/detail.html`
  - `app/config.py`, `.env.example`, `docker-compose.yml`, `requirements.txt`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_api_key_management.py tests/test_external_api_auth.py`
  - validação manual mobile e sem JavaScript da criação, cópia única e
    revogação
  - confirmar `Cache-Control: no-store` na resposta que apresenta o segredo
- Documentação a atualizar:
  - guia de configuração e item/refinamento `BL-0021`

### Etapa 3 — Publicar o contrato de execuções

#### Ticket 3.1 — Entregar API v1 idempotente e isolada

##### Fatia 3.1.1 — Serviços, endpoints, eventos e documentação

- Ordem: `3`
- Objetivo da fatia: escrever contratos HTTP e de domínio antes de implementar
  listagem, detalhe, categorias, criação atômica, alterações versionadas,
  auditoria, eventos pós-commit e documentação OpenAPI.
- Dependências: fatias 1.1.1 e 2.1.1.
- Arquivos esperados:
  - `tests/test_external_executions_api.py`
  - `tests/test_external_api_idempotency.py`
  - `tests/test_external_api_rate_limit.py`
  - `app/schemas/external_api.py`
  - `app/services/external_api_service.py`
  - `app/routers/external_api.py`
  - `app/main.py`
  - `docs/api/external-v1.md`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_external_executions_api.py tests/test_external_api_idempotency.py tests/test_external_api_rate_limit.py`
  - validar schema OpenAPI e exemplos do guia sem credenciais reais
  - confirmar que falha simulada de WebSocket não reverte persistência
- Documentação a atualizar:
  - `docs/api/external-v1.md`, `tests/README.md`, item e refinamento `BL-0021`

## Cenários TDD

Estes cenários devem ser escritos antes da implementação da fatia
correspondente, somente depois da aprovação explícita deste refinamento.

1. A migração cria tabelas, índices e constraints e inicializa
   `Execution.version=1` sem alterar execuções ou itens existentes.
2. O proprietário cria duas chaves nomeadas, recebe cada segredo uma única vez
   e a persistência contém somente prefixo e hash; membro recebe rejeição.
3. Chave válida autentica no grupo; chave malformada, desconhecida, revogada ou
   expirada retorna o mesmo `401` sem revelar motivo ou existência.
4. Revogar uma chave invalida a chamada seguinte, preserva metadados e
   auditorias, e não afeta as demais chaves do grupo.
5. A resposta que mostra o segredo usa `no-store`; listagem, HTML posterior,
   banco, logs e auditoria nunca contêm o segredo.
6. Cada chave possui contador Redis independente; a chamada acima do limite
   retorna `429` com `Retry-After`, e Redis indisponível produz `503` sem
   executar serviço ou persistência.
7. `GET /executions` respeita cursor, limite, ordenação e filtros e nunca
   retorna execução de outro grupo.
8. `GET /executions/{id}` retorna somente cabeçalho e campos planejados; ID de
   outro grupo ou inexistente retorna `404` indistinguível.
9. `GET /categories` retorna somente categorias do grupo na ordenação definida.
10. `POST /executions` com data, orçamento e itens válidos cria uma execução
    avulsa agendada em uma única transação, atribui `created_by` ao emissor e
    registra auditoria da chave.
11. Data civil é persistida no instante UTC correspondente à meia-noite em
    `America/Sao_Paulo`; nome, orçamento, quantidade, observação ou categoria
    inválida retorna `422` sem registro parcial.
12. A mesma `Idempotency-Key` e payload devolve a resposta original sem nova
    execução/auditoria; mesma chave com payload diferente retorna `409`.
13. `PATCH` de execução avulsa agendada com versão atual altera somente campos
    presentes e incrementa a versão uma vez; versão obsoleta retorna `409` com
    estado remoto sanitizado.
14. Execução vinculada aceita data/orçamento, mas rejeita nome diferente sem
    alterar template ou snapshot; criação por template não possui endpoint.
15. Adicionar item com `POST` é idempotente, valida categoria do grupo e não
    altera template nem cria sugestão automática.
16. Alterar item com versão atual atualiza campos planejados e incrementa a
    versão; versão obsoleta ou categoria externa retorna conflito/validação sem
    sobrescrita.
17. Item vinculado rejeita nome diferente e aceita quantidade, categoria e
    observação; item avulso continua renomeável.
18. Remoção exige versão atual e respeita as regras de mutabilidade sem apagar
    item comprado ou histórico.
19. Qualquer escrita externa em execução em andamento, finalizada ou cancelada
    retorna `409` e não altera cabeçalho, itens, versões ou auditoria de
    sucesso.
20. ID de execução com item de outra execução ou grupo retorna `404` sem vazar
    a relação real.
21. Auditoria registra chave, emissor, grupo, ação, recurso e `request_id` na
    mesma transação da mutação, sem payload, Authorization ou valores de compra.
22. Broadcast ocorre depois do commit e identifica uma integração sem segredo;
    falha do WebSocket mantém resposta e persistência bem-sucedidas.
23. Rotas internas HTML/offline continuam funcionando quando Redis está
    indisponível e não aceitam API key como substituto de sessão humana.
24. OpenAPI declara HTTP Bearer, schemas e respostas da v1 e não publica rotas
    HTML de gestão de chave como API externa.

### Contratos de etapas futuras

- Não haverá `xfail(strict=True)` no escopo executável das três fatias; cada
  fatia começa por seus testes vermelhos e termina sem contratos pendentes.
- A BL-0011 deve cobrir futuramente em Playwright: proprietário abre o grupo em
  viewport móvel, cria chave com expiração opcional, vê e copia o segredo uma
  única vez, volta à listagem sem reencontrá-lo e revoga a integração; membro
  não vê controles de chave.

## Estratégia de validação

### Por fatia

- Escrever e executar os contratos focados antes do código de produção.
- Aplicar migração em banco vazio e atualizado; validar downgrade estrutural
  sem apagar dados históricos existentes.
- Executar lint/compilação dos módulos alterados e `git diff --check`.
- Usar Redis isolado nos testes de limite e nunca depender de serviço externo
  nos testes de domínio.
- Revisar logs e respostas para ausência de segredo, Authorization e dados de
  outro grupo.
- Atualizar contratos, matriz de testes, progresso e histórico na mesma fatia.
- Executar `venv/bin/graphify update .` depois das mudanças de código.

### Validação manual

1. Em viewport móvel e sem JavaScript, entrar como proprietário, criar chave
   nomeada sem expiração e confirmar exibição única com instrução de cópia.
2. Recarregar e voltar à tela do grupo, confirmar apenas prefixo, criação,
   expiração, último uso e estado, sem o segredo.
3. Criar uma segunda chave com expiração, usar ambas na API, revogar a primeira
   e confirmar que somente ela recebe `401`.
4. Entrar como membro e confirmar ausência dos controles; adulterar o POST e
   confirmar rejeição sem criar ou revogar chave.
5. Com cliente HTTP, criar execução com item, repetir a chave idempotente,
   consultar detalhe, alterar cabeçalho/item com versões e observar conflitos
   explícitos para versões antigas.
6. Tentar IDs de outro grupo e confirmar `404` sem detalhes; inspecionar banco
   e logs para ausência de segredo e payload sensível.
7. Abrir a execução no navegador, realizar mutação externa e confirmar
   atualização visual; derrubar WebSocket e confirmar que nova mutação continua
   persistida e aparece após recarregar.
8. Indisponibilizar Redis, confirmar `503` na API externa sem mutação e validar
   que navegação e API offline internas continuam operacionais.

### Regressão total

Executar após as três fatias e sem `xfail(strict=True)` da demanda:

- `venv/bin/alembic upgrade head`
- `timeout 300 venv/bin/pytest`
- validação do OpenAPI e do guia com exemplos sanitizados
- Playwright: infraestrutura ausente; manter cobertura futura na BL-0011 e
  executar a validação manual definida acima

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 / Ticket 1.1 — Fundação | `0/1` | `1` | Pendente |
| Etapa 2 / Ticket 2.1 — Chaves e proteção | `0/1` | `1` | Pendente |
| Etapa 3 / Ticket 3.1 — API v1 | `0/1` | `1` | Pendente |

## Fechamento

- Commits/PRs: ainda não iniciados.
- Resultado das validações focadas: ainda não iniciadas.
- Resultado da validação manual: ainda não iniciada.
- Resultado da regressão total: ainda não iniciado.
- `xfail(strict=True)` pendentes no escopo: nenhum planejado.
- Documentação atualizada: item, índice e este refinamento; guia da API será
  criado durante a implementação.
