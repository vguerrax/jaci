# Graph Report - jaci  (2026-08-03)

## Corpus Check
- 125 files · ~124,934 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1550 nodes · 3951 edges · 77 communities (73 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 234 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9e18fb4e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_user
- offline-cache.js
- template_service.py
- Execution
- executions.py
- Execution
- test_database_operations.py
- auth.py
- User
- Group
- agenda_service.py
- main.py
- Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX
- tupa_auth_service.py
- User
- AGENTS.md
- groups.py
- auth.py
- template_service.py
- utils/__init__.py
- offline_cache_service.py
- template_learning_service.py
- 🌙 Jaci
- notification_service.py
- backlog/README.md
- Refinamento — BL-NNNN — Título
- Regras de negócio críticas
- notification_service.py
- Fundação PWA e Offline
- config.py
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
- offline.py
- Pricipais Entidades
- Aprendizado contínuo dos templates
- read
- 0001 - Tratamento de datas e timezone
- 0002 - Backup automático do PostgreSQL
- Tela Inicial Operacional
- Backups do PostgreSQL
- execution_service.py
- privacy_policy
- Estratégia de Banco de Dados
- Backlog legado do Jaci
- Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra
- FL-03 — Geração de Execução
- FL-04 — Execução da Compra
- FL-08 — Consulta da Agenda e Histórico
- user-flows.md
- FL-06 — Aprendizado do Template
- handle_create_execution
- ensure_schema_compatibility
- test_pwa.py
- FL-07 — Gestão de Grupos
- run.py
- docker-entrypoint.sh
- overview.md
- backup_database.sh
- app/__init__.py
- publish.sh
- execution-budget.js
- ensure_schema_compatibility
- test_pwa.py
- Identificação e entrada
- Edição de execuções agendadas

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
- `test_database_engine_uses_sqlite_specific_connection_options()` --calls--> `create_database_engine()`  [EXTRACTED]
  tests/test_database_operations.py → app/database.py

## Import Cycles
- None detected.

## Communities (77 total, 4 thin omitted)

### Community 0 - "make_user"
Cohesion: 0.06
Nodes (129): RecurrenceType, calculate_next_date(), generate_next_execution(), Calcula a próxima data baseada na recorrência. Usado para geração automática de…, Gera a próxima execução do ciclo, se aplicável. Condições: - Execução vinculada…, add_item_to_execution(), complete_item(), create_execution_from_template() (+121 more)

### Community 1 - "offline-cache.js"
Cohesion: 0.05
Nodes (107): applyPersistedOfflineItemState(), auditCard(), buildConflict(), buildQueuedOperation(), calculateExecutionTotal(), classifyOperation(), clearOfflineItemIndicators(), clearOfflineItemIndicatorsWhenSynced() (+99 more)

### Community 2 - "template_service.py"
Cohesion: 0.09
Nodes (57): create_execution_page(), handle_create_execution(), Create execution form page (from template or standalone)., Create a new execution., create_template_page(), edit_template_page(), _get_template_context(), handle_add_item() (+49 more)

### Community 3 - "Execution"
Cohesion: 0.07
Nodes (69): ExecutionStatus, Execution, ExecutionItem, Calcula o valor total do item (qtd * preço unitário)., SyncConflictAudit, AddExecutionItemOperation, ConflictResolutionOperation, _execution_state() (+61 more)

### Community 4 - "executions.py"
Cohesion: 0.10
Nodes (55): close_execution_page(), complete_item_form(), _completed_page(), edit_item_form(), execution_detail(), execution_items_fragment(), execution_sidebar_fragment(), _get_items_fragment() (+47 more)

### Community 5 - "test_database_operations.py"
Cohesion: 0.06
Nodes (48): Aceita nomes usuais de ambiente além de booleanos., Usa psycopg 3 para URLs PostgreSQL fornecidas por provedores., Permite autenticação em desenvolvimento servido por HTTP., Settings, create_database_engine(), Cria engine com ajustes específicos para SQLite ou PostgreSQL., BaseSettings, CompletedProcess (+40 more)

### Community 6 - "auth.py"
Cohesion: 0.07
Nodes (51): handle_change_password(), handle_setup_profile(), handle_update_profile(), login_error_page(), login_page(), login_sent_page(), logout(), password_login() (+43 more)

### Community 7 - "User"
Cohesion: 0.13
Nodes (40): User, create_group_page(), group_detail(), handle_create_group(), handle_edit_group(), handle_invite(), handle_remove_member(), handle_switch_group() (+32 more)

### Community 8 - "Group"
Cohesion: 0.05
Nodes (75): Base, Category, Group, Notification, TemplateLearningDismissal, Template, TemplateItem, create_category_page() (+67 more)

### Community 9 - "agenda_service.py"
Cohesion: 0.07
Nodes (57): agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request, Session (+49 more)

### Community 10 - "main.py"
Cohesion: 0.14
Nodes (24): get_db(), set_sqlite_pragma(), get_active_group(), get_current_user(), get_current_user_ws(), get_unread_notification_count(), Request, Session (+16 more)

### Community 7 - "Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX"
Cohesion: 0.05
Nodes (40): Acompanhamento até produção, BL-0012 — Gestão documental compartilhada dos projetos VGX, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+32 more)

### Community 12 - "tupa_auth_service.py"
Cohesion: 0.16
Nodes (22): add_unread_count(), home(), Request, Painel operacional do grupo ativo., Injeta unread_count no request.state para todas as requisições. Lê o cookie de…, create_user(), _credentials(), decode_access_token() (+14 more)

### Community 10 - "AGENTS.md"
Cohesion: 0.05
Nodes (38): Arquitetura, Backend, Backend, Banco de Dados, Cache e Mensageria, Categoria, Conceitos do Domínio, Concorrência é controlada por bloqueio otimista. (+30 more)

### Community 11 - "groups.py"
Cohesion: 0.11
Nodes (37): create_group_page(), group_detail(), handle_edit_group(), handle_invite(), handle_remove_member(), list_groups(), get, post (+29 more)

### Community 12 - "auth.py"
Cohesion: 0.10
Nodes (36): handle_change_password(), handle_setup_profile(), handle_update_profile(), login_error_page(), login_page(), login_sent_page(), logout(), password_login() (+28 more)

### Community 13 - "template_service.py"
Cohesion: 0.10
Nodes (51): create_template_page(), edit_template_page(), _get_template_context(), handle_add_item(), handle_create_template(), handle_delete_template(), handle_edit_item(), handle_edit_template() (+43 more)

### Community 14 - "utils/__init__.py"
Cohesion: 0.15
Nodes (15): localdate_filter(), localdatetime_filter(), format_local_date(), format_local_datetime(), date, Convert UTC datetime to local timezone for display, Convert UTC datetime to local date only, _build_invite_email() (+7 more)

### Community 15 - "offline_cache_service.py"
Cohesion: 0.39
Nodes (7): build_offline_snapshot(), _enum_value(), _iso(), Any, datetime, Session, Monta dados essenciais somente leitura para consulta offline.

### Community 16 - "template_learning_service.py"
Cohesion: 0.11
Nodes (30): Base, Notification, TemplateLearningDismissal, Template, TemplateItem, analyze_template_history(), apply_template_suggestions(), dismiss_template_suggestions() (+22 more)

### Community 17 - "🌙 Jaci"
Cohesion: 0.07
Nodes (28): 1. Clone o repositório, 3. Instale as dependências, 4. Execute, Backup automático do PostgreSQL, Banco de dados e migrações, Com Caddy (HTTPS automático), 📧 Configuração de e-mail, Configure o ambiente (+20 more)

### Community 15 - "notification_service.py"
Cohesion: 0.11
Nodes (27): handle_mark_all_read(), handle_mark_read(), list_notifications(), get, post, Request, Session, List notifications for the current user. (+19 more)

### Community 16 - "backlog/README.md"
Cohesion: 0.18
Nodes (4): Backlog legado — Sprint 4 — Aprendizado contínuo dos templates, Demandas do backlog ativo, Rastreabilidade das regras de negócio, Rastreabilidade dos fluxos do usuário

### Community 21 - "Refinamento — BL-NNNN — Título"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — `<resultado da etapa>`, Excluído, Fatia 1.1.1 — `<resultado pequeno e verificável>` (+13 more)

### Community 22 - "Regras de negócio críticas"
Cohesion: 0.10
Nodes (19): Regras de negócio críticas, RN01, RN02, RN03, RN04, RN05, RN06, RN07 (+11 more)

### Community 23 - "notification_service.py"
Cohesion: 0.24
Nodes (13): create_notification(), mark_as_read(), notify_execution_completed(), notify_execution_started(), notify_execution_updated(), notify_group_members(), Session, Notifica membros que uma compra agendada foi alterada. (+5 more)

### Community 24 - "Fundação PWA e Offline"
Cohesion: 0.11
Nodes (18): BL-004 — Estratégia de Cache, BL-005 a BL-013 — Cache Local e Operações Offline, BL-014 — Fila Local de Operações, BL-015 — Sincronização Automática, BL-016 — Status Detalhado de Sincronização, BL-017 — Retentativa Automática, BL-019 — Resolução de Conflitos, BL-020 — Central de Sincronização (+10 more)

### Community 21 - "config.py"
Cohesion: 0.17
Nodes (10): get_settings(), _build_invite_email(), _build_login_email(), _build_magic_link(), Template HTML para e-mail de convite para grupo., Monta a URL completa do magic link., Envia e-mail com magic link. Se SMTP não configurado, faz log do link (modo…, Template HTML para e-mail de login. (+2 more)

### Community 26 - "ConnectionManager"
Cohesion: 0.22
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

### Community 25 - "Backups do PostgreSQL"
Cohesion: 0.29
Nodes (7): Agenda e logs, Backups do PostgreSQL, Configuração, Execução manual, Restauração manual em banco isolado, Retenção, Visão geral

### Community 26 - "Identificação e entrada"
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

### Community 41 - "0002 - Backup automático do PostgreSQL"
Cohesion: 0.12
Nodes (13): 0002 - Backup automático do PostgreSQL, Consequências, Contexto, Decisão, Plano refinado, Progresso, Status, Validação (+5 more)

### Community 42 - "Pricipais Entidades"
Cohesion: 0.22
Nodes (8): Categoria, Execução, Grupo, Item de Execução, Item de Template, Pricipais Entidades, Template, Usuário

### Community 48 - "Aprendizado contínuo dos templates"
Cohesion: 0.22
Nodes (8): Aprendizado contínuo dos templates, BL-029 — Detecção de itens adicionados na execução, BL-030 — Incorporação de itens, BL-031 e BL-032 — Quantidades recorrentes, BL-033 e BL-034 — Observações recorrentes, BL-075 e BL-076 — Orçamentos recorrentes, Configuração por grupo, Sugestões ignoradas

### Community 49 - "read"
Cohesion: 0.36
Nodes (9): Path, read(), test_clear_and_collapse_controls_share_a_safe_click_handler(), test_completed_execution_is_searchable_collapsible_and_read_only(), test_mutable_execution_exposes_filter_and_visible_financial_metadata(), test_shared_item_filter_controls_rows_groups_counts_and_empty_state(), test_shared_item_filter_normalizes_and_matches_names_locally(), test_shared_item_filter_preserves_query_across_dynamic_fragment_updates() (+1 more)

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

### Community 54 - "execution_service.py"
Cohesion: 0.18
Nodes (19): cancel_execution(), create_execution_from_pending(), ensure_execution_is_mutable(), generate_next_execution(), get_execution_items_grouped(), get_executions_for_group(), incomplete_item(), datetime (+11 more)

### Community 55 - "privacy_policy"
Cohesion: 0.47
Nodes (5): privacy_policy(), get, Request, Privacy Policy page - LGPD, terms_of_use()

### Community 56 - "Estratégia de Banco de Dados"
Cohesion: 0.33
Nodes (5): Ambientes, Backups de produção, Estratégia de Banco de Dados, Migração de Dados, Migrações

### Community 57 - "Backlog legado do Jaci"
Cohesion: 0.33
Nodes (6): Aprendizado de templates, Backlog legado do Jaci, Edição de execuções agendadas, Entregas concluídas sem identificador BL legado, Mapeamento das fontes abertas migradas, PWA, operação offline e sincronização

### Community 48 - "Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Acompanhamento contínuo do orçamento, Excluído, Fatia 1.1.1 — Implementar o contrato completo da BL-0014 (+13 more)

### Community 59 - "FL-03 — Geração de Execução"
Cohesion: 0.33
Nodes (6): Atores, FL-03 — Geração de Execução, Fluxo Automático, Fluxo Manual, Objetivo, Resultado Esperado

### Community 60 - "FL-04 — Execução da Compra"
Cohesion: 0.33
Nodes (6): Atores, Cenários Alternativos, FL-04 — Execução da Compra, Fluxo Principal, Objetivo, Resultado Esperado

### Community 61 - "FL-08 — Consulta da Agenda e Histórico"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-08 — Consulta da Agenda e Histórico, Fluxo Principal, Objetivo, Resultado Esperado

### Community 52 - "user-flows.md"
Cohesion: 0.08
Nodes (24): Atores, Atores, Atores, Estado e rastreabilidade, FL-02 — Criação de Template, FL-05 — Compra Colaborativa, FL-09 — Operação Offline, FL-10 — Home Operacional (+16 more)

### Community 63 - "FL-06 — Aprendizado do Template"
Cohesion: 0.33
Nodes (6): FL-06 — Aprendizado do Template, Fluxo Principal, Objetivo, Pré-condições, Resultado Esperado, Tipos de Sugestão

### Community 64 - "handle_create_execution"
Cohesion: 0.17
Nodes (16): agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request, Session (+8 more)

### Community 66 - "ensure_schema_compatibility"
Cohesion: 0.50
Nodes (4): ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., apply_migrations(), Aplica migrações Alembic e adota bancos SQLite legados.

### Community 67 - "test_pwa.py"
Cohesion: 0.15
Nodes (12): health_check(), get, Serve o service worker na raiz para permitir cache offline da aplicação., Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores., service_worker(), web_app_manifest(), png_dimensions(), Path (+4 more)

### Community 68 - "FL-07 — Gestão de Grupos"
Cohesion: 0.40
Nodes (5): Atores, FL-07 — Gestão de Grupos, Fluxo Principal, Objetivo, Resultado Esperado

### Community 69 - "run.py"
Cohesion: 0.50
Nodes (4): main(), parse_args(), Namespace, Executa o Jaci aplicando migrações antes de iniciar o servidor.

### Community 71 - "docker-entrypoint.sh"
Cohesion: 0.83
Nodes (3): is_server_process(), docker-entrypoint.sh script, write_cron_environment()

### Community 74 - "execution-budget.js"
Cohesion: 0.29
Nodes (15): alertMessage(), applyVisualState(), budgetBand(), ensureToastContainer(), formatMoney(), handleRemoteAlerts(), init(), refreshFromDocument() (+7 more)

### Community 75 - "ensure_schema_compatibility"
Cohesion: 0.50
Nodes (4): ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., apply_migrations(), Aplica migrações Alembic e adota bancos SQLite legados.

### Community 80 - "test_pwa.py"
Cohesion: 0.15
Nodes (12): health_check(), get, Serve o service worker na raiz para permitir cache offline da aplicação., Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores., service_worker(), web_app_manifest(), png_dimensions(), Path (+4 more)

### Community 83 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0014 — Fixar resumo de orçamento durante a compra, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 86 - "Edição de execuções agendadas"
Cohesion: 0.33
Nodes (5): Campos editáveis, Edição de execuções agendadas, Notificações e sincronização, Regras, Sincronização offline

## Knowledge Gaps
- **374 isolated node(s):** `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script`, `Projeto: Jaci`, `Princípios do Produto` (+369 more)
- **374 isolated node(s):** `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script`, `Projeto: Jaci`, `Princípios do Produto` (+369 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `make_user`, `template_service.py`, `Execution`, `executions.py`, `sync_center`, `auth.py`, `Group`, `agenda_service.py`, `main.py`, `tupa_auth_service.py`, `notification_service.py`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `Execution` connect `Execution` to `make_user`, `template_service.py`, `executions.py`, `Group`, `agenda_service.py`, `notification_service.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra` connect `Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra` to `backlog/README.md`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `User` (e.g. with `Base` and `AddExecutionItemOperation`) actually correct?**
  _`User` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 82 inferred relationships involving `make_user()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_user()` has 82 INFERRED edges - model-reasoned connections that need verification._
- **Are the 81 inferred relationships involving `make_group()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_group()` has 81 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script` to the rest of the system?**
  _374 weakly-connected nodes found - possible documentation gaps or missing edges._