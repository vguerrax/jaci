# Graph Report - jaci  (2026-11-11)

## Corpus Check
- 227 files · ~218,083 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2796 nodes · 6453 edges · 162 communities (152 shown, 10 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 441 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a5594761`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item
- offline-cache.js
- Refinamento — BL-0021 — API externa para gestão de execuções
- Identificação e entrada
- make_user
- test_pwa.py
- template_service.py
- categories.py
- Identificação e entrada
- datetime.py
- Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX
- Refinamento — BL-0020 — Bloquear renomeação de item vinculado ao template
- Refinamento — BL-0025 — Preparar e publicar versão 1.3.0
- Refinamento — BL-0028 — AUTH_MOCK como bypass local do Tupã
- AGENTS.md
- execution-budget.js
- backlog/README.md
- item-filter.js
- Refinamento — BL-0015 — Adicionar item como comprado durante execução
- sync_center
- service-worker.js
- read
- loading-indicator.js
- sync-status.js
- get_group_by_id
- 🌙 Jaci
- privacy_policy
- Refinamento — BL-0013 — Busca e padronização das telas de itens
- tupa_auth_service.py
- run.py
- docker-entrypoint.sh
- Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra
- backup_database.sh
- app/__init__.py
- publish.sh
- tests/README.md
- Refinamento — BL-NNNN — Título
- Regras de negócio críticas
- agenda.py
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
- get_execution_totals
- Refinamento — BL-0027 — Incorporação sem categoria
- Identificação e entrada
- Pricipais Entidades
- 0001 - Tratamento de datas e timezone
- Aprendizado contínuo dos templates
- Tela Inicial Operacional
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Backlog legado do Jaci
- Edição de execuções agendadas
- SessionExpired
- FL-05 — Compra Colaborativa
- run
- Identificação e entrada
- Refinamento — BL-0016 — Botão flutuante para adicionar itens
- FL-04 — Execução da Compra
- utils/__init__.py
- Identificação e entrada
- Identificação e entrada
- FL-08 — Consulta da Agenda e Histórico
- session_http.py
- test_purchase_playwright.py
- item-add-modal.js
- Refinamento — BL-0017 — Nome da execução avulsa
- auth.py
- offline_queue.test.cjs
- Identificação e entrada
- Settings
- Identificação e entrada
- test_item_add_fab.py
- executions.py
- Refinamento — BL-0011 — Cobertura, navegador e CI
- Refinamento — BL-0026 — Ferramentas e ambiente de testes
- Identificação e entrada
- ConnectionManager
- Execution
- test_test_environment.py
- Refinamento — BL-0009 — Criptografia em repouso — 1.5.0
- PasswordProvider
- password_service.py
- Refinamento — BL-0001 — Rastreabilidade da operação offline
- Identificação e entrada
- test_postgresql_backup.py
- package.json
- get_settings
- ValueError
- migrate_sqlite_to_postgres.py
- 0002 - Backup automático do PostgreSQL
- items/BL-0007-replicacao-externa-backups.md
- test_coverage_runner.py
- test_password_http.py
- Planejamento de releases após a 1.3.0
- setup_test_env.sh
- Refinamento — BL-0007 — Cópia externa por SSH/SFTP — 1.5.0
- run_test_server.sh
- run_tests.sh
- run_ui_tests.sh
- routers/passwords.py
- Refinamento — BL-0019 — Sessão por oito horas de inatividade — 1.5.0
- FL-09 — Operação Offline
- FL-06 — Aprendizado do Template
- User
- test_offline_queue_node.py
- Refinamento — BL-0010 — Recuperação e troca de senha — 1.5.0
- Refinamento da versão 1.5.0 — Acesso à conta e continuidade da sessão
- auth_service.py
- test_tupa_session_provider.py
- test_password_recovery.py
- password_cache.test.cjs
- FL-01 — Primeiro Acesso e Onboarding
- execution_service.py
- FL-03 — Geração de Execução
- FL-10 — Home Operacional
- password_privacy.py
- request_recovery
- repositories/__init__.py
- test_session_auth_flow.py
- Provider
- execution_ws_handler
- .normalize_database_url
- FL-07 — Gestão de Grupos
- FL-02 — Criação de Template
- format_local_date
- overview.md
- Fluxos Principais do Usuário — Jaci

## God Nodes (most connected - your core abstractions)
1. `User` - 159 edges
2. `make_user()` - 136 edges
3. `make_group()` - 130 edges
4. `create_template()` - 101 edges
5. `create_execution_from_template()` - 92 edges
6. `Execution` - 78 edges
7. `add_item_to_template()` - 65 edges
8. `ExecutionItem` - 58 edges
9. `get_settings()` - 53 edges
10. `Group` - 50 edges

## Surprising Connections (you probably didn't know these)
- `test_real_login_still_requires_password()` --indirect_call--> `get_db()`  [INFERRED]
  tests/test_auth_mock_bypass.py → app/database.py
- `Provider` --uses--> `AccessSession`  [INFERRED]
  tests/test_session_auth_flow.py → app/models/access_session.py
- `Provider` --uses--> `SessionExpired`  [INFERRED]
  tests/test_session_auth_flow.py → app/services/session_policy.py
- `Provider` --uses--> `AccessTokenExpired`  [INFERRED]
  tests/test_session_auth_flow.py → app/services/session_policy.py
- `Provider` --uses--> `SessionUnavailable`  [INFERRED]
  tests/test_session_auth_flow.py → app/services/session_policy.py

## Import Cycles
- None detected.

## Communities (162 total, 10 thin omitted)

### Community 0 - "Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Restaurar o empilhamento dos modais de item, Excluído, Fatia 1.1.1 — Proteger a ordem de camadas e o cache PWA (+13 more)

### Community 1 - "offline-cache.js"
Cohesion: 0.05
Nodes (113): applyPersistedOfflineItemState(), auditCard(), buildConflict(), buildQueuedOperation(), calculateExecutionTotal(), classifyOperation(), clearOfflineItemIndicators(), clearOfflineItemIndicatorsWhenSynced() (+105 more)

### Community 2 - "Refinamento — BL-0021 — API externa para gestão de execuções"
Cohesion: 0.06
Nodes (32): Autenticação e escopo, Cenários TDD, Contrato HTTP v1, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Persistir identidade, concorrência e rastreabilidade (+24 more)

### Community 3 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0027 — Incorporar item sem categoria ao finalizar compra, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 4 - "make_user"
Cohesion: 0.05
Nodes (150): RecurrenceType, generate_next_execution(), Gera a próxima execução do ciclo, se aplicável. Condições: - Execução vinculada…, add_item_to_execution(), complete_item(), create_execution_from_template(), create_execution_standalone(), finalize_execution() (+142 more)

### Community 5 - "test_pwa.py"
Cohesion: 0.15
Nodes (12): health_check(), get, Serve o service worker na raiz para permitir cache offline da aplicação., Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores., service_worker(), web_app_manifest(), png_dimensions(), Path (+4 more)

### Community 6 - "template_service.py"
Cohesion: 0.05
Nodes (90): TemplateLearningDismissal, Template, TemplateItem, create_template_page(), edit_template_page(), _get_template_context(), _get_template_items_fragment(), handle_add_item() (+82 more)

### Community 7 - "categories.py"
Cohesion: 0.12
Nodes (37): create_category_page(), delete_category_confirm_page(), edit_category_page(), handle_create_category(), handle_delete_category(), handle_edit_category(), handle_move_category(), handle_uncategorized_position() (+29 more)

### Community 8 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0018 — Corrigir backdrop sobre o modal de completar item, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 9 - "datetime.py"
Cohesion: 0.13
Nodes (16): Base, ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., set_sqlite_pragma(), AccessSession, Sessão do navegador, sem senha nem token em claro., AuthRateLimit, Category (+8 more)

### Community 10 - "Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX"
Cohesion: 0.05
Nodes (40): Acompanhamento até produção, BL-0012 — Gestão documental compartilhada dos projetos VGX, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+32 more)

### Community 11 - "Refinamento — BL-0020 — Bloquear renomeação de item vinculado ao template"
Cohesion: 0.08
Nodes (24): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Proteger a identidade do item online e offline, Etapa 2 — Fechar o ciclo de identidade entre execução e planejamento, Excluído (+16 more)

### Community 12 - "Refinamento — BL-0025 — Preparar e publicar versão 1.3.0"
Cohesion: 0.06
Nodes (33): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Encerramento da release — 2026-10-28, Escopo, Estratégia de validação, Etapa 1 — Preparar o candidato, Etapa 2 — Validar e obter aceite (+25 more)

### Community 13 - "Refinamento — BL-0028 — AUTH_MOCK como bypass local do Tupã"
Cohesion: 0.10
Nodes (20): Aprovação e início, Cenários TDD, CI remoto / entrega para integração, Encerramento da 1.4.0, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Ajustar contrato do AUTH_MOCK, Fatia 1.1 — Adaptador e identidade local (+12 more)

### Community 14 - "AGENTS.md"
Cohesion: 0.05
Nodes (39): Arquitetura, Backend, Backend, Banco de Dados, Cache e Mensageria, Categoria, Conceitos do Domínio, Concorrência é controlada por bloqueio otimista. (+31 more)

### Community 15 - "execution-budget.js"
Cohesion: 0.29
Nodes (15): alertMessage(), applyVisualState(), budgetBand(), ensureToastContainer(), formatMoney(), handleRemoteAlerts(), init(), refreshFromDocument() (+7 more)

### Community 17 - "item-filter.js"
Cohesion: 0.30
Nodes (13): apply(), expandMatchingGroup(), formatMoney(), initAll(), initRoot(), normalize(), restoreForcedCollapse(), scheduleApply() (+5 more)

### Community 18 - "Refinamento — BL-0015 — Adicionar item como comprado durante execução"
Cohesion: 0.06
Nodes (34): Acompanhamento até produção, BL-0015 — Adicionar item como comprado durante execução, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+26 more)

### Community 19 - "sync_center"
Cohesion: 0.23
Nodes (9): get, Request, Session, Central local para visualização e resolução da fila de sincronização., sync_center(), make_request(), Request, test_sync_center_renders_local_queue_management_shell() (+1 more)

### Community 20 - "service-worker.js"
Cohesion: 0.18
Nodes (12): ACTIVE_CACHES, cacheOwnerPage(), guardObserved(), isSensitiveAuthRequest(), isShellAsset(), legacyCache(), navigationUpdate, networkFirstApi() (+4 more)

### Community 21 - "read"
Cohesion: 0.30
Nodes (11): Path, read(), test_clear_and_collapse_controls_share_a_safe_click_handler(), test_completed_execution_is_searchable_collapsible_and_read_only(), test_hidden_filter_rows_override_bootstrap_display_utilities(), test_mutable_execution_exposes_filter_and_visible_financial_metadata(), test_shared_item_filter_controls_rows_groups_counts_and_empty_state(), test_shared_item_filter_normalizes_and_matches_names_locally() (+3 more)

### Community 22 - "loading-indicator.js"
Cohesion: 0.33
Nodes (7): beginRequest(), endRequest(), isPlainLeftClick(), requestCount(), scheduleHide(), shouldShowForLink(), show()

### Community 23 - "sync-status.js"
Cohesion: 0.42
Nodes (8): failSync(), finishSync(), formatDateTime(), render(), renderDetails(), setState(), startSync(), waitForRetry()

### Community 24 - "get_group_by_id"
Cohesion: 0.12
Nodes (33): create_group_page(), group_detail(), handle_create_group(), handle_edit_group(), handle_invite(), handle_remove_member(), handle_switch_group(), list_groups() (+25 more)

### Community 25 - "🌙 Jaci"
Cohesion: 0.06
Nodes (33): 1. Clone o repositório, 3. Instale as dependências, 4. Execute, Ambiente sintético de testes (BL-0026), AUTH_MOCK — bypass do Tupã (BL-0028), Backup automático do PostgreSQL, Banco de dados e migrações, CI no GitHub (+25 more)

### Community 26 - "privacy_policy"
Cohesion: 0.47
Nodes (5): privacy_policy(), get, Request, Privacy Policy page - LGPD, terms_of_use()

### Community 28 - "Refinamento — BL-0013 — Busca e padronização das telas de itens"
Cohesion: 0.09
Nodes (23): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Busca local e navegação padronizada, Excluído, Fatia 1.1.1 — Criar contratos TDD e integrar a Lista (+15 more)

### Community 29 - "tupa_auth_service.py"
Cohesion: 0.15
Nodes (32): _decode(), decode_access_token(), _error(), _hash(), logout(), Bypass Tupã para usuários locais, habilitado somente por APP_ENV=test/AUTH_MOCK., refresh(), _runtime() (+24 more)

### Community 30 - "run.py"
Cohesion: 0.50
Nodes (4): main(), parse_args(), Namespace, Executa o Jaci aplicando migrações antes de iniciar o servidor.

### Community 32 - "docker-entrypoint.sh"
Cohesion: 0.83
Nodes (3): is_server_process(), docker-entrypoint.sh script, write_cron_environment()

### Community 33 - "Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Acompanhamento contínuo do orçamento, Excluído, Fatia 1.1.1 — Implementar o contrato completo da BL-0014 (+13 more)

### Community 45 - "tests/README.md"
Cohesion: 0.12
Nodes (10): Backlog legado — Sprint 4 — Aprendizado contínuo dos templates, Bypass local AUTH_MOCK — BL-0028, Cobertura Python — BL-0011, Contratos offline FL-09 — BL-0001, Demandas de backups abortadas — 2026-11-10, Demandas do backlog com cobertura rastreada, Navegador — BL-0011, Rastreabilidade das regras de negócio (+2 more)

### Community 46 - "Refinamento — BL-NNNN — Título"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — `<resultado da etapa>`, Excluído, Fatia 1.1.1 — `<resultado pequeno e verificável>` (+13 more)

### Community 47 - "Regras de negócio críticas"
Cohesion: 0.10
Nodes (19): Regras de negócio críticas, RN01, RN02, RN03, RN04, RN05, RN06, RN07 (+11 more)

### Community 48 - "agenda.py"
Cohesion: 0.10
Nodes (37): agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request, Session (+29 more)

### Community 49 - "Fundação PWA e Offline"
Cohesion: 0.10
Nodes (21): BL-004 — Estratégia de Cache, BL-005 a BL-013 — Cache Local e Operações Offline, BL-014 — Fila Local de Operações, BL-015 — Sincronização Automática, BL-016 — Status Detalhado de Sincronização, BL-017 — Retentativa Automática, BL-019 — Resolução de Conflitos, BL-020 — Central de Sincronização (+13 more)

### Community 50 - "Backlog de produção"
Cohesion: 0.11
Nodes (18): Backlog de produção, Checklist de passagem ponta a ponta, Ciclo de vida, Classificações, Decisão operacional de backups — 2026-11-10, Dependência externa publicada — 2026-11-11, Entrada rápida, Evidências e dados sensíveis (+10 more)

### Community 51 - "Identificação e entrada"
Cohesion: 0.14
Nodes (14): Acompanhamento até produção, BL-0010 — Disponibilizar reset de senha via login e área logada, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+6 more)

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
Nodes (12): Acompanhamento até produção, BL-0006 — Exportar compras para calendário e compartilhar listas, compras e convites, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 58 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0007 — Replicar backups em armazenamento externo, Comportamento esperado, Comportamento observado, Decisão de encerramento, Evidências sanitizadas, Histórico, Identificação e entrada (+4 more)

### Community 59 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0008 — Disponibilizar autoexclusão e anonimização de conta, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 60 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0009 — Implementar criptografia de dados em repouso, Comportamento esperado, Comportamento observado, Decisão de encerramento, Evidências sanitizadas, Histórico, Identificação e entrada (+4 more)

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

### Community 65 - "get_execution_totals"
Cohesion: 0.21
Nodes (21): get_execution_totals(), Calcula totais da execução., _as_utc(), build_home_dashboard(), get_home_alerts(), get_home_metrics(), get_priority_execution(), get_recent_history() (+13 more)

### Community 66 - "Refinamento — BL-0027 — Incorporação sem categoria"
Cohesion: 0.15
Nodes (12): Cenários TDD, Encerramento da 1.4.0, Escopo e riscos, Estratégia de validação, Etapa 1 / Ticket 1 / Fatia 1.1 — Normalizar o sentinela, Fechamento, Objetivo e critérios de sucesso, Plano de implementação (+4 more)

### Community 67 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0021 — Expor API externa para criar e editar execuções, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 68 - "Pricipais Entidades"
Cohesion: 0.22
Nodes (8): Categoria, Execução, Grupo, Item de Execução, Item de Template, Pricipais Entidades, Template, Usuário

### Community 69 - "0001 - Tratamento de datas e timezone"
Cohesion: 0.29
Nodes (7): 0001 - Tratamento de datas e timezone, Antipadrões, Consequências, Contexto, Decisão, Exemplos, Status

### Community 70 - "Aprendizado contínuo dos templates"
Cohesion: 0.22
Nodes (9): Aprendizado contínuo dos templates, BL-029 — Detecção de itens adicionados na execução, BL-030 — Incorporação de itens, BL-031 e BL-032 — Quantidades recorrentes, BL-033 e BL-034 — Observações recorrentes, BL-075 e BL-076 — Orçamentos recorrentes, Configuração por grupo, Identidade do item após a primeira compra (+1 more)

### Community 71 - "Tela Inicial Operacional"
Cohesion: 0.29
Nodes (7): Alertas, Histórico Recente, Indicadores, Objetivo, Offline e Sincronização, Prioridade da Compra Principal, Tela Inicial Operacional

### Community 72 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0022 — Unificar a gestão de categorias em uma única lista, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 73 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0023 — Priorizar compras abertas por status e data, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 74 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0028 — Usar AUTH_MOCK como bypass do Tupã para usuários locais, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 75 - "Backlog legado do Jaci"
Cohesion: 0.33
Nodes (6): Aprendizado de templates, Backlog legado do Jaci, Edição de execuções agendadas, Entregas concluídas sem identificador BL legado, Mapeamento das fontes abertas migradas, PWA, operação offline e sincronização

### Community 76 - "Edição de execuções agendadas"
Cohesion: 0.33
Nodes (5): Campos editáveis, Edição de execuções agendadas, Notificações e sincronização, Regras, Sincronização offline

### Community 77 - "SessionExpired"
Cohesion: 0.26
Nodes (6): AccessTokenExpired, Exception, SessionExpired, MockSessionProvider, ProviderUnavailable, TupaSessionProvider

### Community 78 - "FL-05 — Compra Colaborativa"
Cohesion: 0.40
Nodes (5): Atores, FL-05 — Compra Colaborativa, Fluxo Principal, Objetivo, Resultado Esperado

### Community 79 - "run"
Cohesion: 0.14
Nodes (18): Path, Executa Chromium com servidor e banco exclusivos; nunca usa servidor existente., run(), _stop(), _wait_for_server(), write_result(), publication(), fixture (+10 more)

### Community 80 - "Identificação e entrada"
Cohesion: 0.12
Nodes (17): Aceite manual — 2026-11-11, Acompanhamento até produção, Acompanhamento da implementação, BL-0019 — Manter sessão autenticada por oito horas de inatividade, Comportamento esperado, Comportamento observado, Correção durante validação — 2026-11-11, Evidência externa — 2026-11-11 (+9 more)

### Community 81 - "Refinamento — BL-0016 — Botão flutuante para adicionar itens"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Adição contextual por modal nas telas mutáveis, Excluído, Fatia 1.1.1 — Contratos TDD e fluxo modal completo online/offline (+13 more)

### Community 82 - "FL-04 — Execução da Compra"
Cohesion: 0.33
Nodes (6): Atores, Cenários Alternativos, FL-04 — Execução da Compra, Fluxo Principal, Objetivo, Resultado Esperado

### Community 83 - "utils/__init__.py"
Cohesion: 0.13
Nodes (19): invite_member(), Convida um novo membro para o grupo via magic link. Retorna dict com success,…, _build_invite_email(), _build_login_email(), _build_magic_link(), Template HTML para e-mail de convite para grupo., Monta a URL completa do magic link., Envia e-mail com magic link. Se SMTP não configurado, faz log do link (modo… (+11 more)

### Community 84 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0020 — Bloquear renomeação de item vinculado ao template, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 85 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0024 — Autocompletar nomes de itens pelo histórico do grupo, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 86 - "FL-08 — Consulta da Agenda e Histórico"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-08 — Consulta da Agenda e Histórico, Fluxo Principal, Objetivo, Resultado Esperado

### Community 87 - "session_http.py"
Cohesion: 0.13
Nodes (24): _revoke_reference(), internal_return_url(), localdatetime_filter(), format_local_datetime(), Convert UTC datetime to local timezone for display, csrf_value(), _current(), failure_response() (+16 more)

### Community 88 - "test_purchase_playwright.py"
Cohesion: 0.08
Nodes (33): browser_context_args(), only_synthetic_environment(), pinned_browser_assets(), fixture, ui_purchase(), create_local_account(), create_purchase(), password_account() (+25 more)

### Community 89 - "item-add-modal.js"
Cohesion: 0.27
Nodes (15): completeSuccess(), finishClose(), focusableElements(), formFor(), hideLocalModal(), hideModal(), initialize(), initializeModal() (+7 more)

### Community 90 - "Refinamento — BL-0017 — Nome da execução avulsa"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Nome exclusivo para compra sem lista, Excluído, Fatia 1.1.1 — Contratos TDD e implementação completa (+13 more)

### Community 91 - "auth.py"
Cohesion: 0.10
Nodes (40): confirm_logout(), handle_setup_profile(), handle_update_profile(), login_error_page(), login_page(), login_sent_page(), logout(), password_login() (+32 more)

### Community 92 - "offline_queue.test.cjs"
Cohesion: 0.19
Nodes (12): assert, browser(), fs, { IDBFactory }, path, plain(), prepared(), response() (+4 more)

### Community 93 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0016 — Disponibilizar botão flutuante para adicionar itens, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 94 - "Settings"
Cohesion: 0.10
Nodes (20): Permite autenticação em desenvolvimento servido por HTTP., Settings, create_database_engine(), Cria engine com ajustes específicos para SQLite ou PostgreSQL., BaseSettings, Engine, model_validator, create_database_if_missing() (+12 more)

### Community 95 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0017 — Permitir informar um nome para execução avulsa, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 96 - "test_item_add_fab.py"
Cohesion: 0.28
Nodes (12): Path, read(), test_both_modal_pages_load_the_local_cached_controller(), test_fab_and_modal_styles_respect_safe_areas_and_local_fallback(), test_local_modal_controller_preserves_scroll_focus_and_keyboard_behavior(), test_managed_item_modals_stay_above_backdrop_and_page_actions(), test_modal_controller_closes_only_after_online_or_offline_success(), test_modal_pages_keep_the_single_form_available_without_javascript() (+4 more)

### Community 97 - "executions.py"
Cohesion: 0.10
Nodes (53): Group, close_execution_page(), complete_item_form(), _completed_page(), create_execution_page(), edit_item_form(), execution_detail(), execution_items_fragment() (+45 more)

### Community 98 - "Refinamento — BL-0011 — Cobertura, navegador e CI"
Cohesion: 0.07
Nodes (26): Cenários TDD e contratos futuros, Encerramento da 1.4.0, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Medição Python, Etapa 2 / Ticket 2 — Navegador real, Etapa 3 / Ticket 3 — CI e evidências, Evidência da tarefa 1 — Cobertura (+18 more)

### Community 99 - "Refinamento — BL-0026 — Ferramentas e ambiente de testes"
Cohesion: 0.08
Nodes (24): Cenários TDD, Contratos futuros, Encerramento da 1.4.0, Entrega documental já autorizada, Entrega para integração, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Ambiente e autenticação de teste (+16 more)

### Community 100 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0025 — Preparar e publicar versão 1.3.0, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 101 - "ConnectionManager"
Cohesion: 0.14
Nodes (11): ConnectionManager, Any, WebSocket, Gerenciador de conexões WebSocket. Agrupa conexões por execution_id para…, Aceita a conexão e registra na sala., Remove a conexão da sala., Envia mensagem para todos na sala, exceto o remetente (se informado). Formato:…, Envia mensagem para um único cliente. (+3 more)

### Community 102 - "Execution"
Cohesion: 0.06
Nodes (77): ExecutionStatus, Execution, ExecutionItem, Calcula o valor total do item (qtd * preço unitário)., SyncConflictAudit, AddExecutionItemOperation, ConflictResolutionOperation, _execution_state() (+69 more)

### Community 103 - "test_test_environment.py"
Cohesion: 0.26
Nodes (13): process(), parametrize, Contratos BL-0026: ambiente isolado, mock e comandos públicos., setup(), test_cleanup_refuses_wrong_environment_and_preserves_unrelated_files(), test_mock_cannot_start_outside_test(), test_mock_http_authorization_and_unsupported_operations(), test_mock_login_refresh_restart_revocation_and_tamper() (+5 more)

### Community 104 - "Refinamento — BL-0009 — Criptografia em repouso — 1.5.0"
Cohesion: 0.07
Nodes (27): Aborto solicitado pelo usuário — 2026-11-10, Base de release definida pelo usuário, Cenários TDD após aprovação, Contrato funcional e interfaces, Decisões da 1.5.0, Entrega das três subtarefas — 2026-10-30, Etapa 1 / Ticket 1 — Três subtarefas sequenciais, Execução autorizada — 2026-10-30 (+19 more)

### Community 105 - "PasswordProvider"
Cohesion: 0.14
Nodes (11): api_route, PasswordProvider, Provedor de senha sintético para contratos HTTP e Chromium isolado., endpoint(), health(), outbox(), get, post (+3 more)

### Community 106 - "password_service.py"
Cohesion: 0.26
Nodes (14): _available(), change_password(), InvalidResetLink, normalize_email(), open_reset_token(), PasswordFlowError, datetime, Exception (+6 more)

### Community 107 - "Refinamento — BL-0001 — Rastreabilidade da operação offline"
Cohesion: 0.10
Nodes (20): Cenários TDD e contratos futuros, CI remoto e entrega para integração, Encerramento da 1.4.0, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Reconciliação completa, Fatia 1.1 — Contratos da implementação efetiva, Fatia 1.1 — Contratos efetivos (+12 more)

### Community 108 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0026 — Ferramentas, ambiente de testes e rastreabilidade das releases, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 109 - "test_postgresql_backup.py"
Cohesion: 0.24
Nodes (18): CompletedProcess, _backup_environment(), fake_postgres_tools(), fixture, parametrize, Path, _run_backup(), test_backup_disabled_exits_without_calling_postgres_tools() (+10 more)

### Community 110 - "package.json"
Cohesion: 0.20
Nodes (9): fake-indexeddb, devDependencies, fake-indexeddb, engines, node, name, private, scripts (+1 more)

### Community 111 - "get_settings"
Cohesion: 0.12
Nodes (38): get_settings(), lock_session(), Lock de sessão compartilhado entre workers, antes de tocar ou rotacionar., reference_hash(), _access_deadline(), access_token_for_user(), _cipher(), cookie_grant() (+30 more)

### Community 112 - "ValueError"
Cohesion: 0.28
Nodes (13): allowed_runtime(), Path, Guardas sem efeitos colaterais para os ambientes sintéticos do Jaci., validate_database(), validate_runtime(), Cache explícito de dependências visuais reais, fixadas por hash para testes UI., setup(), main() (+5 more)

### Community 113 - "migrate_sqlite_to_postgres.py"
Cohesion: 0.21
Nodes (12): load_target_database_url(), migrate_data(), normalize_postgres_target(), normalize_sqlite_source(), parse_args(), Namespace, Migra todos os dados do SQLite para PostgreSQL preservando IDs e relações., Normaliza URLs fornecidas por provedores para o driver Psycopg 3. (+4 more)

### Community 114 - "0002 - Backup automático do PostgreSQL"
Cohesion: 0.22
Nodes (8): 0002 - Backup automático do PostgreSQL, Consequências, Contexto, Decisão, Plano refinado, Progresso, Status, Validação

### Community 115 - "items/BL-0007-replicacao-externa-backups.md"
Cohesion: 0.12
Nodes (13): Ambientes, Backups de produção, Estratégia de Banco de Dados, Migração de Dados, Migrações, Agenda e logs, Backups do PostgreSQL, Configuração (+5 more)

### Community 116 - "test_coverage_runner.py"
Cohesion: 0.53
Nodes (5): Contratos BL-0011: relatórios úteis e piso de cobertura realmente aplicado., run_coverage(), test_coverage_floor_fails_a_passing_selection(), test_coverage_reports_are_created_for_selected_tests(), test_test_failure_is_not_hidden_by_coverage()

### Community 117 - "test_password_http.py"
Cohesion: 0.27
Nodes (15): csrf(), login(), request_link(), test_foreign_origin_is_refused_even_with_correct_form_token(), test_foreign_product_reset_is_refused_by_the_provider(), test_invalid_reset_and_foreign_product_never_change_password(), test_mock_exposes_unavailable_password_operation_without_network(), test_no_referrer_form_accepts_null_origin_only_with_signed_csrf() (+7 more)

### Community 118 - "Planejamento de releases após a 1.3.0"
Cohesion: 0.15
Nodes (13): Ajuste de contrato do AUTH_MOCK antes da 1.4.0, Cancelamento do escopo da 1.5.0 — 2026-11-10, Contrato de acompanhamento, Correções descobertas na validação da 1.4.0, Dependências das próximas versões, Histórico da branch de integração da 1.5.0, Organização da 1.4.0, Planejamento de releases após a 1.3.0 (+5 more)

### Community 120 - "Refinamento — BL-0007 — Cópia externa por SSH/SFTP — 1.5.0"
Cohesion: 0.12
Nodes (16): Aborto solicitado pelo usuário — 2026-11-10, Base de release definida pelo usuário, Cenários TDD após aprovação, Contrato funcional e interfaces, Decisões da 1.5.0, Entrega das três subtarefas — 2026-10-29, Etapa 1 / Ticket 1 — Três subtarefas sequenciais, Evidência e limites (+8 more)

### Community 129 - "routers/passwords.py"
Cohesion: 0.35
Nodes (15): change_password(), _context(), forgot_page(), forgot_password(), _page(), _password_success(), get, post (+7 more)

### Community 130 - "Refinamento — BL-0019 — Sessão por oito horas de inatividade — 1.5.0"
Cohesion: 0.09
Nodes (23): Autorização e atividade em HTTP, Cenários TDD do escopo, Concorrência, refresh e revogação, Contrato técnico proposto, Correção de primeiro acesso — 2026-11-11, Decisões e escopo, Diagnóstico e classificação da triagem, Estado persistido e credenciais (+15 more)

### Community 131 - "FL-09 — Operação Offline"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-09 — Operação Offline, Fluxo Principal, Objetivo, Resultado Esperado

### Community 132 - "FL-06 — Aprendizado do Template"
Cohesion: 0.33
Nodes (6): FL-06 — Aprendizado do Template, Fluxo Principal, Objetivo, Pré-condições, Resultado Esperado, Tipos de Sugestão

### Community 133 - "User"
Cohesion: 0.06
Nodes (62): get_db(), get_active_group(), get_current_user(), get_current_user_ws(), get_unread_notification_count(), Request, Session, Dependências reutilizáveis para injeção em rotas. (+54 more)

### Community 135 - "Refinamento — BL-0010 — Recuperação e troca de senha — 1.5.0"
Cohesion: 0.10
Nodes (20): Cenários TDD, Confirmação de reset e troca no perfil, Dependência publicada — 2026-11-11, Dependências e limites, Entrada do link e formulário limpo, Escopo e fluxos, Estratégia de validação, Etapa 1 / Ticket 1 — Contratos e recuperação pública (+12 more)

### Community 136 - "Refinamento da versão 1.5.0 — Acesso à conta e continuidade da sessão"
Cohesion: 0.17
Nodes (12): Atualização da dependência externa — 2026-11-11, Decisões explícitas do usuário, Dependência externa D-01 — Revogação no Tupã, Diagnóstico e fontes locais, Fechamento desta etapa documental, Ordem da versão e integração, Política comum de senha e sessão, Progresso (+4 more)

### Community 137 - "auth_service.py"
Cohesion: 0.22
Nodes (13): authenticate_with_password(), get_or_create_tupa_user(), Session, Cria a identidade no Tupã e o perfil local no Jaci., Completa os dados locais do perfil., Atualiza os dados pessoais do usuário., Associa uma identidade Tupã ao perfil local do Jaci., Autentica pelo adaptador selecionado e carrega o perfil local. (+5 more)

### Community 138 - "test_tupa_session_provider.py"
Cohesion: 0.16
Nodes (6): contract(), fixture, parametrize, signing_key(), test_malformed_active_response_never_authorizes(), test_service_credential_or_provider_failure_does_not_revoke_user()

### Community 139 - "test_password_recovery.py"
Cohesion: 0.17
Nodes (6): password_environment(), fixture, parametrize, _reply(), test_password_policy_rejects_invalid_input_without_reflection(), test_rate_window_expires_and_old_hashes_are_removed()

### Community 140 - "password_cache.test.cjs"
Cohesion: 0.17
Nodes (4): assert, fs, test, vm

### Community 141 - "FL-01 — Primeiro Acesso e Onboarding"
Cohesion: 0.40
Nodes (5): Atores, FL-01 — Primeiro Acesso e Onboarding, Fluxo Principal, Objetivo, Resultado Esperado

### Community 142 - "execution_service.py"
Cohesion: 0.15
Nodes (23): handle_update_execution(), Edita dados próprios de uma execução agendada., cancel_execution(), create_execution_from_pending(), ensure_execution_is_mutable(), generate_next_execution(), get_execution_display_name(), get_execution_items_grouped() (+15 more)

### Community 143 - "FL-03 — Geração de Execução"
Cohesion: 0.33
Nodes (6): Atores, FL-03 — Geração de Execução, Fluxo Automático, Fluxo Manual, Objetivo, Resultado Esperado

### Community 144 - "FL-10 — Home Operacional"
Cohesion: 0.40
Nodes (5): FL-10 — Home Operacional, Fluxo Principal, Objetivo, Resultado Esperado, Sessão durante a compra (BL-0019)

### Community 145 - "password_privacy.py"
Cohesion: 0.22
Nodes (8): install_password_log_filters(), PasswordLogFilter, PasswordPrivacyMiddleware, BaseHTTPMiddleware, Cabeçalhos de recuperação e remoção de queries sensíveis dos logs., _redact(), test_password_urls_are_redacted_from_access_and_client_logs(), test_uvicorn_access_formatter_preserves_status_and_removes_reset_secret()

### Community 146 - "request_recovery"
Cohesion: 0.39
Nodes (7): consume(), datetime, Session, remove_expired(), _limit_key(), Session, request_recovery()

### Community 150 - "test_session_auth_flow.py"
Cohesion: 0.23
Nodes (14): issue(), BL-0019: persistência, rotação e HTTP. Não executar sem liberação., test_access_expiring_during_validation_refreshes_once_without_ending_session(), test_cookie_reference_is_random_and_tokens_are_not_persisted_open(), test_each_request_touches_even_automatic_and_under_one_minute(), test_expired_local_session_never_refreshes_or_resurrects(), test_http_background_counts_but_expired_post_never_reaches_handler(), test_idle_is_rechecked_after_slow_refresh() (+6 more)

### Community 151 - "Provider"
Cohesion: 0.25
Nodes (4): guard(), Provider, fixture, test_real_adapter_requires_configuration_before_network()

### Community 152 - "execution_ws_handler"
Cohesion: 0.33
Nodes (6): websocket, WebSocket para sincronização em tempo real de uma execução. Autenticação por…, websocket_execution(), execution_ws_handler(), WebSocket, Gerencia a conexão WebSocket para uma execução específica. Usa cookie opaco…

### Community 153 - ".normalize_database_url"
Cohesion: 0.40
Nodes (3): Aceita nomes usuais de ambiente além de booleanos., Usa psycopg 3 para URLs PostgreSQL fornecidas por provedores., field_validator

### Community 155 - "FL-07 — Gestão de Grupos"
Cohesion: 0.40
Nodes (5): Atores, FL-07 — Gestão de Grupos, Fluxo Principal, Objetivo, Resultado Esperado

### Community 156 - "FL-02 — Criação de Template"
Cohesion: 0.40
Nodes (5): Atores, FL-02 — Criação de Template, Fluxo Principal, Objetivo, Resultado Esperado

### Community 157 - "format_local_date"
Cohesion: 0.50
Nodes (4): localdate_filter(), format_local_date(), date, Convert UTC datetime to local date only

### Community 158 - "overview.md"
Cohesion: 0.50
Nodes (3): Jaci, Operação com conexão instável, Qual problema o produto resolve?

### Community 159 - "Fluxos Principais do Usuário — Jaci"
Cohesion: 0.67
Nodes (3): Fluxos Principais do Usuário — Jaci, Objetivo, Princípios Gerais

## Knowledge Gaps
- **856 isolated node(s):** `navigationUpdate`, `ACTIVE_CACHES`, `name`, `test`, `node` (+851 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `routers/passwords.py`, `make_user`, `template_service.py`, `categories.py`, `datetime.py`, `auth_service.py`, `test_password_recovery.py`, `execution_service.py`, `sync_center`, `get_group_by_id`, `tupa_auth_service.py`, `agenda.py`, `utils/__init__.py`, `test_purchase_playwright.py`, `auth.py`, `executions.py`, `Execution`, `get_settings`, `test_password_http.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `routers/passwords.py`, `User`, `datetime.py`, `auth_service.py`, `password_service.py`, `SessionExpired`, `ValueError`, `request_recovery`, `utils/__init__.py`, `session_http.py`, `test_purchase_playwright.py`, `auth.py`, `tupa_auth_service.py`, `Settings`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `User` (e.g. with `Base` and `AddExecutionItemOperation`) actually correct?**
  _`User` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 133 inferred relationships involving `make_user()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_user()` has 133 INFERRED edges - model-reasoned connections that need verification._
- **Are the 127 inferred relationships involving `make_group()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_group()` has 127 INFERRED edges - model-reasoned connections that need verification._
- **What connects `navigationUpdate`, `ACTIVE_CACHES`, `name` to the rest of the system?**
  _856 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._