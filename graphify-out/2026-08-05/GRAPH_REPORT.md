# Graph Report - jaci  (2026-08-05)

## Corpus Check
- 137 files · ~141,964 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1786 nodes · 4384 edges · 100 communities (96 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 280 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4707d303`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_group
- offline-cache.js
- template_service.py
- Execution
- auth.py
- utils/__init__.py
- executions.py
- get_category_by_id
- test_auth_pages.py
- main.py
- Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX
- build_offline_snapshot
- test_pwa.py
- test_database_operations.py
- AGENTS.md
- execution-budget.js
- ConnectionManager
- item-filter.js
- Refinamento — BL-0015 — Adicionar item como comprado durante execução
- sync_center
- service-worker.js
- read
- loading-indicator.js
- sync-status.js
- User
- 🌙 Jaci
- privacy_policy
- Refinamento — BL-0013 — Busca e padronização das telas de itens
- tests/README.md
- run.py
- docker-entrypoint.sh
- Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra
- backup_database.sh
- app/__init__.py
- publish.sh
- Refinamento — BL-NNNN — Título
- Regras de negócio críticas
- tupa_auth_service.py
- Fundação PWA e Offline
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
- Identificação e entrada
- ExecutionStatus
- 0002 - Backup automático do PostgreSQL
- offline.py
- Pricipais Entidades
- 0001 - Tratamento de datas e timezone
- Aprendizado contínuo dos templates
- Tela Inicial Operacional
- FL-08 — Consulta da Agenda e Histórico
- Backups do PostgreSQL
- home_service.py
- Backlog legado do Jaci
- Edição de execuções agendadas
- FL-03 — Geração de Execução
- FL-04 — Execução da Compra
- make_user
- FL-09 — Operação Offline
- Refinamento — BL-0016 — Botão flutuante para adicionar itens
- FL-01 — Primeiro Acesso e Onboarding
- notification_service.py
- Estratégia de Banco de Dados
- ensure_schema_compatibility
- overview.md
- FL-06 — Aprendizado do Template
- user-flows.md
- item-add-modal.js
- Refinamento — BL-0017 — Nome da execução avulsa
- handle_setup_profile
- config.py
- Identificação e entrada
- sync_conflict_audit_service.py
- Identificação e entrada
- read
- auth_service.py
- test_future_user_flows.py
- datetime.py

## God Nodes (most connected - your core abstractions)
1. `User` - 144 edges
2. `make_user()` - 107 edges
3. `make_group()` - 106 edges
4. `create_template()` - 81 edges
5. `create_execution_from_template()` - 74 edges
6. `Execution` - 69 edges
7. `add_item_to_template()` - 51 edges
8. `ExecutionItem` - 50 edges
9. `Group` - 44 edges
10. `ExecutionStatus` - 36 edges

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

## Communities (100 total, 4 thin omitted)

### Community 0 - "make_group"
Cohesion: 0.11
Nodes (38): handle_update_execution(), Edita dados próprios de uma execução agendada., create_execution_standalone(), Cria uma execução avulsa sem template., parse_local_date(), Parse a date string from form and convert to UTC for storage., make_group(), test_calendar_groups_executions_by_local_scheduled_date() (+30 more)

### Community 1 - "offline-cache.js"
Cohesion: 0.05
Nodes (113): applyPersistedOfflineItemState(), auditCard(), buildConflict(), buildQueuedOperation(), calculateExecutionTotal(), classifyOperation(), clearOfflineItemIndicators(), clearOfflineItemIndicatorsWhenSynced() (+105 more)

### Community 2 - "template_service.py"
Cohesion: 0.06
Nodes (82): Template, create_template_page(), edit_template_page(), _get_template_context(), _get_template_items_fragment(), handle_add_item(), handle_create_template(), handle_delete_template() (+74 more)

### Community 3 - "Execution"
Cohesion: 0.07
Nodes (50): Execution, ExecutionItem, Calcula o valor total do item (qtd * preço unitário)., AddExecutionItemOperation, ConflictResolutionOperation, ExecutionItemOperation, FinalizeExecutionOperation, _item_state() (+42 more)

### Community 4 - "auth.py"
Cohesion: 0.18
Nodes (18): login_error_page(), login_page(), login_sent_page(), logout(), profile_page(), get, Request, Tela de configuração de perfil (primeiro acesso). (+10 more)

### Community 5 - "utils/__init__.py"
Cohesion: 0.27
Nodes (9): clear_auth_cookies(), create_magic_token(), decode_magic_token(), Response, Cria token para magic link (15 minutos)., Decodifica magic token. Retorna o e-mail se válido, None caso contrário., Define os cookies httpOnly emitidos pelo Tupã., Remove os cookies de autenticação. (+1 more)

### Community 6 - "executions.py"
Cohesion: 0.10
Nodes (58): Group, close_execution_page(), complete_item_form(), _completed_page(), create_execution_page(), edit_item_form(), execution_detail(), execution_items_fragment() (+50 more)

### Community 7 - "get_category_by_id"
Cohesion: 0.14
Nodes (26): create_category_page(), delete_category_confirm_page(), edit_category_page(), handle_create_category(), handle_delete_category(), handle_edit_category(), handle_move_category(), handle_uncategorized_position() (+18 more)

### Community 8 - "test_auth_pages.py"
Cohesion: 0.53
Nodes (5): make_request(), Request, test_invalid_registration_renders_register_page_and_preserves_identity_fields(), test_login_page_only_contains_login_form_and_registration_link(), test_register_page_contains_registration_form_and_login_link()

### Community 9 - "main.py"
Cohesion: 0.13
Nodes (24): get_db(), set_sqlite_pragma(), get_active_group(), get_current_user(), get_current_user_ws(), get_unread_notification_count(), Request, Session (+16 more)

### Community 10 - "Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX"
Cohesion: 0.05
Nodes (40): Acompanhamento até produção, BL-0012 — Gestão documental compartilhada dos projetos VGX, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+32 more)

### Community 11 - "build_offline_snapshot"
Cohesion: 0.21
Nodes (11): build_offline_snapshot(), _enum_value(), Any, Session, Monta dados essenciais somente leitura para consulta offline., db(), make_category(), fixture (+3 more)

### Community 12 - "test_pwa.py"
Cohesion: 0.12
Nodes (15): health_check(), home(), get, Request, Painel operacional do grupo ativo., Serve o service worker na raiz para permitir cache offline da aplicação., Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores., service_worker() (+7 more)

### Community 13 - "test_database_operations.py"
Cohesion: 0.06
Nodes (48): Aceita nomes usuais de ambiente além de booleanos., Usa psycopg 3 para URLs PostgreSQL fornecidas por provedores., Permite autenticação em desenvolvimento servido por HTTP., Settings, create_database_engine(), Cria engine com ajustes específicos para SQLite ou PostgreSQL., BaseSettings, CompletedProcess (+40 more)

### Community 14 - "AGENTS.md"
Cohesion: 0.05
Nodes (39): Arquitetura, Backend, Backend, Banco de Dados, Cache e Mensageria, Categoria, Conceitos do Domínio, Concorrência é controlada por bloqueio otimista. (+31 more)

### Community 15 - "execution-budget.js"
Cohesion: 0.29
Nodes (15): alertMessage(), applyVisualState(), budgetBand(), ensureToastContainer(), formatMoney(), handleRemoteAlerts(), init(), refreshFromDocument() (+7 more)

### Community 16 - "ConnectionManager"
Cohesion: 0.22
Nodes (8): ConnectionManager, Any, WebSocket, Gerenciador de conexões WebSocket. Agrupa conexões por execution_id para…, Aceita a conexão e registra na sala., Remove a conexão da sala., Envia mensagem para todos na sala, exceto o remetente (se informado). Formato:…, Envia mensagem para um único cliente.

### Community 17 - "item-filter.js"
Cohesion: 0.30
Nodes (13): apply(), expandMatchingGroup(), formatMoney(), initAll(), initRoot(), normalize(), restoreForcedCollapse(), scheduleApply() (+5 more)

### Community 18 - "Refinamento — BL-0015 — Adicionar item como comprado durante execução"
Cohesion: 0.06
Nodes (34): Acompanhamento até produção, BL-0015 — Adicionar item como comprado durante execução, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+26 more)

### Community 19 - "sync_center"
Cohesion: 0.22
Nodes (8): get, Request, Session, Central local para visualização e resolução da fila de sincronização., sync_center(), make_request(), Request, test_sync_center_requires_authentication()

### Community 20 - "service-worker.js"
Cohesion: 0.22
Nodes (3): ACTIVE_CACHES, isShellAsset(), SHELL_ASSETS

### Community 21 - "read"
Cohesion: 0.30
Nodes (11): Path, read(), test_clear_and_collapse_controls_share_a_safe_click_handler(), test_completed_execution_is_searchable_collapsible_and_read_only(), test_hidden_filter_rows_override_bootstrap_display_utilities(), test_mutable_execution_exposes_filter_and_visible_financial_metadata(), test_shared_item_filter_controls_rows_groups_counts_and_empty_state(), test_shared_item_filter_normalizes_and_matches_names_locally() (+3 more)

### Community 22 - "loading-indicator.js"
Cohesion: 0.33
Nodes (7): beginRequest(), endRequest(), isPlainLeftClick(), requestCount(), scheduleHide(), shouldShowForLink(), show()

### Community 23 - "sync-status.js"
Cohesion: 0.42
Nodes (8): failSync(), finishSync(), formatDateTime(), render(), renderDetails(), setState(), startSync(), waitForRetry()

### Community 24 - "User"
Cohesion: 0.13
Nodes (40): User, create_group_page(), group_detail(), handle_create_group(), handle_edit_group(), handle_invite(), handle_remove_member(), handle_switch_group() (+32 more)

### Community 25 - "🌙 Jaci"
Cohesion: 0.07
Nodes (28): 1. Clone o repositório, 3. Instale as dependências, 4. Execute, Backup automático do PostgreSQL, Banco de dados e migrações, Com Caddy (HTTPS automático), 📧 Configuração de e-mail, Configure o ambiente (+20 more)

### Community 26 - "privacy_policy"
Cohesion: 0.47
Nodes (5): privacy_policy(), get, Request, Privacy Policy page - LGPD, terms_of_use()

### Community 28 - "Refinamento — BL-0013 — Busca e padronização das telas de itens"
Cohesion: 0.09
Nodes (23): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Busca local e navegação padronizada, Excluído, Fatia 1.1.1 — Criar contratos TDD e integrar a Lista (+15 more)

### Community 29 - "tests/README.md"
Cohesion: 0.18
Nodes (4): Backlog legado — Sprint 4 — Aprendizado contínuo dos templates, Demandas do backlog ativo, Rastreabilidade das regras de negócio, Rastreabilidade dos fluxos do usuário

### Community 30 - "run.py"
Cohesion: 0.50
Nodes (4): main(), parse_args(), Namespace, Executa o Jaci aplicando migrações antes de iniciar o servidor.

### Community 32 - "docker-entrypoint.sh"
Cohesion: 0.83
Nodes (3): is_server_process(), docker-entrypoint.sh script, write_cron_environment()

### Community 33 - "Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Acompanhamento contínuo do orçamento, Excluído, Fatia 1.1.1 — Implementar o contrato completo da BL-0014 (+13 more)

### Community 46 - "Refinamento — BL-NNNN — Título"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — `<resultado da etapa>`, Excluído, Fatia 1.1.1 — `<resultado pequeno e verificável>` (+13 more)

### Community 47 - "Regras de negócio críticas"
Cohesion: 0.10
Nodes (19): Regras de negócio críticas, RN01, RN02, RN03, RN04, RN05, RN06, RN07 (+11 more)

### Community 48 - "tupa_auth_service.py"
Cohesion: 0.19
Nodes (19): add_unread_count(), Injeta unread_count no request.state para todas as requisições. Lê o cookie de…, create_user(), _credentials(), decode_access_token(), _jwks(), logout(), migrate_user() (+11 more)

### Community 49 - "Fundação PWA e Offline"
Cohesion: 0.11
Nodes (18): BL-004 — Estratégia de Cache, BL-005 a BL-013 — Cache Local e Operações Offline, BL-014 — Fila Local de Operações, BL-015 — Sincronização Automática, BL-016 — Status Detalhado de Sincronização, BL-017 — Retentativa Automática, BL-019 — Resolução de Conflitos, BL-020 — Central de Sincronização (+10 more)

### Community 50 - "Backlog de produção"
Cohesion: 0.14
Nodes (14): Backlog de produção, Checklist de passagem ponta a ponta, Ciclo de vida, Classificações, Entrada rápida, Evidências e dados sensíveis, Git Flow, Itens arquivados (+6 more)

### Community 51 - "Identificação e entrada"
Cohesion: 0.15
Nodes (12): Acompanhamento até produção, BL-0010 — Disponibilizar reset de senha via login e área logada, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 52 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0001 — Completar cobertura e rastreabilidade da operação offline, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 53 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0002 — Adicionar unidades de medida, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 54 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0003 — Disponibilizar histórico de preços por grupo e item, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 55 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0004 — Disponibilizar análise de gastos e dashboard financeiro, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 56 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0005 — Evoluir inteligência de compras, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 57 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0006 — Implementar integrações externas, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 58 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0007 — Replicar backups em armazenamento externo, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 59 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0008 — Disponibilizar autoexclusão e anonimização de conta, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 60 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0009 — Implementar criptografia de dados em repouso, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 61 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0011 — Ampliar cobertura automatizada e testes de UI, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 62 - "Identificação e entrada"
Cohesion: 0.14
Nodes (12): Acompanhamento até produção, BL-0013 — Buscar itens e padronizar categorias nas telas de Lista e Compra, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 63 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0014 — Fixar resumo de orçamento durante a compra, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 64 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-NNNN — Título curto, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 65 - "ExecutionStatus"
Cohesion: 0.10
Nodes (30): ExecutionStatus, RecurrenceType, build_calendar_data(), calculate_next_date(), generate_next_execution(), get_executions_for_date(), get_executions_for_month(), date (+22 more)

### Community 66 - "0002 - Backup automático do PostgreSQL"
Cohesion: 0.25
Nodes (8): 0002 - Backup automático do PostgreSQL, Consequências, Contexto, Decisão, Plano refinado, Progresso, Status, Validação

### Community 67 - "offline.py"
Cohesion: 0.12
Nodes (33): _execution_state(), Finaliza no servidor uma execução encerrada offline., sync_finalize_execution_operation(), complete_item(), create_execution_from_pending(), ensure_execution_is_mutable(), generate_next_execution(), get_execution_display_name() (+25 more)

### Community 68 - "Pricipais Entidades"
Cohesion: 0.22
Nodes (8): Categoria, Execução, Grupo, Item de Execução, Item de Template, Pricipais Entidades, Template, Usuário

### Community 69 - "0001 - Tratamento de datas e timezone"
Cohesion: 0.25
Nodes (7): 0001 - Tratamento de datas e timezone, Antipadrões, Consequências, Contexto, Decisão, Exemplos, Status

### Community 70 - "Aprendizado contínuo dos templates"
Cohesion: 0.25
Nodes (8): Aprendizado contínuo dos templates, BL-029 — Detecção de itens adicionados na execução, BL-030 — Incorporação de itens, BL-031 e BL-032 — Quantidades recorrentes, BL-033 e BL-034 — Observações recorrentes, BL-075 e BL-076 — Orçamentos recorrentes, Configuração por grupo, Sugestões ignoradas

### Community 71 - "Tela Inicial Operacional"
Cohesion: 0.29
Nodes (7): Alertas, Histórico Recente, Indicadores, Objetivo, Offline e Sincronização, Prioridade da Compra Principal, Tela Inicial Operacional

### Community 72 - "FL-08 — Consulta da Agenda e Histórico"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-08 — Consulta da Agenda e Histórico, Fluxo Principal, Objetivo, Resultado Esperado

### Community 73 - "Backups do PostgreSQL"
Cohesion: 0.29
Nodes (7): Agenda e logs, Backups do PostgreSQL, Configuração, Execução manual, Restauração manual em banco isolado, Retenção, Visão geral

### Community 74 - "home_service.py"
Cohesion: 0.09
Nodes (40): agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request, Session (+32 more)

### Community 75 - "Backlog legado do Jaci"
Cohesion: 0.33
Nodes (6): Aprendizado de templates, Backlog legado do Jaci, Edição de execuções agendadas, Entregas concluídas sem identificador BL legado, Mapeamento das fontes abertas migradas, PWA, operação offline e sincronização

### Community 76 - "Edição de execuções agendadas"
Cohesion: 0.33
Nodes (5): Campos editáveis, Edição de execuções agendadas, Notificações e sincronização, Regras, Sincronização offline

### Community 77 - "FL-03 — Geração de Execução"
Cohesion: 0.33
Nodes (6): Atores, FL-03 — Geração de Execução, Fluxo Automático, Fluxo Manual, Objetivo, Resultado Esperado

### Community 78 - "FL-04 — Execução da Compra"
Cohesion: 0.33
Nodes (6): Atores, Cenários Alternativos, FL-04 — Execução da Compra, Fluxo Principal, Objetivo, Resultado Esperado

### Community 79 - "make_user"
Cohesion: 0.11
Nodes (65): add_item_to_execution(), create_execution_from_template(), finalize_execution(), Cria uma execução a partir de um template, copiando seus itens., Adiciona item à execução sem alterar o template associado., Finaliza a execução. Se discard_pending=True, remove itens não concluídos. Se…, add_item_to_template(), create_template() (+57 more)

### Community 80 - "FL-09 — Operação Offline"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-09 — Operação Offline, Fluxo Principal, Objetivo, Resultado Esperado

### Community 81 - "Refinamento — BL-0016 — Botão flutuante para adicionar itens"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Adição contextual por modal nas telas mutáveis, Excluído, Fatia 1.1.1 — Contratos TDD e fluxo modal completo online/offline (+13 more)

### Community 82 - "FL-01 — Primeiro Acesso e Onboarding"
Cohesion: 0.40
Nodes (5): Atores, FL-01 — Primeiro Acesso e Onboarding, Fluxo Principal, Objetivo, Resultado Esperado

### Community 83 - "notification_service.py"
Cohesion: 0.11
Nodes (28): Notification, handle_mark_all_read(), handle_mark_read(), list_notifications(), get, post, Request, Session (+20 more)

### Community 84 - "Estratégia de Banco de Dados"
Cohesion: 0.33
Nodes (5): Ambientes, Backups de produção, Estratégia de Banco de Dados, Migração de Dados, Migrações

### Community 85 - "ensure_schema_compatibility"
Cohesion: 0.50
Nodes (4): ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., apply_migrations(), Aplica migrações Alembic e adota bancos SQLite legados.

### Community 87 - "FL-06 — Aprendizado do Template"
Cohesion: 0.33
Nodes (6): FL-06 — Aprendizado do Template, Fluxo Principal, Objetivo, Pré-condições, Resultado Esperado, Tipos de Sugestão

### Community 88 - "user-flows.md"
Cohesion: 0.08
Nodes (23): Atores, Atores, Atores, FL-02 — Criação de Template, FL-05 — Compra Colaborativa, FL-07 — Gestão de Grupos, FL-10 — Home Operacional, Fluxo Crítico do Produto (+15 more)

### Community 89 - "item-add-modal.js"
Cohesion: 0.27
Nodes (15): completeSuccess(), finishClose(), focusableElements(), formFor(), hideLocalModal(), hideModal(), initialize(), initializeModal() (+7 more)

### Community 90 - "Refinamento — BL-0017 — Nome da execução avulsa"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Nome exclusivo para compra sem lista, Excluído, Fatia 1.1.1 — Contratos TDD e implementação completa (+13 more)

### Community 91 - "handle_setup_profile"
Cohesion: 0.14
Nodes (19): handle_change_password(), handle_setup_profile(), handle_update_profile(), password_login(), post, Response, Session, Magic link de login foi substituído pelo Tupã. (+11 more)

### Community 92 - "config.py"
Cohesion: 0.17
Nodes (10): get_settings(), _build_invite_email(), _build_login_email(), _build_magic_link(), Template HTML para e-mail de convite para grupo., Monta a URL completa do magic link., Envia e-mail com magic link. Se SMTP não configurado, faz log do link (modo…, Template HTML para e-mail de login. (+2 more)

### Community 93 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0016 — Disponibilizar botão flutuante para adicionar itens, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 94 - "sync_conflict_audit_service.py"
Cohesion: 0.32
Nodes (11): SyncConflictAudit, offline_conflict_history(), Histórico auditável de conflitos de sincronização dos grupos do usuário., create_conflict_audit(), _jsonable(), list_conflict_audits(), Any, BaseModel (+3 more)

### Community 95 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0017 — Permitir informar um nome para execução avulsa, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 96 - "read"
Cohesion: 0.33
Nodes (10): Path, read(), test_both_modal_pages_load_the_local_cached_controller(), test_fab_and_modal_styles_respect_safe_areas_and_local_fallback(), test_local_modal_controller_preserves_scroll_focus_and_keyboard_behavior(), test_modal_controller_closes_only_after_online_or_offline_success(), test_modal_pages_keep_the_single_form_available_without_javascript(), test_mutable_execution_exposes_one_modal_form_and_preserves_offline_contract() (+2 more)

### Community 97 - "auth_service.py"
Cohesion: 0.31
Nodes (9): authenticate_with_password(), get_or_create_tupa_user(), Session, Associa uma identidade Tupã ao perfil local do Jaci., Autentica no Tupã e carrega o perfil local., Cria a identidade no Tupã e o perfil local no Jaci., register_with_password(), test_first_access_creates_default_home_and_categories() (+1 more)

### Community 99 - "test_future_user_flows.py"
Cohesion: 0.43
Nodes (6): future_flow, Contratos dos fluxos documentados e dos fluxos futuros ainda pendentes., test_fl08_spending_analysis_uses_completed_executions_only(), test_fl09_offline_operation_is_queued_before_remote_sync(), test_fl09_reconnection_synchronizes_queued_operations_without_data_loss(), test_fl09_sync_conflict_requires_explicit_resolution_and_preserves_both_versions()

### Community 100 - "datetime.py"
Cohesion: 0.14
Nodes (18): Base, Category, TemplateLearningDismissal, TemplateItem, create_category(), get_categories_by_group(), move_category(), Session (+10 more)

## Knowledge Gaps
- **465 isolated node(s):** `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script`, `Projeto: Jaci`, `Princípios do Produto` (+460 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `make_group`, `template_service.py`, `Execution`, `auth.py`, `executions.py`, `get_category_by_id`, `main.py`, `build_offline_snapshot`, `test_pwa.py`, `sync_center`, `tupa_auth_service.py`, `ExecutionStatus`, `offline.py`, `home_service.py`, `make_user`, `notification_service.py`, `handle_setup_profile`, `sync_conflict_audit_service.py`, `auth_service.py`, `datetime.py`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `Execution` connect `Execution` to `make_group`, `ExecutionStatus`, `template_service.py`, `offline.py`, `datetime.py`, `executions.py`, `home_service.py`, `build_offline_snapshot`, `make_user`, `notification_service.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `Refinamento — BL-0016 — Botão flutuante para adicionar itens` connect `Refinamento — BL-0016 — Botão flutuante para adicionar itens` to `tests/README.md`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `User` (e.g. with `Base` and `AddExecutionItemOperation`) actually correct?**
  _`User` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 104 inferred relationships involving `make_user()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_user()` has 104 INFERRED edges - model-reasoned connections that need verification._
- **Are the 103 inferred relationships involving `make_group()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_group()` has 103 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script` to the rest of the system?**
  _465 weakly-connected nodes found - possible documentation gaps or missing edges._