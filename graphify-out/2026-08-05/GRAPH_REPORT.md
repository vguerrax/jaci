# Graph Report - jaci  (2026-08-05)

## Corpus Check
- 142 files · ~149,860 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1884 nodes · 4584 edges · 100 communities (96 shown, 4 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 319 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0fd7aaaa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item
- offline-cache.js
- template_service.py
- Execution
- Category
- template_learning_service.py
- executions.py
- get_category_by_id
- Identificação e entrada
- main.py
- Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX
- Refinamento — BL-0020 — Bloquear renomeação de item vinculado ao template
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
- home_service.py
- run.py
- docker-entrypoint.sh
- Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra
- backup_database.sh
- app/__init__.py
- publish.sh
- backlog/README.md
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
- agenda.py
- 0002 - Backup automático do PostgreSQL
- FL-07 — Gestão de Grupos
- Pricipais Entidades
- 0001 - Tratamento de datas e timezone
- Aprendizado contínuo dos templates
- Tela Inicial Operacional
- FL-08 — Consulta da Agenda e Histórico
- BL-0007-replicacao-externa-backups.md
- format_local_date
- Backlog legado do Jaci
- Edição de execuções agendadas
- FL-03 — Geração de Execução
- FL-04 — Execução da Compra
- make_user
- Identificação e entrada
- Refinamento — BL-0016 — Botão flutuante para adicionar itens
- FL-01 — Primeiro Acesso e Onboarding
- notification_service.py
- Identificação e entrada
- ensure_schema_compatibility
- overview.md
- FL-06 — Aprendizado do Template
- user-flows.md
- item-add-modal.js
- Refinamento — BL-0017 — Nome da execução avulsa
- auth.py
- config.py
- Identificação e entrada
- add_unread_count
- Identificação e entrada
- test_item_add_fab.py
- calculate_next_date
- FL-02 — Criação de Template
- execution_service.py

## God Nodes (most connected - your core abstractions)
1. `User` - 145 edges
2. `make_user()` - 115 edges
3. `make_group()` - 114 edges
4. `create_template()` - 87 edges
5. `create_execution_from_template()` - 78 edges
6. `Execution` - 75 edges
7. `add_item_to_template()` - 58 edges
8. `ExecutionItem` - 54 edges
9. `Group` - 45 edges
10. `ExecutionStatus` - 37 edges

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

### Community 0 - "Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Restaurar o empilhamento dos modais de item, Excluído, Fatia 1.1.1 — Proteger a ordem de camadas e o cache PWA (+13 more)

### Community 1 - "offline-cache.js"
Cohesion: 0.05
Nodes (113): applyPersistedOfflineItemState(), auditCard(), buildConflict(), buildQueuedOperation(), calculateExecutionTotal(), classifyOperation(), clearOfflineItemIndicators(), clearOfflineItemIndicatorsWhenSynced() (+105 more)

### Community 2 - "template_service.py"
Cohesion: 0.09
Nodes (57): create_template_page(), edit_template_page(), _get_template_context(), _get_template_items_fragment(), handle_add_item(), handle_create_template(), handle_delete_template(), handle_edit_item() (+49 more)

### Community 3 - "Execution"
Cohesion: 0.05
Nodes (88): Execution, ExecutionItem, Calcula o valor total do item (qtd * preço unitário)., SyncConflictAudit, AddExecutionItemOperation, ConflictResolutionOperation, _execution_state(), ExecutionItemOperation (+80 more)

### Community 4 - "Category"
Cohesion: 0.20
Nodes (14): Category, authenticate_with_password(), get_or_create_tupa_user(), Session, Associa uma identidade Tupã ao perfil local do Jaci., Autentica no Tupã e carrega o perfil local., Cria a identidade no Tupã e o perfil local no Jaci., Completa os dados locais do perfil. (+6 more)

### Community 5 - "template_learning_service.py"
Cohesion: 0.14
Nodes (26): TemplateLearningDismissal, Template, analyze_template_history(), apply_template_suggestions(), dismiss_template_suggestions(), _dismissal_key_for_suggestion(), _dismissal_value_for_suggestion(), _dismissed_keys() (+18 more)

### Community 6 - "executions.py"
Cohesion: 0.09
Nodes (63): Group, close_execution_page(), complete_item_form(), _completed_page(), create_execution_page(), edit_item_form(), execution_detail(), execution_items_fragment() (+55 more)

### Community 7 - "get_category_by_id"
Cohesion: 0.09
Nodes (37): create_category_page(), delete_category_confirm_page(), edit_category_page(), handle_create_category(), handle_delete_category(), handle_edit_category(), handle_move_category(), handle_uncategorized_position() (+29 more)

### Community 8 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0018 — Corrigir backdrop sobre o modal de completar item, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 9 - "main.py"
Cohesion: 0.14
Nodes (24): get_db(), set_sqlite_pragma(), get_active_group(), get_current_user(), get_current_user_ws(), get_unread_notification_count(), Request, Session (+16 more)

### Community 10 - "Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX"
Cohesion: 0.05
Nodes (40): Acompanhamento até produção, BL-0012 — Gestão documental compartilhada dos projetos VGX, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+32 more)

### Community 11 - "Refinamento — BL-0020 — Bloquear renomeação de item vinculado ao template"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Proteger a identidade do item online e offline, Excluído, Fatia 1.1.1 — Contratos TDD e implementação completa (+13 more)

### Community 12 - "test_pwa.py"
Cohesion: 0.17
Nodes (10): Serve o service worker na raiz para permitir cache offline da aplicação., Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores., service_worker(), web_app_manifest(), png_dimensions(), Path, test_base_template_declares_global_loading_indicator(), test_base_template_declares_manifest_ios_support_and_install_action() (+2 more)

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
Cohesion: 0.18
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
Cohesion: 0.12
Nodes (42): User, create_group_page(), group_detail(), handle_create_group(), handle_edit_group(), handle_invite(), handle_remove_member(), handle_switch_group() (+34 more)

### Community 25 - "🌙 Jaci"
Cohesion: 0.07
Nodes (28): 1. Clone o repositório, 3. Instale as dependências, 4. Execute, Backup automático do PostgreSQL, Banco de dados e migrações, Com Caddy (HTTPS automático), 📧 Configuração de e-mail, Configure o ambiente (+20 more)

### Community 26 - "privacy_policy"
Cohesion: 0.47
Nodes (5): privacy_policy(), get, Request, Privacy Policy page - LGPD, terms_of_use()

### Community 28 - "Refinamento — BL-0013 — Busca e padronização das telas de itens"
Cohesion: 0.09
Nodes (23): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Busca local e navegação padronizada, Excluído, Fatia 1.1.1 — Criar contratos TDD e integrar a Lista (+15 more)

### Community 29 - "home_service.py"
Cohesion: 0.23
Nodes (19): _as_utc(), build_home_dashboard(), get_home_alerts(), get_home_metrics(), get_priority_execution(), get_recent_history(), _local_day_start_utc(), datetime (+11 more)

### Community 30 - "run.py"
Cohesion: 0.50
Nodes (4): main(), parse_args(), Namespace, Executa o Jaci aplicando migrações antes de iniciar o servidor.

### Community 32 - "docker-entrypoint.sh"
Cohesion: 0.83
Nodes (3): is_server_process(), docker-entrypoint.sh script, write_cron_environment()

### Community 33 - "Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Acompanhamento contínuo do orçamento, Excluído, Fatia 1.1.1 — Implementar o contrato completo da BL-0014 (+13 more)

### Community 45 - "backlog/README.md"
Cohesion: 0.17
Nodes (4): Backlog legado — Sprint 4 — Aprendizado contínuo dos templates, Demandas do backlog ativo, Rastreabilidade das regras de negócio, Rastreabilidade dos fluxos do usuário

### Community 46 - "Refinamento — BL-NNNN — Título"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — `<resultado da etapa>`, Excluído, Fatia 1.1.1 — `<resultado pequeno e verificável>` (+13 more)

### Community 47 - "Regras de negócio críticas"
Cohesion: 0.10
Nodes (19): Regras de negócio críticas, RN01, RN02, RN03, RN04, RN05, RN06, RN07 (+11 more)

### Community 48 - "tupa_auth_service.py"
Cohesion: 0.24
Nodes (16): create_user(), _credentials(), decode_access_token(), _jwks(), logout(), migrate_user(), Any, refresh() (+8 more)

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
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0013 — Buscar itens e padronizar categorias nas telas de Lista e Compra, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 63 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0014 — Fixar resumo de orçamento durante a compra, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 64 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-NNNN — Título curto, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 65 - "agenda.py"
Cohesion: 0.14
Nodes (29): agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request, Session (+21 more)

### Community 66 - "0002 - Backup automático do PostgreSQL"
Cohesion: 0.22
Nodes (8): 0002 - Backup automático do PostgreSQL, Consequências, Contexto, Decisão, Plano refinado, Progresso, Status, Validação

### Community 67 - "FL-07 — Gestão de Grupos"
Cohesion: 0.40
Nodes (5): Atores, FL-07 — Gestão de Grupos, Fluxo Principal, Objetivo, Resultado Esperado

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

### Community 73 - "BL-0007-replicacao-externa-backups.md"
Cohesion: 0.13
Nodes (12): Ambientes, Backups de produção, Estratégia de Banco de Dados, Migração de Dados, Migrações, Agenda e logs, Backups do PostgreSQL, Configuração (+4 more)

### Community 74 - "format_local_date"
Cohesion: 0.28
Nodes (7): localdate_filter(), localdatetime_filter(), format_local_date(), format_local_datetime(), date, Convert UTC datetime to local timezone for display, Convert UTC datetime to local date only

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
Cohesion: 0.05
Nodes (141): RecurrenceType, generate_next_execution(), Gera a próxima execução do ciclo, se aplicável. Condições: - Execução vinculada…, add_item_to_execution(), complete_item(), create_execution_from_template(), create_execution_standalone(), finalize_execution() (+133 more)

### Community 80 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0019 — Manter sessão autenticada por oito horas de inatividade, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 81 - "Refinamento — BL-0016 — Botão flutuante para adicionar itens"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Adição contextual por modal nas telas mutáveis, Excluído, Fatia 1.1.1 — Contratos TDD e fluxo modal completo online/offline (+13 more)

### Community 82 - "FL-01 — Primeiro Acesso e Onboarding"
Cohesion: 0.40
Nodes (5): Atores, FL-01 — Primeiro Acesso e Onboarding, Fluxo Principal, Objetivo, Resultado Esperado

### Community 83 - "notification_service.py"
Cohesion: 0.11
Nodes (28): Notification, handle_mark_all_read(), handle_mark_read(), list_notifications(), get, post, Request, Session (+20 more)

### Community 84 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0020 — Bloquear renomeação de item vinculado ao template, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 85 - "ensure_schema_compatibility"
Cohesion: 0.50
Nodes (4): ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., apply_migrations(), Aplica migrações Alembic e adota bancos SQLite legados.

### Community 87 - "FL-06 — Aprendizado do Template"
Cohesion: 0.33
Nodes (6): FL-06 — Aprendizado do Template, Fluxo Principal, Objetivo, Pré-condições, Resultado Esperado, Tipos de Sugestão

### Community 88 - "user-flows.md"
Cohesion: 0.10
Nodes (19): Atores, Atores, Estado e rastreabilidade, FL-05 — Compra Colaborativa, FL-09 — Operação Offline, FL-10 — Home Operacional, Fluxo Crítico do Produto, Fluxo Principal (+11 more)

### Community 89 - "item-add-modal.js"
Cohesion: 0.27
Nodes (15): completeSuccess(), finishClose(), focusableElements(), formFor(), hideLocalModal(), hideModal(), initialize(), initializeModal() (+7 more)

### Community 90 - "Refinamento — BL-0017 — Nome da execução avulsa"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Nome exclusivo para compra sem lista, Excluído, Fatia 1.1.1 — Contratos TDD e implementação completa (+13 more)

### Community 91 - "auth.py"
Cohesion: 0.08
Nodes (45): handle_change_password(), handle_setup_profile(), handle_update_profile(), login_error_page(), login_page(), login_sent_page(), logout(), password_login() (+37 more)

### Community 92 - "config.py"
Cohesion: 0.17
Nodes (10): get_settings(), _build_invite_email(), _build_login_email(), _build_magic_link(), Template HTML para e-mail de convite para grupo., Monta a URL completa do magic link., Envia e-mail com magic link. Se SMTP não configurado, faz log do link (modo…, Template HTML para e-mail de login. (+2 more)

### Community 93 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0016 — Disponibilizar botão flutuante para adicionar itens, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 94 - "add_unread_count"
Cohesion: 0.29
Nodes (8): add_unread_count(), health_check(), home(), get, Request, Painel operacional do grupo ativo., Injeta unread_count no request.state para todas as requisições. Lê o cookie de…, middleware

### Community 95 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0017 — Permitir informar um nome para execução avulsa, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 96 - "test_item_add_fab.py"
Cohesion: 0.28
Nodes (12): Path, read(), test_both_modal_pages_load_the_local_cached_controller(), test_fab_and_modal_styles_respect_safe_areas_and_local_fallback(), test_local_modal_controller_preserves_scroll_focus_and_keyboard_behavior(), test_managed_item_modals_stay_above_backdrop_and_page_actions(), test_modal_controller_closes_only_after_online_or_offline_success(), test_modal_pages_keep_the_single_form_available_without_javascript() (+4 more)

### Community 97 - "calculate_next_date"
Cohesion: 0.40
Nodes (5): calculate_next_date(), Calcula a próxima data baseada na recorrência. Usado para geração automática de…, generate_next_execution(), parametrize, test_supported_recurrences_calculate_the_next_cycle()

### Community 98 - "FL-02 — Criação de Template"
Cohesion: 0.40
Nodes (5): Atores, FL-02 — Criação de Template, Fluxo Principal, Objetivo, Resultado Esperado

### Community 100 - "execution_service.py"
Cohesion: 0.25
Nodes (7): Base, ExecutionStatus, TemplateItem, _iso(), datetime, DeclarativeBase, str

## Knowledge Gaps
- **518 isolated node(s):** `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script`, `Projeto: Jaci`, `Princípios do Produto` (+513 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `agenda.py`, `template_service.py`, `Execution`, `execution_service.py`, `Category`, `executions.py`, `get_category_by_id`, `calculate_next_date`, `main.py`, `make_user`, `tupa_auth_service.py`, `notification_service.py`, `sync_center`, `auth.py`, `add_unread_count`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `Base` and `AddExecutionItemOperation`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 112 inferred relationships involving `make_user()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_user()` has 112 INFERRED edges - model-reasoned connections that need verification._
- **Are the 111 inferred relationships involving `make_group()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_group()` has 111 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script` to the rest of the system?**
  _518 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `offline-cache.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05067466266866567 - nodes in this community are weakly interconnected._