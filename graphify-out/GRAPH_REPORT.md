# Graph Report - .  (2026-08-04)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1057 nodes · 3442 edges · 45 communities (40 shown, 5 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 235 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7c0a241c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_user
- offline-cache.js
- template_service.py
- Execution
- auth.py
- agenda_service.py
- executions.py
- categories.py
- get_group_by_id
- datetime.py
- notification_service.py
- User
- test_pwa.py
- test_postgresql_backup.py
- test_database_operations.py
- execution-budget.js
- ConnectionManager
- item-filter.js
- migrate_sqlite_to_postgres.py
- sync_center
- service-worker.js
- read
- loading-indicator.js
- sync-status.js
- email.py
- config.py
- privacy_policy
- .normalize_database_url
- ensure_schema_compatibility
- run.py
- docker-entrypoint.sh
- .disable_secure_cookie_in_debug
- backup_database.sh
- app/__init__.py
- publish.sh

## God Nodes (most connected - your core abstractions)
1. `User` - 144 edges
2. `make_user()` - 85 edges
3. `make_group()` - 84 edges
4. `create_template()` - 71 edges
5. `create_execution_from_template()` - 70 edges
6. `Execution` - 61 edges
7. `add_item_to_template()` - 50 edges
8. `ExecutionItem` - 49 edges
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
- `test_backup_settings_are_loaded_from_dotenv()` --calls--> `Settings`  [EXTRACTED]
  tests/test_postgresql_backup.py → app/config.py

## Import Cycles
- None detected.

## Communities (45 total, 5 thin omitted)

### Community 0 - "make_user"
Cohesion: 0.06
Nodes (129): RecurrenceType, add_item_to_execution(), cancel_execution(), complete_item(), create_execution_from_pending(), create_execution_from_template(), create_execution_standalone(), ensure_execution_is_mutable() (+121 more)

### Community 1 - "offline-cache.js"
Cohesion: 0.05
Nodes (107): applyPersistedOfflineItemState(), auditCard(), buildConflict(), buildQueuedOperation(), calculateExecutionTotal(), classifyOperation(), clearOfflineItemIndicators(), clearOfflineItemIndicatorsWhenSynced() (+99 more)

### Community 2 - "template_service.py"
Cohesion: 0.05
Nodes (85): TemplateLearningDismissal, Template, TemplateItem, create_template_page(), edit_template_page(), _get_template_context(), handle_add_item(), handle_create_template() (+77 more)

### Community 3 - "Execution"
Cohesion: 0.07
Nodes (62): ExecutionStatus, Execution, ExecutionItem, Calcula o valor total do item (qtd * preço unitário)., SyncConflictAudit, AddExecutionItemOperation, ConflictResolutionOperation, _execution_state() (+54 more)

### Community 4 - "auth.py"
Cohesion: 0.05
Nodes (70): add_unread_count(), websocket, WebSocket para sincronização em tempo real de uma execução. Autenticação via…, Injeta unread_count no request.state para todas as requisições. Lê o cookie de…, websocket_execution(), handle_change_password(), handle_setup_profile(), handle_update_profile() (+62 more)

### Community 5 - "agenda_service.py"
Cohesion: 0.06
Nodes (65): agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request, Session (+57 more)

### Community 6 - "executions.py"
Cohesion: 0.11
Nodes (54): Group, close_execution_page(), complete_item_form(), _completed_page(), create_execution_page(), edit_item_form(), execution_detail(), execution_items_fragment() (+46 more)

### Community 7 - "categories.py"
Cohesion: 0.12
Nodes (38): Category, create_category_page(), delete_category_confirm_page(), edit_category_page(), handle_create_category(), handle_delete_category(), handle_edit_category(), handle_move_category() (+30 more)

### Community 8 - "get_group_by_id"
Cohesion: 0.09
Nodes (39): create_group_page(), group_detail(), handle_create_group(), handle_edit_group(), handle_invite(), handle_remove_member(), handle_switch_group(), list_groups() (+31 more)

### Community 9 - "datetime.py"
Cohesion: 0.16
Nodes (18): Base, get_db(), set_sqlite_pragma(), get_active_group(), get_current_user(), get_current_user_ws(), get_unread_notification_count(), Request (+10 more)

### Community 10 - "notification_service.py"
Cohesion: 0.11
Nodes (28): Notification, handle_mark_all_read(), handle_mark_read(), list_notifications(), get, post, Request, Session (+20 more)

### Community 11 - "User"
Cohesion: 0.16
Nodes (18): Dependência que exige usuário autenticado. Levanta exceção se não autenticado., require_user(), User, authenticate_with_password(), get_or_create_tupa_user(), Session, Associa uma identidade Tupã ao perfil local do Jaci., Autentica no Tupã e carrega o perfil local. (+10 more)

### Community 12 - "test_pwa.py"
Cohesion: 0.12
Nodes (15): health_check(), home(), get, Request, Painel operacional do grupo ativo., Serve o service worker na raiz para permitir cache offline da aplicação., Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores., service_worker() (+7 more)

### Community 13 - "test_postgresql_backup.py"
Cohesion: 0.24
Nodes (18): CompletedProcess, _backup_environment(), fake_postgres_tools(), fixture, parametrize, Path, _run_backup(), test_backup_disabled_exits_without_calling_postgres_tools() (+10 more)

### Community 14 - "test_database_operations.py"
Cohesion: 0.16
Nodes (13): Settings, create_database_engine(), Cria engine com ajustes específicos para SQLite ou PostgreSQL., BaseSettings, Engine, create_database_if_missing(), test_cloud_postgres_urls_are_normalized_to_psycopg_driver(), test_create_database_is_idempotent_for_sqlite() (+5 more)

### Community 15 - "execution-budget.js"
Cohesion: 0.29
Nodes (15): alertMessage(), applyVisualState(), budgetBand(), ensureToastContainer(), formatMoney(), handleRemoteAlerts(), init(), refreshFromDocument() (+7 more)

### Community 16 - "ConnectionManager"
Cohesion: 0.18
Nodes (8): ConnectionManager, Any, WebSocket, Gerenciador de conexões WebSocket. Agrupa conexões por execution_id para…, Aceita a conexão e registra na sala., Remove a conexão da sala., Envia mensagem para todos na sala, exceto o remetente (se informado). Formato:…, Envia mensagem para um único cliente.

### Community 17 - "item-filter.js"
Cohesion: 0.31
Nodes (13): apply(), expandMatchingGroup(), formatMoney(), initAll(), initRoot(), normalize(), restoreForcedCollapse(), scheduleApply() (+5 more)

### Community 18 - "migrate_sqlite_to_postgres.py"
Cohesion: 0.21
Nodes (12): load_target_database_url(), migrate_data(), normalize_postgres_target(), normalize_sqlite_source(), parse_args(), Namespace, Migra todos os dados do SQLite para PostgreSQL preservando IDs e relações., Normaliza URLs fornecidas por provedores para o driver Psycopg 3. (+4 more)

### Community 19 - "sync_center"
Cohesion: 0.23
Nodes (9): get, Request, Session, Central local para visualização e resolução da fila de sincronização., sync_center(), make_request(), Request, test_sync_center_renders_local_queue_management_shell() (+1 more)

### Community 20 - "service-worker.js"
Cohesion: 0.22
Nodes (3): ACTIVE_CACHES, isShellAsset(), SHELL_ASSETS

### Community 21 - "read"
Cohesion: 0.36
Nodes (9): Path, read(), test_clear_and_collapse_controls_share_a_safe_click_handler(), test_completed_execution_is_searchable_collapsible_and_read_only(), test_mutable_execution_exposes_filter_and_visible_financial_metadata(), test_shared_item_filter_controls_rows_groups_counts_and_empty_state(), test_shared_item_filter_normalizes_and_matches_names_locally(), test_shared_item_filter_preserves_query_across_dynamic_fragment_updates() (+1 more)

### Community 22 - "loading-indicator.js"
Cohesion: 0.33
Nodes (7): beginRequest(), endRequest(), isPlainLeftClick(), requestCount(), scheduleHide(), shouldShowForLink(), show()

### Community 23 - "sync-status.js"
Cohesion: 0.42
Nodes (8): failSync(), finishSync(), formatDateTime(), render(), renderDetails(), setState(), startSync(), waitForRetry()

### Community 24 - "email.py"
Cohesion: 0.31
Nodes (8): _build_invite_email(), _build_login_email(), _build_magic_link(), Template HTML para e-mail de convite para grupo., Monta a URL completa do magic link., Envia e-mail com magic link. Se SMTP não configurado, faz log do link (modo…, Template HTML para e-mail de login., send_magic_link()

### Community 26 - "privacy_policy"
Cohesion: 0.47
Nodes (5): privacy_policy(), get, Request, Privacy Policy page - LGPD, terms_of_use()

### Community 28 - ".normalize_database_url"
Cohesion: 0.40
Nodes (3): Aceita nomes usuais de ambiente além de booleanos., Usa psycopg 3 para URLs PostgreSQL fornecidas por provedores., field_validator

### Community 29 - "ensure_schema_compatibility"
Cohesion: 0.50
Nodes (4): ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., apply_migrations(), Aplica migrações Alembic e adota bancos SQLite legados.

### Community 30 - "run.py"
Cohesion: 0.50
Nodes (4): main(), parse_args(), Namespace, Executa o Jaci aplicando migrações antes de iniciar o servidor.

### Community 32 - "docker-entrypoint.sh"
Cohesion: 0.83
Nodes (3): is_server_process(), docker-entrypoint.sh script, write_cron_environment()

## Knowledge Gaps
- **3 isolated node(s):** `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script`
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `make_user`, `template_service.py`, `Execution`, `auth.py`, `agenda_service.py`, `executions.py`, `categories.py`, `get_group_by_id`, `datetime.py`, `notification_service.py`, `test_pwa.py`, `sync_center`?**
  _High betweenness centrality (0.241) - this node is a cross-community bridge._
- **Why does `Execution` connect `Execution` to `make_user`, `template_service.py`, `agenda_service.py`, `executions.py`, `datetime.py`, `notification_service.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `create_execution_from_template()` connect `make_user` to `template_service.py`, `Execution`, `agenda_service.py`, `executions.py`, `User`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `User` (e.g. with `Base` and `AddExecutionItemOperation`) actually correct?**
  _`User` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 82 inferred relationships involving `make_user()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_user()` has 82 INFERRED edges - model-reasoned connections that need verification._
- **Are the 81 inferred relationships involving `make_group()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_group()` has 81 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._