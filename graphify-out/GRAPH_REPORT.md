# Graph Report - jaci  (2026-08-03)

## Corpus Check
- 124 files · ~124,531 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1543 nodes · 3912 edges · 84 communities (80 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 230 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4c897ae0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_user
- offline-cache.js
- executions.py
- Execution
- test_database_operations.py
- User
- ExecutionStatus
- Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX
- tupa_auth_service.py
- categories.py
- AGENTS.md
- groups.py
- auth.py
- templates.py
- group_service.py
- template_service.py
- template_learning_service.py
- 🌙 Jaci
- backlog/README.md
- Refinamento — BL-0013 — Busca e padronização das telas de itens
- user-flows.md
- Refinamento — BL-NNNN — Título
- Regras de negócio críticas
- datetime.py
- Fundação PWA e Offline
- auth_service.py
- ConnectionManager
- item-filter.js
- Backlog de produção
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- sync_center
- service-worker.js
- loading-indicator.js
- sync-status.js
- format_local_date
- Pricipais Entidades
- Aprendizado contínuo dos templates
- read
- 0001 - Tratamento de datas e timezone
- 0002 - Backup automático do PostgreSQL
- Tela Inicial Operacional
- Backups do PostgreSQL
- execution_ws_handler
- privacy_policy
- Estratégia de Banco de Dados
- Backlog legado do Jaci
- Edição de execuções agendadas
- FL-03 — Geração de Execução
- FL-04 — Execução da Compra
- FL-08 — Consulta da Agenda e Histórico
- FL-09 — Operação Offline
- FL-06 — Aprendizado do Template
- test_auth_pages.py
- ensure_schema_compatibility
- FL-01 — Primeiro Acesso e Onboarding
- FL-07 — Gestão de Grupos
- run.py
- docker-entrypoint.sh
- overview.md
- backup_database.sh
- app/__init__.py
- publish.sh

## God Nodes (most connected - your core abstractions)
1. `User` - 144 edges
2. `make_user()` - 83 edges
3. `make_group()` - 82 edges
4. `create_template()` - 68 edges
5. `create_execution_from_template()` - 67 edges
6. `Execution` - 61 edges
7. `ExecutionItem` - 49 edges
8. `add_item_to_template()` - 48 edges
9. `Group` - 44 edges
10. `finalize_execution()` - 36 edges

## Surprising Connections (you probably didn't know these)
- `test_cloud_postgres_urls_are_normalized_to_psycopg_driver()` --calls--> `Settings`  [EXTRACTED]
  tests/test_database_operations.py → app/config.py
- `test_debug_environment_disables_secure_cookies_for_local_http()` --calls--> `Settings`  [EXTRACTED]
  tests/test_database_operations.py → app/config.py
- `test_production_environment_keeps_secure_cookies()` --calls--> `Settings`  [EXTRACTED]
  tests/test_database_operations.py → app/config.py
- `test_release_environment_name_disables_debug()` --calls--> `Settings`  [EXTRACTED]
  tests/test_database_operations.py → app/config.py
- `test_database_engine_uses_sqlite_specific_connection_options()` --calls--> `create_database_engine()`  [EXTRACTED]
  tests/test_database_operations.py → app/database.py

## Import Cycles
- None detected.

## Communities (84 total, 4 thin omitted)

### Community 0 - "make_user"
Cohesion: 0.07
Nodes (109): home(), Painel operacional do grupo ativo., generate_next_execution(), Gera a próxima execução do ciclo, se aplicável. Condições: - Execução vinculada…, add_item_to_execution(), complete_item(), create_execution_from_template(), create_execution_standalone() (+101 more)

### Community 1 - "offline-cache.js"
Cohesion: 0.05
Nodes (104): applyPersistedOfflineItemState(), auditCard(), buildConflict(), buildQueuedOperation(), classifyOperation(), clearOfflineItemIndicators(), clearOfflineItemIndicatorsWhenSynced(), closeManualModal() (+96 more)

### Community 2 - "executions.py"
Cohesion: 0.06
Nodes (96): Group, close_execution_page(), complete_item_form(), _completed_page(), create_execution_page(), edit_item_form(), execution_detail(), execution_items_fragment() (+88 more)

### Community 3 - "Execution"
Cohesion: 0.06
Nodes (67): Execution, ExecutionItem, Calcula o valor total do item (qtd * preço unitário)., SyncConflictAudit, AddExecutionItemOperation, ConflictResolutionOperation, _execution_state(), ExecutionItemOperation (+59 more)

### Community 4 - "test_database_operations.py"
Cohesion: 0.06
Nodes (48): Aceita nomes usuais de ambiente além de booleanos., Usa psycopg 3 para URLs PostgreSQL fornecidas por provedores., Permite autenticação em desenvolvimento servido por HTTP., Settings, create_database_engine(), Cria engine com ajustes específicos para SQLite ou PostgreSQL., BaseSettings, CompletedProcess (+40 more)

### Community 5 - "User"
Cohesion: 0.09
Nodes (38): get_db(), get_active_group(), get_current_user(), get_current_user_ws(), get_unread_notification_count(), Request, Session, Dependências reutilizáveis para injeção em rotas. (+30 more)

### Community 6 - "ExecutionStatus"
Cohesion: 0.10
Nodes (40): ExecutionStatus, agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request (+32 more)

### Community 7 - "Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX"
Cohesion: 0.05
Nodes (40): Acompanhamento até produção, BL-0012 — Gestão documental compartilhada dos projetos VGX, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+32 more)

### Community 8 - "tupa_auth_service.py"
Cohesion: 0.09
Nodes (32): add_unread_count(), health_check(), get, Request, Serve o service worker na raiz para permitir cache offline da aplicação., Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores., Injeta unread_count no request.state para todas as requisições. Lê o cookie de…, service_worker() (+24 more)

### Community 9 - "categories.py"
Cohesion: 0.12
Nodes (38): Category, create_category_page(), delete_category_confirm_page(), edit_category_page(), handle_create_category(), handle_delete_category(), handle_edit_category(), handle_move_category() (+30 more)

### Community 10 - "AGENTS.md"
Cohesion: 0.05
Nodes (38): Arquitetura, Backend, Backend, Banco de Dados, Cache e Mensageria, Categoria, Conceitos do Domínio, Concorrência é controlada por bloqueio otimista. (+30 more)

### Community 11 - "groups.py"
Cohesion: 0.13
Nodes (35): create_group_page(), group_detail(), handle_create_group(), handle_edit_group(), handle_invite(), handle_remove_member(), handle_switch_group(), list_groups() (+27 more)

### Community 12 - "auth.py"
Cohesion: 0.11
Nodes (33): handle_change_password(), handle_setup_profile(), handle_update_profile(), login_error_page(), login_page(), login_sent_page(), logout(), password_login() (+25 more)

### Community 13 - "templates.py"
Cohesion: 0.14
Nodes (34): create_template_page(), edit_template_page(), _get_template_context(), handle_add_item(), handle_create_template(), handle_delete_template(), handle_edit_item(), handle_edit_template() (+26 more)

### Community 14 - "group_service.py"
Cohesion: 0.10
Nodes (23): get_settings(), invite_member(), Convida um novo membro para o grupo via magic link. Retorna dict com success,…, Troca o grupo ativo na sessão., switch_active_group(), _build_invite_email(), _build_login_email(), _build_magic_link() (+15 more)

### Community 15 - "template_service.py"
Cohesion: 0.13
Nodes (22): RecurrenceType, Template, TemplateItem, _iso(), datetime, can_delete_template(), delete_template(), get_template_item_by_id() (+14 more)

### Community 16 - "template_learning_service.py"
Cohesion: 0.14
Nodes (24): analyze_template_history(), apply_template_suggestions(), dismiss_template_suggestions(), _dismissal_key_for_suggestion(), _dismissal_value_for_suggestion(), _dismissed_keys(), get_template_suggestions(), _is_learning_enabled_for_execution() (+16 more)

### Community 17 - "🌙 Jaci"
Cohesion: 0.07
Nodes (28): 1. Clone o repositório, 3. Instale as dependências, 4. Execute, Backup automático do PostgreSQL, Banco de dados e migrações, Com Caddy (HTTPS automático), 📧 Configuração de e-mail, Configure o ambiente (+20 more)

### Community 18 - "backlog/README.md"
Cohesion: 0.19
Nodes (3): Backlog legado — Sprint 4 — Aprendizado contínuo dos templates, Rastreabilidade das regras de negócio, Rastreabilidade dos fluxos do usuário

### Community 19 - "Refinamento — BL-0013 — Busca e padronização das telas de itens"
Cohesion: 0.09
Nodes (23): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Busca local e navegação padronizada, Excluído, Fatia 1.1.1 — Criar contratos TDD e integrar a Lista (+15 more)

### Community 20 - "user-flows.md"
Cohesion: 0.10
Nodes (18): Atores, Atores, FL-02 — Criação de Template, FL-05 — Compra Colaborativa, FL-10 — Home Operacional, Fluxo Crítico do Produto, Fluxo Principal, Fluxo Principal (+10 more)

### Community 21 - "Refinamento — BL-NNNN — Título"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — `<resultado da etapa>`, Excluído, Fatia 1.1.1 — `<resultado pequeno e verificável>` (+13 more)

### Community 22 - "Regras de negócio críticas"
Cohesion: 0.10
Nodes (19): Regras de negócio críticas, RN01, RN02, RN03, RN04, RN05, RN06, RN07 (+11 more)

### Community 23 - "datetime.py"
Cohesion: 0.28
Nodes (6): Base, set_sqlite_pragma(), Notification, TemplateLearningDismissal, DeclarativeBase, listens_for

### Community 24 - "Fundação PWA e Offline"
Cohesion: 0.11
Nodes (18): BL-004 — Estratégia de Cache, BL-005 a BL-013 — Cache Local e Operações Offline, BL-014 — Fila Local de Operações, BL-015 — Sincronização Automática, BL-016 — Status Detalhado de Sincronização, BL-017 — Retentativa Automática, BL-019 — Resolução de Conflitos, BL-020 — Central de Sincronização (+10 more)

### Community 25 - "auth_service.py"
Cohesion: 0.22
Nodes (13): authenticate_with_password(), get_or_create_tupa_user(), Session, Associa uma identidade Tupã ao perfil local do Jaci., Autentica no Tupã e carrega o perfil local., Cria a identidade no Tupã e o perfil local no Jaci., Completa os dados locais do perfil., Atualiza os dados pessoais do usuário. (+5 more)

### Community 26 - "ConnectionManager"
Cohesion: 0.18
Nodes (8): ConnectionManager, Any, WebSocket, Gerenciador de conexões WebSocket. Agrupa conexões por execution_id para…, Aceita a conexão e registra na sala., Remove a conexão da sala., Envia mensagem para todos na sala, exceto o remetente (se informado). Formato:…, Envia mensagem para um único cliente.

### Community 27 - "item-filter.js"
Cohesion: 0.31
Nodes (13): apply(), expandMatchingGroup(), formatMoney(), initAll(), initRoot(), normalize(), restoreForcedCollapse(), scheduleApply() (+5 more)

### Community 28 - "Backlog de produção"
Cohesion: 0.14
Nodes (14): Backlog de produção, Checklist de passagem ponta a ponta, Ciclo de vida, Classificações, Entrada rápida, Evidências e dados sensíveis, Git Flow, Itens arquivados (+6 more)

### Community 29 - "Identificação e entrada"
Cohesion: 0.15
Nodes (12): Acompanhamento até produção, BL-0010 — Disponibilizar reset de senha via login e área logada, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 30 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0001 — Completar cobertura e rastreabilidade da operação offline, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 31 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0002 — Adicionar unidades de medida, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 32 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0003 — Disponibilizar histórico de preços por grupo e item, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 33 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0004 — Disponibilizar análise de gastos e dashboard financeiro, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 34 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0005 — Evoluir inteligência de compras, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 35 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0006 — Implementar integrações externas, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 36 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0007 — Replicar backups em armazenamento externo, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 37 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0008 — Disponibilizar autoexclusão e anonimização de conta, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 38 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0009 — Implementar criptografia de dados em repouso, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 39 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0011 — Ampliar cobertura automatizada e testes de UI, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 40 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0013 — Buscar itens e padronizar categorias nas telas de Lista e Compra, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 41 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-NNNN — Título curto, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 42 - "sync_center"
Cohesion: 0.22
Nodes (8): get, Request, Session, Central local para visualização e resolução da fila de sincronização., sync_center(), make_request(), Request, test_sync_center_requires_authentication()

### Community 43 - "service-worker.js"
Cohesion: 0.22
Nodes (3): ACTIVE_CACHES, isShellAsset(), SHELL_ASSETS

### Community 44 - "loading-indicator.js"
Cohesion: 0.33
Nodes (7): beginRequest(), endRequest(), isPlainLeftClick(), requestCount(), scheduleHide(), shouldShowForLink(), show()

### Community 45 - "sync-status.js"
Cohesion: 0.42
Nodes (8): failSync(), finishSync(), formatDateTime(), render(), renderDetails(), setState(), startSync(), waitForRetry()

### Community 46 - "format_local_date"
Cohesion: 0.28
Nodes (7): localdate_filter(), localdatetime_filter(), format_local_date(), format_local_datetime(), date, Convert UTC datetime to local timezone for display, Convert UTC datetime to local date only

### Community 47 - "Pricipais Entidades"
Cohesion: 0.22
Nodes (8): Categoria, Execução, Grupo, Item de Execução, Item de Template, Pricipais Entidades, Template, Usuário

### Community 48 - "Aprendizado contínuo dos templates"
Cohesion: 0.22
Nodes (8): Aprendizado contínuo dos templates, BL-029 — Detecção de itens adicionados na execução, BL-030 — Incorporação de itens, BL-031 e BL-032 — Quantidades recorrentes, BL-033 e BL-034 — Observações recorrentes, BL-075 e BL-076 — Orçamentos recorrentes, Configuração por grupo, Sugestões ignoradas

### Community 49 - "read"
Cohesion: 0.39
Nodes (8): Path, read(), test_completed_execution_is_searchable_collapsible_and_read_only(), test_mutable_execution_exposes_filter_and_visible_financial_metadata(), test_shared_item_filter_controls_rows_groups_counts_and_empty_state(), test_shared_item_filter_normalizes_and_matches_names_locally(), test_shared_item_filter_preserves_query_across_dynamic_fragment_updates(), test_template_detail_exposes_accessible_filter_contract()

### Community 50 - "0001 - Tratamento de datas e timezone"
Cohesion: 0.25
Nodes (7): 0001 - Tratamento de datas e timezone, Antipadrões, Consequências, Contexto, Decisão, Exemplos, Status

### Community 51 - "0002 - Backup automático do PostgreSQL"
Cohesion: 0.25
Nodes (8): 0002 - Backup automático do PostgreSQL, Consequências, Contexto, Decisão, Plano refinado, Progresso, Status, Validação

### Community 52 - "Tela Inicial Operacional"
Cohesion: 0.29
Nodes (7): Alertas, Histórico Recente, Indicadores, Objetivo, Offline e Sincronização, Prioridade da Compra Principal, Tela Inicial Operacional

### Community 53 - "Backups do PostgreSQL"
Cohesion: 0.29
Nodes (7): Agenda e logs, Backups do PostgreSQL, Configuração, Execução manual, Restauração manual em banco isolado, Retenção, Visão geral

### Community 54 - "execution_ws_handler"
Cohesion: 0.33
Nodes (6): websocket, WebSocket para sincronização em tempo real de uma execução. Autenticação via…, websocket_execution(), execution_ws_handler(), WebSocket, Gerencia a conexão WebSocket para uma execução específica. Autentica via token…

### Community 55 - "privacy_policy"
Cohesion: 0.47
Nodes (5): privacy_policy(), get, Request, Privacy Policy page - LGPD, terms_of_use()

### Community 56 - "Estratégia de Banco de Dados"
Cohesion: 0.33
Nodes (5): Ambientes, Backups de produção, Estratégia de Banco de Dados, Migração de Dados, Migrações

### Community 57 - "Backlog legado do Jaci"
Cohesion: 0.33
Nodes (6): Aprendizado de templates, Backlog legado do Jaci, Edição de execuções agendadas, Entregas concluídas sem identificador BL legado, Mapeamento das fontes abertas migradas, PWA, operação offline e sincronização

### Community 58 - "Edição de execuções agendadas"
Cohesion: 0.33
Nodes (5): Campos editáveis, Edição de execuções agendadas, Notificações e sincronização, Regras, Sincronização offline

### Community 59 - "FL-03 — Geração de Execução"
Cohesion: 0.33
Nodes (6): Atores, FL-03 — Geração de Execução, Fluxo Automático, Fluxo Manual, Objetivo, Resultado Esperado

### Community 60 - "FL-04 — Execução da Compra"
Cohesion: 0.33
Nodes (6): Atores, Cenários Alternativos, FL-04 — Execução da Compra, Fluxo Principal, Objetivo, Resultado Esperado

### Community 61 - "FL-08 — Consulta da Agenda e Histórico"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-08 — Consulta da Agenda e Histórico, Fluxo Principal, Objetivo, Resultado Esperado

### Community 62 - "FL-09 — Operação Offline"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-09 — Operação Offline, Fluxo Principal, Objetivo, Resultado Esperado

### Community 63 - "FL-06 — Aprendizado do Template"
Cohesion: 0.33
Nodes (6): FL-06 — Aprendizado do Template, Fluxo Principal, Objetivo, Pré-condições, Resultado Esperado, Tipos de Sugestão

### Community 64 - "test_auth_pages.py"
Cohesion: 0.53
Nodes (5): make_request(), Request, test_invalid_registration_renders_register_page_and_preserves_identity_fields(), test_login_page_only_contains_login_form_and_registration_link(), test_register_page_contains_registration_form_and_login_link()

### Community 66 - "ensure_schema_compatibility"
Cohesion: 0.50
Nodes (4): ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., apply_migrations(), Aplica migrações Alembic e adota bancos SQLite legados.

### Community 67 - "FL-01 — Primeiro Acesso e Onboarding"
Cohesion: 0.40
Nodes (5): Atores, FL-01 — Primeiro Acesso e Onboarding, Fluxo Principal, Objetivo, Resultado Esperado

### Community 68 - "FL-07 — Gestão de Grupos"
Cohesion: 0.40
Nodes (5): Atores, FL-07 — Gestão de Grupos, Fluxo Principal, Objetivo, Resultado Esperado

### Community 69 - "run.py"
Cohesion: 0.50
Nodes (4): main(), parse_args(), Namespace, Executa o Jaci aplicando migrações antes de iniciar o servidor.

### Community 71 - "docker-entrypoint.sh"
Cohesion: 0.83
Nodes (3): is_server_process(), docker-entrypoint.sh script, write_cron_environment()

## Knowledge Gaps
- **374 isolated node(s):** `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script`, `Projeto: Jaci`, `Princípios do Produto` (+369 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `make_user`, `executions.py`, `Execution`, `ExecutionStatus`, `tupa_auth_service.py`, `categories.py`, `sync_center`, `groups.py`, `auth.py`, `templates.py`, `group_service.py`, `template_service.py`, `datetime.py`, `auth_service.py`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `Execution` connect `Execution` to `make_user`, `executions.py`, `ExecutionStatus`, `template_service.py`, `template_learning_service.py`, `datetime.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `User` (e.g. with `Base` and `AddExecutionItemOperation`) actually correct?**
  _`User` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 80 inferred relationships involving `make_user()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_user()` has 80 INFERRED edges - model-reasoned connections that need verification._
- **Are the 79 inferred relationships involving `make_group()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_group()` has 79 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script` to the rest of the system?**
  _374 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `make_user` be split into smaller, more focused modules?**
  _Cohesion score 0.06918767507002802 - nodes in this community are weakly interconnected._